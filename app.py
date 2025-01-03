import io
from flask import Flask, request, render_template, send_file, session as flask_session, url_for, redirect, flash
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

class Users(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
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

categories=Table(
    'categories',metadata,
    Column('category_id',Integer,nullable=False,autoincrement=True),
    Column('category_name',String(100),nullable=False),
    Column('description',String(300),nullable=True)
)

class Expense(db.Model):
    __tablename__ = 'expenses'
    ExpenseID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, nullable=False)
    categoryid = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    expensedate = db.Column(db.Date, nullable=False)
    expensedesc = db.Column(db.String(500))
    receiptpath = db.Column(db.String(500))
    expensetime = db.Column(db.Time, nullable=False)

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    Goal_id = db.Column(db.Integer, primary_key=True)
    Target_amount = db.Column(db.Float, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    Goal_status = db.Column(db.Enum('On-going', 'Completed', 'Cancelled'), default='On-going')
    Goal_description = db.Column(db.Text, nullable=True)
    Achieved_amount = db.Column(db.Float, nullable=True)
    Goal_type = db.Column(db.Enum('Personal', 'Family'), default='Personal')
    User_id = db.Column(db.String(100), nullable=True)
    family_head_id = db.Column(db.String(100), nullable=True)

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
        user = Users.query.filter_by(email=email).first()

        user_id = user_login(email, password)
        user = Users.query.filter_by(email=email).first()

        if user_id:  # If user_id is returned, login is successful
            flask_session['user_id'] =user.user_id  # Store user_id in session
            flask_session['role']=user.role
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
    with engine.connect() as conn:
        result = conn.execute(select(categories)).fetchall()
    print(result)
    return render_template('add_expenses.html',categories=result)

@app.route('/show_expenses', methods=['GET'])
def show_expenses():
    """Display all expenses."""
    selected_month = request.args.get('month')  # Get selected month from query params
    selected_category = request.args.get('category')
    with engine.connect() as conn:
        categories_result = conn.execute(select(categories.c.category_id, categories.c.category_name)).fetchall()
        # Base query to fetch all expenses
        query = select(
            expenses.c.ExpenseID,
            expenses.c.UserID,
            expenses.c.categoryid,
            expenses.c.amount,
            expenses.c.expensedate,
            expenses.c.expensedesc,
            expenses.c.receiptpath,
            expenses.c.expensetime,
            categories.c.category_name  # Select category name
        ).select_from(expenses.join(categories, expenses.c.categoryid == categories.c.category_id))

        # Apply month filter if selected
        if selected_month:
            query = query.where(expenses.c.expensedate.like(f"{selected_month}-%"))
        if selected_category:
            query = query.where(categories.c.category_name == selected_category)

        result = conn.execute(query).fetchall()
        
        # Fetch distinct months for dropdown
        months_query = conn.execute(select(expenses.c.expensedate.distinct())).fetchall()
        months = sorted(set(expensedate.strftime('%Y-%m') for expensedate, in months_query))

    return render_template('show_expenses.html', expenses=result, months=months, selected_month=selected_month, selected_category=selected_category, categories=categories_result)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle expense submission."""
    try:
        # Get required fields
        category = request.form.get('category')  # Use .get() to safely retrieve form data
        amount = int(request.form.get('amount'))
        date = request.form.get('date')
        time = request.form.get('time')
        print(category,amount,date,time)
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
        # flash('New expense added successfully','info')

        # Redirect to the expenses page
        return redirect(url_for('index'))

    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/edit_expenses/<int:ExpenseID>',methods=['GET','POST'])
def edit(ExpenseID):
    with engine.connect() as conn:
        updating_expense = conn.execute(select(expenses).where(expenses.c.ExpenseID==ExpenseID)).fetchone()
        category = conn.execute(select(categories)).fetchall()
    #print(updating_expense)
    #print(categories)
        if request.method == 'POST':
            try:
                # Get updated data from the form
                cat = request.form.get('category')
                amount = int(request.form.get('amount'))
                date = request.form.get('date')
                time = request.form.get('time')
                print(cat,amount,date,time)
                # Validate the data
                if not cat or not amount or not date or not time:
                    flash("Error: Missing required fields!", 'danger')
                    return redirect(request.url)

                # Validate the date and time
                submitted_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                current_datetime = datetime.now()
                if submitted_datetime > current_datetime:
                    flash("Error: Date and time cannot be in the future!", 'danger')
                    return redirect(request.url)

                # Optional fields
                description = request.form.get('description', 'No description provided')
                receipt = request.files.get('receipt')

                # Save the uploaded file if provided
                receipt_path = None
                if receipt and receipt.filename:
                    receipt_path = os.path.join(app.config['UPLOAD_FOLDER'], receipt.filename)
                    receipt.save(receipt_path)
                else:
                    receipt_path = 'No file uploaded'
                # Update the expense in the database
                conn.execute(
                    expenses.update()
                    .where(expenses.c.ExpenseID == ExpenseID)
                    .values(
                        categoryid=cat,
                        amount=amount,
                        expensedate=date,
                        expensetime=time,
                        expensedesc=description,
                        receiptpath=receipt_path,
                    )
                )
                conn.commit()

                # flash("Expense updated successfully!", 'success')
                return redirect(url_for('index'))

            except Exception as e:
                flash(f"Error updating expense: {str(e)}", 'danger')
                return redirect(request.url)
        # Render the edit form with current expense data and category list
    return render_template('edit_expenses.html',expense=updating_expense,categories=category)

@app.route('/add_amount_to_expenses', methods=['POST'])
def add_amount_to_expenses():
    """Handle adding amount to an expense."""
    try:
        data = request.get_json()
        ExpenseID = data['ExpenseID']
        added_amount = float(data['addedAmount'])

        with engine.connect() as conn:
            # Fetch current amount
            current_expense = conn.execute(select(expenses).where(expenses.c.ExpenseID == ExpenseID)).fetchone()
            if not current_expense:
                return {"error": "Expense not found"}, 404

            new_amount = current_expense.amount + added_amount

            # Update the amount
            conn.execute(
                expenses.update()
                .where(expenses.c.ExpenseID == ExpenseID)
                .values(amount=new_amount)
            )
            conn.commit()

        return {"message": "Amount added successfully!"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
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
    return render_template('addBudget.html')

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
    
@app.route('/Budget',methods=['PUT'])
def update_budget():
    data=request.get_json()
    try:
        budget = db.session.query(Budget).filter_by(budget_id=data['budget_id']).first()
        budget.limit = data['limit']
        budget.start_date = data['start_date']
        budget.end_date = data['end_date']
        db.session.commit()
        flash("Budget updated successfully")
        return jsonify({"message":1}),200
    except Exception as e:
        print(str(e))
        return jsonify({"message":0}),400

@app.route('/Alerts',methods=["GET"])
def get_alerts():
    alerts=db.session.query(Alert)
    alert=[]
    for i in alerts:
        alert.append([i.alert_id,i.alert_date,i.alert_message,i.alert_type,i.budget_id,i.is_resolved])
    return jsonify({"alerts":alerts}),200

#MODULE 5 
@app.route('/mod5sprint2')
def mod5sprint2():
    return render_template('sprint2mod5.html')

def get_user_data(query, user_id=None, is_family_head=False):
    if is_family_head:
        return query.all()
    else:
        return query.filter_by(user_id=user_id).all()

def fetch_budgets():
    user_id = flask_session.get('user_id')  # Retrieving user_id from session
    budgets = Budget.query.filter_by(user_id=user_id).all()
    data = [
        {
            'budget_id': b.budget_id,
            'category_id': b.category_id,
            'user_id': b.user_id,
            'limit': float(b.limit),
            'start_date': b.start_date,
            'end_date': b.end_date,
        }
        for b in budgets
    ]
    return pd.DataFrame(data)

def fetch_expenses(start_date=None, end_date=None, category=None):
    user_id = flask_session.get('user_id')
    query = Expense.query.filter_by(UserID=user_id)

    if start_date:
        query = query.filter(Expense.expensedate >= start_date)
    if end_date:
        query = query.filter(Expense.expensedate <= end_date)
    if category:
        query = query.filter(Expense.categoryid == category)
    
    expenses = query.all()
    data = [
        {
            'ExpenseID': e.ExpenseID,
            'UserID': e.UserID,
            'categoryid': e.categoryid,
            'amount': e.amount,
            'expensedate': e.expensedate,
            'expensedesc': e.expensedesc,
            'receiptpath': e.receiptpath,
            'expensetime': e.expensetime
        }
        for e in expenses
    ]
    return pd.DataFrame(data)

def fetch_savings_goals():
    user_id=flask_session.get('user_id')
    goals = SavingsGoal.query.filter_by(User_id=user_id).all()
    data = [
        {
            'Goal_id': g.Goal_id,
            'Target_amount': g.Target_amount,
            'start_date': g.start_date,
            'end_date': g.end_date,
            'Goal_status': g.Goal_status,
            'Goal_description': g.Goal_description,
            'Achieved_amount': g.Achieved_amount,
            'Goal_type': g.Goal_type,
            'User_id': g.User_id,
            'family_head_id': g.family_head_id
        }
        for g in goals
    ]
    return pd.DataFrame(data)

@app.route('/budget')
def budget():
    # Get the user role and user ID from the session
    role = flask_session.get('role')
    user_id = flask_session.get('user_id')
    
    # Fetch budget data
    budgets = fetch_budgets()
    filtered_budgets=''

    if role == 'FamilyHead':
        # If the user is a FamilyHead, show all data
        filtered_budgets = budgets
    else:
        # If the user is a regular user, show only their personal data
        filtered_budgets = budgets[budgets['user_id'] == user_id]
        print(filtered_budgets)

    categories = filtered_budgets['category_id'].unique()
    return render_template('trail2.html', categories=categories, budgets=filtered_budgets)


@app.route('/savings')
def savings():
    # Get the user role and user ID from the session
    role = flask_session.get('role')
    user_id = flask_session.get('user_id')

    # Fetch savings goal data
    savings_goals = fetch_savings_goals()

    if role == 'FamilyHead':
        # If the user is a FamilyHead, show all data
        filtered_savings = savings_goals
    else:
        # If the user is a regular user, show only their personal data
        filtered_savings = savings_goals[savings_goals['User_id'] == user_id]

    statuses = filtered_savings['Goal_status'].unique()
    return render_template('trial2save.html', statuses=statuses, savings_goals=filtered_savings)

@app.route('/filter_expenses', methods=['POST'])
def filter_expenses():
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    category = filters.get('category')

    df = fetch_expenses(start_date=start_date, end_date=end_date, category=category)
    return jsonify(df.to_dict(orient='records'))

@app.route('/export_expenses_csv', methods=['POST'])
def export_expenses_csv():
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    category = filters.get('category')

    df = fetch_expenses(start_date=start_date, end_date=end_date, category=category)
    file_path = 'data/filtered_expenses.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)


@app.route('/expense')
def expense():
    # Get the user role and user ID from the session
    role = flask_session.get('role')
    user_id = flask_session.get('user_id')

    # Fetch expense data
    expenses = fetch_expenses()

    if role == 'FamilyHead':
        # If the user is a FamilyHead, show all data
        filtered_expenses = expenses
    else:
        # If the user is a regular user, show only their personal data
        filtered_expenses = expenses[expenses['UserID'] == user_id]

    categories = filtered_expenses['categoryid'].unique()
    return render_template('expenses.html', categories=categories, expenses=filtered_expenses)

# Route to generate and send plots
@app.route('/generate_plot', methods=['POST'])
def generate_plot():
    plot_type = request.json['plot_type']
    
    role = flask_session.get('role')
    user_id = flask_session.get('user_id')
    
    # Fetch budget data
    budgets = fetch_budgets()
    df=''

    if role == 'FamilyHead':
        # If the user is a FamilyHead, show all data
        df = budgets
    else:
        # If the user is a regular user, show only their personal data
        df = budgets[budgets['user_id'] == user_id]
        

    # Pie Chart: Budget distribution by category
    if plot_type == 'pie':
        category_sums = df.groupby('category_id')['limit'].sum()
        plt.figure(figsize=(8, 6))
        category_sums.plot.pie(autopct='%1.1f%%', startangle=90, cmap='tab20', ylabel='')
        plt.title('Budget Distribution by Category')
    
    # Bar Chart: Budget limit comparison by category
    elif plot_type == 'bar':
        category_sums = df.groupby('category_id')['limit'].sum()
        plt.figure(figsize=(8, 6))
        category_sums.plot.bar(color='skyblue', edgecolor='black')
        plt.title('Budget Limit by Category')
        plt.xlabel('Category ID')
        plt.ylabel('Limit')

    # Line Chart: Budget limits over time
    elif plot_type == 'line':
    # Ensure dates are parsed and sorted
        df['start_date'] = pd.to_datetime(df['start_date'])
        df.sort_values('start_date', inplace=True)



    # Group by 'start_date' and 'category_id', summing 'limit'
        grouped = df.groupby(['start_date', 'category_id'])['limit'].sum().reset_index()

    # Plot each category's data
        plt.figure(figsize=(10, 6))
        for category in grouped['category_id'].unique():
            category_data = grouped[grouped['category_id'] == category]
            plt.plot(
                category_data['start_date'], 
                category_data['limit'], 
                marker='o', 
                label=f'Category {category}'
            )

        plt.title('Budget Limits Over Time')
        plt.xlabel('Start Date')
        plt.ylabel('Limit')
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Save plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/consolidated')
def download_consolidated():
    # Fetch data
    budget_df = fetch_budgets()
    expense_df = fetch_expenses()
    savings_df = fetch_savings_goals()

    # File path for consolidated CSV
    file_path = 'data/consolidated_report.csv'
    os.makedirs('data', exist_ok=True)

    with open(file_path, 'w', newline='') as f:
        f.write("Budgets\n")
        budget_df.to_csv(f, index=False)
        f.write("\n")  

        f.write("Expenses\n")
        expense_df.to_csv(f, index=False)
        f.write("\n")  

        f.write("Savings Goals\n")
        savings_df.to_csv(f, index=False)
        f.write("\n")

    return send_file(file_path, as_attachment=True)

# Route to download CSV
@app.route('/download_csv')
def download_csv():
    df = fetch_budgets()
    file_path = 'data/budgets.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)


# Route to generate and send plots
@app.route('/generate_expense_plot', methods=['POST'])
def generate_expense_plot():
    plot_type = request.json['plot_type']
    

    role = flask_session.get('role')
    user_id = flask_session.get('user_id')
    print("Expenses User id",user_id)
    # Fetch expense data
    expenses = fetch_expenses()
    df=''

    if role == 'FamilyHead':
        # If the user is a FamilyHead, show all data
        df = expenses
    else:
        # If the user is a regular user, show only their personal data
        df = expenses[expenses['UserID'] == user_id]

    # Pie Chart: Expense distribution by category
    if plot_type == 'pie':
        category_sums = df.groupby('categoryid')['amount'].sum()
        plt.figure(figsize=(8, 6))
        category_sums.plot.pie(autopct='%1.1f%%', startangle=90, cmap='tab20', ylabel='')
        plt.title('Expense Distribution by Category')
    
    # Bar Chart: Expense amounts by category
    elif plot_type == 'bar':
        category_sums = df.groupby('categoryid')['amount'].sum()
        plt.figure(figsize=(8, 6))
        category_sums.plot.bar(color='lightcoral', edgecolor='black')
        plt.title('Expense Amounts by Category')
        plt.xlabel('Category ID')
        plt.ylabel('Amount')

    # Line Chart: Expense trends over time
    elif plot_type == 'line':
        df['expensedate'] = pd.to_datetime(df['expensedate'])
        df.sort_values('expensedate', inplace=True)

        grouped = df.groupby(['expensedate', 'categoryid'])['amount'].sum().reset_index()

        plt.figure(figsize=(10, 6))
        for category in grouped['categoryid'].unique():
            category_data = grouped[grouped['categoryid'] == category]
            plt.plot(
                category_data['expensedate'], 
                category_data['amount'], 
                marker='o', 
                label=f'Category {category}'
            )

        plt.title('Expense Trends Over Time')
        plt.xlabel('Expense Date')
        plt.ylabel('Amount')
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Save plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')

# Route to download CSV
@app.route('/download_expenses_csv')
def download_expenses_csv():
    df = fetch_expenses()
    file_path = 'data/expenses.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)




# Route to generate and send plots
@app.route('/generate_savings_plot', methods=['POST'])
def generate_savings_plot():
    plot_type = request.json['plot_type']
    df = fetch_savings_goals()

    # Pie Chart: Distribution of goals by status
    if plot_type == 'pie':
        status_counts = df['Goal_status'].value_counts()
        plt.figure(figsize=(8, 6))
        status_counts.plot.pie(autopct='%1.1f%%', startangle=90, cmap='tab20', ylabel='')
        plt.title('Distribution of Goals by Status')

    # Bar Chart: Target vs. Achieved amounts
    elif plot_type == 'bar':
        plt.figure(figsize=(10, 6))
        df.set_index('Goal_id')[['Target_amount', 'Achieved_amount']].plot.bar(color=['steelblue', 'coral'], edgecolor='black')
        plt.title('Target vs. Achieved Amounts for Each Goal')
        plt.xlabel('Goal ID')
        plt.ylabel('Amount')
        plt.legend(['Target Amount', 'Achieved Amount'])

    # Line Chart: Cumulative achieved amounts over time
    elif plot_type == 'line':
        df['start_date'] = pd.to_datetime(df['start_date'])
        df.sort_values('start_date', inplace=True)
        df['Cumulative_Achieved'] = df['Achieved_amount'].cumsum()

        plt.figure(figsize=(10, 6))
        plt.plot(df['start_date'], df['Cumulative_Achieved'], marker='o', color='green')
        plt.title('Cumulative Achieved Amount Over Time')
        plt.xlabel('Start Date')
        plt.ylabel('Cumulative Achieved Amount')
        plt.grid(True, linestyle='--', linewidth=0.5)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')
# Route to download CSV
@app.route('/download_savings_csv')
def download_savings_csv():
    df = fetch_savings_goals()
    file_path = 'data/savings_goals.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
