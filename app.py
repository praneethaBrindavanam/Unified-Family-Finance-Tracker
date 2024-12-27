from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import secrets
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import jsonify,request
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Time, TIMESTAMP,func 
from sqlalchemy.sql import select
from models import db,Budget,Alert
import matplotlib.pyplot as plt
import os
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Recipt_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# SQLAlchemy Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/unified_family'
#change the password and databasename as per your system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)
DATABASE_URI = 'mysql+pymysql://root:1234@localhost/unified_family'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

db = SQLAlchemy(app)


class Budget(db.Model):
    __tablename__="budgets"
    budget_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    category_id=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,nullable=False)
    limit=db.Column(db.DECIMAL)
    start_date=db.Column(db.Date)
    end_date=db.Column(db.Date)

class AlertType(enum.Enum):
    WARNING = 'Warning'
    CRITICAL = 'Critical'

class Alert(db.Model):
    __tablename__ = "alert"
    alert_id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, nullable=False)
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    alert_message = db.Column(db.String(255), nullable=False)
    alert_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)

users = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('email', String(255), unique=True, nullable=False),
    Column('password_hash', String(255), nullable=False),
    Column('phone_number', String(20), nullable=True),
    Column('role', String(50), nullable=False),
    Column('created_at', TIMESTAMP, nullable=False, server_default=func.now())
)
expenses = Table(
    'expenses', metadata,
    Column('ExpenseID', Integer, primary_key=True, autoincrement=True),
    Column('UserID', Integer, nullable=False),
    Column('categoryid', String(50), nullable=False),
    Column('amount', Integer, nullable=False),
    Column('expensedate', Date, nullable=False),
    Column('expensedesc', String(500)),
    Column('receiptpath', String(500)),
    Column('expensetime', Time, nullable=False)
)
metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def insert_expense(category, amount, expense_date, description, receipt_path, expense_time):
    """Insert a new expense into the database."""
    with engine.connect() as conn:
        conn.execute(expenses.insert().values(
            UserID=1001,  # Hardcoded for demonstration
            categoryid=category,
            amount=amount,
            expensedate=expense_date,
            expensedesc=description,
            receiptpath=receipt_path,
            expensetime=expense_time
        ))
        conn.commit()

def add_user_with_verification(name, email, password, phone_number, role):
    try:
        # Hash the password using scrypt
        hashed_password = generate_password_hash(password, method='scrypt')
        print(f"Adding user with email: {email}, hashed password: {hashed_password}")
        session.execute(
            users.insert().values(
                name=name,
                email=email,
                password_hash=hashed_password,
                phone_number=phone_number,
                role=role
            )
        )
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        return False


# Verify user login
def user_login(email, password):
    stmt = select(users).where(users.c.email == email)
    result = session.execute(stmt).fetchone()
    if result and check_password_hash(result.password_hash, password):
        return result.user_id
    return False    


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # Get form data (ensure you have the correct field names)
            name = request.json.get('name')
            email = request.json.get('email')
            password = request.json.get('password')
            phone_number = request.json.get('phone')
            role = request.json.get('role', 'users')  # Default to 'user'
            print(f"Received: Name={name}, Email={email}, Role={role}")
            if name and email and password:
                # Call the function to add user to database
                if add_user_with_verification(name, email, password, phone_number, role):
                    return {"success": True, "message": "Signup successful!"}, 200
                else:
                    return {"success": False, "message": "Database error."}, 400
            else:
                return {"success": False, "message": "All fields are required."}, 400
        except Exception as e:
            print(f"Error in signup: {e}")
            return {"success": False, "message": "An error occurred."}, 500
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_id = user_login(email, password)
        if user_id:  # If user_id is returned, login is successful
            #session['user_id'] = user_id  # Store user_id in session
            return redirect(url_for('navigationbar'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')

@app.route('/navigationbar')
def navigationbar():
    return render_template('navigationbar.html', title="Dashboard")

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/verification', methods=['GET', 'POST'])
def verification():
    return render_template('verification.html')

@app.route('/add_expenses', methods=['GET'])
def form():
    """Render the expense form."""
    return render_template('add_expenses.html')

@app.route('/show_expenses', methods=['GET'])
def show_expenses():
    """Display all expenses."""
    with engine.connect() as conn:
        result = conn.execute(select(expenses)).fetchall()
    return render_template('show_expenses.html', expenses=result)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle expense submission."""
    try:
        # Get required fields
        category = request.form.get('category')  # Use .get() to safely retrieve form data
        amount = int(request.form.get('amount'))
        date = request.form.get('date')
        time = request.form.get('time')

        # Validate that we got all required fields
        if not category or not amount or not date or not time:
            return "<h1>Error: Missing required fields!</h1>", 400

        # Validate date and time
        submitted_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        current_datetime = datetime.now()
        if submitted_datetime > current_datetime:
            return "<h1>Error: Date and time cannot be in the future!</h1>", 400

        # Get optional fields
        description = request.form.get('description', 'No description provided')
        receipt = request.files.get('receipt')

        # Save the uploaded file if provided
        receipt_path = None
        if receipt and receipt.filename:
            receipt_path = os.path.join(app.config['UPLOAD_FOLDER'], receipt.filename)
            receipt.save(receipt_path)
        else:
            receipt_path = 'No file uploaded'

        # Insert data into the database
        insert_expense(category, amount, date, description, receipt_path, time)

        # Redirect to the expenses page
        return redirect(url_for('show_expenses'))

    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/saving_goals')
def saving_goals():
    #Hardcoded to 1 because session management is not done yet
    user_id = 1 #session.get('user_id')
    family_head_id = 1 #session.get('family_head_id')

    sql = text("""
        SELECT * FROM savings_goals
        WHERE 
            (Goal_type = 'Personal' AND User_id = :user_id)
            OR
            (Goal_type = 'Family' AND family_head_id = :family_head_id)
    """)
    savings_goals = db.session.execute(sql, {"user_id": user_id, "family_head_id": family_head_id}).fetchall()

    return render_template("saving_goals.html", datas=savings_goals)


@app.route("/add_amount/<string:id>", methods=["GET", "POST"])
def add_amount(id):
    #Hardcoded to 1 because session management is not done yet
    user_id = 1 #session.get("user_id")
    family_head_id =1 #session.get("family_head_id")

    sql = text("""
        SELECT * FROM savings_goals 
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()

    if not goal:
        flash("Goal not found")
        return redirect(url_for("saving_goals"))

    if request.method == "POST":
        additional_amount = float(request.form["additional_amount"])

        # Update achieved_amount
        update_sql = text("""
            UPDATE savings_goals 
            SET achieved_amount = COALESCE(achieved_amount, 0) + :amount
            WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
        """)
        db.session.execute(update_sql, {
            "amount": additional_amount,
            "goal_id": id,
            "user_id": user_id,
            "family_head_id": family_head_id
        })

        # Update goal status
        goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()
        achieved_amount = goal._mapping["Achieved_amount"]
        target_amount = goal._mapping["Target_amount"]

        status = "completed" if achieved_amount >= target_amount else "on-going"
        status_sql = text("""
            UPDATE savings_goals 
            SET Goal_status = :status
            WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
        """)
        db.session.execute(status_sql, {"status": status, "goal_id": id, "user_id": user_id, "family_head_id": family_head_id})
        db.session.commit()

        flash("Amount Added Successfully!")
        return redirect(url_for("saving_goals"))

    return render_template("add_amount.html", data=goal)


@app.route("/addgoal", methods=['GET', 'POST'])
def add_Goal():
    #Hardcoded to 1 because session management is not done yet
    family_head_id = 1 #session.get('family_head_id')
    user_id = 1 #session.get('user_id')

    if request.method == "POST":
        target_amount = request.form['target_amount']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        goal_status = request.form['goal_status']
        goal_description = request.form['goal_description']
        achieved_amount = request.form['achieved_amount']
        goal_type = request.form['goal_type']

        sql = text("""
            INSERT INTO savings_goals 
            (User_id, family_head_id, Target_amount, start_date, end_date, Goal_status, Goal_description, Achieved_amount, Goal_type)
            VALUES (:user_id, :family_head_id, :target_amount, :start_date, :end_date, :goal_status, :goal_description, :achieved_amount, :goal_type)
        """)
        db.session.execute(sql, {
            "user_id": user_id,
            "family_head_id": family_head_id,
            "target_amount": target_amount,
            "start_date": start_date,
            "end_date": end_date,
            "goal_status": goal_status,
            "goal_description": goal_description,
            "achieved_amount": achieved_amount,
            "goal_type": goal_type
        })
        db.session.commit()

        flash("Goal Added Successfully")
        return redirect(url_for('saving_goals'))

    return render_template("addgoals.html")


@app.route("/edit_Goals/<string:id>", methods=['GET', 'POST'])
def edit_Goals(id):
    #Hardcoded to 1 because session management is not done yet
    user_id = 1 #session.get('user_id')

    if request.method == 'POST':
        target_amount = request.form['target_amount']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        goal_status = request.form['goal_status']
        goal_description = request.form['goal_description']
        achieved_amount = request.form['achieved_amount']
        goal_type = request.form['goal_type']

        sql = text("""
            UPDATE savings_goals 
            SET Target_amount = :target_amount, start_date = :start_date, end_date = :end_date, 
                Goal_status = :goal_status, Goal_description = :goal_description, 
                Achieved_amount = :achieved_amount, Goal_type = :goal_type
            WHERE Goal_id = :goal_id AND User_id = :user_id
        """)
        db.session.execute(sql, {
            "target_amount": target_amount,
            "start_date": start_date,
            "end_date": end_date,
            "goal_status": goal_status,
            "goal_description": goal_description,
            "achieved_amount": achieved_amount,
            "goal_type": goal_type,
            "goal_id": id,
            "user_id": user_id
        })
        db.session.commit()

        flash("Goal Updated Successfully")
        return redirect(url_for("saving_goals"))

    sql = text("SELECT * FROM savings_goals WHERE Goal_id = :goal_id")
    goal = db.session.execute(sql, {"goal_id": id}).fetchone()

    return render_template("editgoals.html", datas=goal)


@app.route("/delete_Goals/<string:id>", methods=['GET', 'POST'])
def delete_Goals(id):
    #Hardcoded to 1 because session management is not done yet
    user_id =1 #session.get('user_id')

    sql = text("DELETE FROM savings_goals WHERE Goal_id = :goal_id AND User_id = :user_id")
    db.session.execute(sql, {"goal_id": id, "user_id": user_id})
    db.session.commit()

    flash('Goal Deleted Successfully')
    return redirect(url_for("saving_goals"))


@app.route('/budgethome')
def budgethome():
    return render_template('index.html')


@app.route('/addBudget')
def bud():
    return render_template('Budget.html')

@app.route('/viewAlerts')
def ale():
    with db.engine.connect() as conn:
        alerts=conn.execute(text("select * from alert"))
        alerts=[[a.alert_id,a.budget_id,a.alert_type,a.alert_message,a.alert_date,a.is_resolved] for a in alerts]
        return render_template('Alerts.html',alerts=alerts)

@app.route('/Budget',methods=['GET'])
def getall_budget():
    budgets=db.session.query(Budget).all()
    budgets=[[budget.budget_id,budget.category_id,budget.limit,budget.start_date,budget.end_date,budget.user_id] for budget in budgets]
    return render_template('viewBudget.html',budgets=budgets)

@app.route('/Budget',methods=['POST'])
def add_budget():
    data=request.get_json()
    budget=Budget(category_id=data['category_id'],user_id=data['user_id'],limit=data['limit'],start_date=data['start_date'],end_date=data['end_date'])
    db.session.add(budget)
    db.session.commit()
    return jsonify({"message":"Budget created successfully"}),201

@app.route('/Budget',methods=['DELETE'])
def delete_budget():
    data=request.get_json()
    try:
        budget=db.session.query(Budget).filter_by(budget_id=data['budget_id']).first()
        db.session.delete(budget)
        db.session.commit()
        return jsonify({"message":f"Budget with id:-{data['budget_id']} is deleted"})
    except:
        return jsonify({"message":"No id with such budget"}),404

@app.route('/Alerts',methods=["GET"])
def get_alerts():
    alerts=db.session.query(Alert)
    alert=[]
    for i in alerts:
        alert.append([i.alert_id,i.alert_date,i.alert_message,i.alert_type,i.budget_id,i.is_resolved])
    return jsonify({"alerts":alerts}),200


GRAPH_DIR = "static/images"
DOWNLOAD_DIR = "static/downloads"
os.makedirs(GRAPH_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Route for budget visualization
@app.route('/organize')
def budget_visualization():
    # Query budget data
    budgets = Budget.query.all()
    df = pd.DataFrame([{ 'category_id': b.category_id, 'limit': b.limit } for b in budgets])

    # Generate and save the graph
    graph_path = os.path.join(GRAPH_DIR, 'budget_graph.png')
    plt.figure(figsize=(10, 6))
    plt.plot(df['category_id'], df['limit'], marker='o', color='blue', label='Budget Limit')
    plt.title('Budget Graph')
    plt.xlabel('Category ID')
    plt.ylabel('Budget Limit')
    plt.legend()
    plt.grid()
    plt.savefig(graph_path)
    plt.close()

    # Generate and save the CSV
    csv_path = os.path.join(DOWNLOAD_DIR, 'budget_data.csv')
    df.to_csv(csv_path, index=False)

    return render_template('indexreport.html', graph_url=url_for('static', filename='images/budget_graph.png'), csv_url=url_for('static', filename='downloads/budget_data.csv'))

# Route for expenses visualization
@app.route('/expenses')
def expenses_visualization():
    # Query expense data
    expenses = expenses.query.all()
    df = pd.DataFrame([{ 'categoryid': e.categoryid, 'amount': e.amount } for e in expenses])

    # Generate and save the graph
    graph_path = os.path.join(GRAPH_DIR, 'expenses_graph.png')
    plt.figure(figsize=(10, 6))
    plt.plot(df['categoryid'], df['amount'], marker='o', color='blue', label='Expense Limit')
    plt.title('Expenses Graph')
    plt.xlabel('Category ID')
    plt.ylabel('Amount')
    plt.legend()
    plt.grid()
    plt.savefig(graph_path)
    plt.close()

    # Generate and save the CSV
    csv_path = os.path.join(DOWNLOAD_DIR, 'expense_data.csv')
    df.to_csv(csv_path, index=False)

    return render_template('indexreport.html', graph_url=url_for('static', filename='images/expenses_graph.png'), csv_url=url_for('static', filename='downloads/expense_data.csv'))


if __name__ == '__main__':
    app.run(debug=True)
