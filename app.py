import io
from flask import Flask, request, render_template, send_file, url_for, redirect, flash , send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import column, text
import secrets
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from datetime import timedelta
from flask import session
from flask import jsonify,request
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Time, TIMESTAMP,func 
from sqlalchemy.sql import select
from models import db,Budget,Alert
import matplotlib.pyplot as plt
import os
import pandas as pd
from flask import session as flask_session
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Recipt_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# SQLAlchemy Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/recent'

#change the password and databasename as per your system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)
DATABASE_URI = 'mysql+pymysql://root:root@localhost/recent'
engine = create_engine(DATABASE_URI)
metadata = MetaData()

db = SQLAlchemy(app)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    fam_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    fam_code = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False) 


class Budget(db.Model):
    __tablename__="budgets"
    budget_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    category_id=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,nullable=False)
    limit=db.Column(db.DECIMAL)
    start_date=db.Column(db.Date)
    end_date=db.Column(db.Date)

class AlertType(enum.Enum):
    Warning = 'Warning'
    Critical = 'Critical'

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
    Column('created_at', TIMESTAMP, nullable=False, server_default=func.now()),  
    Column('family_head_id', Integer, nullable=False)  ,
    Column('role', String(50), nullable=False)
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
    family_head_id = Column(Integer , nullable = False )
    
    
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
    Column('description',String(300),nullable=True),
    Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False)  # Foreign key to 'users' table
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

class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # Establish a relationship with the 'User' model (optional, if you want to reference user data directly)
    user = relationship('Users', backref='categories', lazy=True)

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    Goal_id = db.Column(db.Integer, primary_key=True)
    Target_amount = db.Column(db.Float, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    Goal_status = db.Column(db.Enum('On-going', 'Completed', 'Cancelled','Not Achieved','Active'), default='On-going')
    Goal_description = db.Column(db.Text, nullable=True)
    Achieved_amount = db.Column(db.Float, nullable=True)
    Goal_type = db.Column(db.Enum('Personal', 'Family'), default='Personal')
    User_id = db.Column(db.String(100), nullable=True)
    family_head_id = db.Column(db.String(100), nullable=True)
    priority = db.Column(db.Integer, nullable=False)

class Investments(db.Model):
    _tablename_ = 'investments'
    investment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_id = db.Column(db.String(100), nullable=True)
    investment_type = db.Column(db.String(50), nullable=False)
    investment_name = db.Column(db.String(255), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    purchase_price = db.Column(db.DECIMAL(15, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    roi = db.Column(db.DECIMAL(5, 2),nullable=True)
    info = db.Column(db.Text,nullable=True)
    current_value = db.Column(db.DECIMAL(15, 2),nullable=True)
    end_date = db.Column(db.Date,nullable=True)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def insert_expense(user_id, category, amount, expense_date, description, receipt_path, expense_time):
    """Insert a new expense into the database."""
    with engine.connect() as conn:
        conn.execute(expenses.insert().values(
            UserID=user_id,
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
@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/add', methods=["POST"])
def add_profile():
    """Handle form submission to add a new profile."""
    id=request.form.get("id")
    username = request.form.get("username")
    email = request.form.get("email")
    fam_name = request.form.get("fam_name")
    role = request.form.get("role")
    fam_code = request.form.get("fam_code")
    password=request.form.get("password")

    # Validation: Ensure all fields are filled
    if not all([username, email, fam_name, role, fam_code]):
        return "All fields are required!", 400

    # Create a new profile
    new_profile = Profile(
        id=id,
        username=username,
        email=email,
        fam_name=fam_name,
        role=role,
        fam_code=fam_code,
        password=password
    )

    try:
        db.session.add(new_profile)
        db.session.commit()
        return redirect('/index.html')
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500

@app.route('/delete/<int:id>')
def delete_profile(id):
    """Delete a profile by ID."""
    profile = Profile.query.get(id)
    if not profile:
        return "Profile not found!", 404

    try:
        db.session.delete(profile)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {e}", 500
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Extract form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch the user from the database
        user = Profile.query.filter_by(email=email).first()

        if user and user.password == password:  # Replace with hash comparison in production
            # Login successful: Set session variables
            session['email'] = user.email
            session['password'] = user.password
            flash("Login successful!", "success")
            # Redirect to home or dashboard
            return render_template('dashboard.html')
        else:
            # Show an error message
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('login.html')

    # Render the login.html page on GET request
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
    user_id = flask_session.get('user_id')
    print(user_id)

    with engine.connect() as conn:
        # Fetch categories for the specific user (excluding predefined ones)
        user_categories = conn.execute(
            select(categories).where(categories.c.user_id == user_id)
        ).fetchall()

        # Fetch predefined categories for user_id = 1 (default categories)
        predefined_categories = conn.execute(
            select(categories).where(categories.c.user_id == 0)
        ).fetchall()

    # Count how many categories the user has
    user_categories_count = len(user_categories)
    max_categories_limit = 5

    # Convert query results to dictionaries for easier access in the template
    user_categories_list = [{"category_id": row[0], "category_name": row[1]} for row in user_categories]
    predefined_categories_list = [{"category_id": row[0], "category_name": row[1]} for row in predefined_categories]

    # Filter out predefined categories that already exist in user categories
    predefined_categories_filtered = [
        category for category in predefined_categories_list 
        if category["category_id"] not in [cat["category_id"] for cat in user_categories_list]
    ]
    print(user_categories_list)
    # Return template with formatted category data
    return render_template('add_expenses.html', 
                           user_categories=user_categories_list, 
                           predefined_categories=predefined_categories_filtered,
                           user_categories_count=user_categories_count,
                           max_categories_limit=max_categories_limit)

@app.route('/show_expenses', methods=['GET'])
def show_expenses():
    """Display all expenses and quick stats."""
    user_id = flask_session.get('user_id')
    print(user_id)
    
    selected_month = request.args.get('month')
    selected_category = request.args.get('category')
    time_period = request.args.get('time_period')  # Parameter for quick filters
    start_date = request.args.get('start_date')  # Start date for custom range
    end_date = request.args.get('end_date')  # End date for custom range

    # Parse filters
    if selected_month == "":
        selected_month = None
    if selected_category == "":
        selected_category = None

    # Handle quick filters (time_period)
    if time_period == "last_10_days":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
    elif time_period == "1_month":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    elif time_period == "3_months":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
    else:
        # Convert string dates to datetime for custom range filters
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

    with engine.connect() as conn:
        # Fetch user-specific categories
        user_categories = conn.execute(
            select(categories.c.category_id, categories.c.category_name)
            .where(categories.c.user_id == user_id)
        ).fetchall()

        # Fetch predefined categories for user_id = 1
        predefined_categories = conn.execute(
            select(categories.c.category_id, categories.c.category_name)
            .where(categories.c.user_id == 0)
        ).fetchall()

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
            categories.c.category_name
        ).select_from(expenses.join(categories, expenses.c.categoryid == categories.c.category_id))
        query = query.where(expenses.c.UserID == user_id)
        
        # Apply filters to the query
        if selected_month:
            query = query.where(expenses.c.expensedate.like(f"{selected_month}-%"))
        if selected_category:
            query = query.where(categories.c.category_name == selected_category)
        if start_date and end_date:
            query = query.where(expenses.c.expensedate.between(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        elif start_date:
            query = query.where(expenses.c.expensedate >= start_date.strftime('%Y-%m-%d'))
        elif end_date:
            query = query.where(expenses.c.expensedate <= end_date.strftime('%Y-%m-%d'))

        # Execute the query to fetch expenses
        result = conn.execute(query).fetchall()

        # Fetch distinct months for dropdown
        months_query = conn.execute(select(expenses.c.expensedate.distinct())).fetchall()
        months = sorted(set(expensedate.strftime('%Y-%m') for expensedate, in months_query))

        # Fetch min and max amount
        min_max_query = conn.execute(
            select(
                db.func.min(expenses.c.amount).label('min_amount'),
                db.func.max(expenses.c.amount).label('max_amount')
            ).where(expenses.c.UserID == user_id)  # Apply user filter here as well
        ).fetchone()

        # Set default values if query does not return results
        min_amount = min_max_query.min_amount if min_max_query and min_max_query.min_amount is not None else 0
        max_amount = min_max_query.max_amount if min_max_query and min_max_query.max_amount is not None else 10000  # Use a reasonable default

        # Quick Stats Query
        total_spent = conn.execute(select(db.func.sum(expenses.c.amount)).where(expenses.c.UserID == user_id)).scalar() or 0
        num_expenses = conn.execute(select(db.func.count(expenses.c.ExpenseID)).where(expenses.c.UserID == user_id)).scalar() or 0
        avg_expense = conn.execute(select(db.func.avg(expenses.c.amount)).where(expenses.c.UserID == user_id)).scalar() or 0

        # Highest Spent Category with Name
        highest_spent_category = conn.execute(
            select(
                categories.c.category_name,  # Retrieve category name
                db.func.sum(expenses.c.amount).label('total_amount')
            )
            .join(categories, categories.c.category_id == expenses.c.categoryid)  # Correct join using category_id
            .where(expenses.c.UserID == user_id)  # Apply user filter here as well
            .group_by(categories.c.category_name)  # Group by category name
            .order_by(db.func.sum(expenses.c.amount).desc())
            .limit(1)
        ).fetchone()

        highest_spent_category_name = highest_spent_category[0] if highest_spent_category else 'None'
        highest_spent_category_total = highest_spent_category[1] if highest_spent_category else 0.0
    print(user_categories)
    # Pass the stats to the template along with the expenses
    return render_template(
        'show_expenses.html',
        expenses=result,
        months=months,
        selected_month=selected_month,
        selected_category=selected_category,
        user_categories=user_categories,
        predefined_categories=predefined_categories,
        min_amount=min_amount,
        max_amount=max_amount,
        selected_time_period=time_period,  # Pass selected time period
        start_date=start_date.strftime('%Y-%m-%d') if start_date else '',  # Preserve custom start date
        end_date=end_date.strftime('%Y-%m-%d') if end_date else '',  # Preserve custom end date
        # Quick Stats
        total_spent=total_spent,
        num_expenses=num_expenses,
        avg_expense=avg_expense,
        highest_spent_category_name=highest_spent_category_name,
        highest_spent_category_total=highest_spent_category_total
    )


@app.route('/add_new_category', methods=['POST'])
def add_new_category():
    try:
        user_id = flask_session.get('user_id')
        MAX_CATEGORIES_PER_USER = 5

        # Only check limits for non-predefined categories (user_id != 1)
        if user_id != 0:
            with engine.connect() as conn:
                # Count the number of custom categories for the user
                category_count = conn.execute(
                    select(db.func.count().label('category_count'))
                    .where(categories.c.user_id == user_id)
                ).scalar()

            if category_count >= MAX_CATEGORIES_PER_USER:
                # Return an error if user exceeds max categories limit
                return "<h1>Error: You have reached the limit of custom categories!</h1>", 400

        category_name = request.form['category_name']
        category_desc = request.form['category_desc']

        with engine.connect() as conn:
            # Insert the new category for the user
            conn.execute(categories.insert().values(
                category_name=category_name,
                description=category_desc,
                user_id=user_id
            ))
            conn.commit()

        return redirect(url_for('show_expenses'))

    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/delete_category/', methods=['POST', 'GET'])
def delete_category():
    """Delete a user's custom category and associated expenses."""
    user_id = flask_session.get('user_id')
    category_id = request.form.get('category_id')
    print(f"Attempting to delete category with ID {category_id} for user {user_id}")
    if not category_id:
        flash('No category selected.', 'danger')
        return redirect(url_for('manage_categories'))
    with engine.connect() as conn:
        # Validate that the category exists and belongs to the user
        category = conn.execute(
            select(categories).where(
                categories.c.category_id == category_id,
                categories.c.user_id == user_id
            )
        ).fetchone()

        if category:
            # Delete the category
            conn.execute(
                expenses.delete().where(expenses.c.categoryid == category_id)
            )
            conn.execute(categories.delete().where(categories.c.category_id == category_id))
            conn.commit()
            flash('Category deleted successfully!', 'success')
        else:
            flash('Invalid category or you do not have permission to delete it.', 'danger')
    return redirect(url_for('show_expenses'))
@app.route('/submit', methods=['POST'])
def submit():
    """Handle expense submission."""
    try:
        # Get required fields
        user_id=flask_session.get('user_id')
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
        insert_expense(user_id, category, amount, date, description, receipt_path, time)
        # flash('New expense added successfully','info')

        # Redirect to the expenses page
        return redirect(url_for('show_expenses'))

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
                return redirect(url_for('show_expenses'))

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
    
@app.route('/delete_expense/<int:ExpenseID>', methods=['POST'])
def delete_expense(ExpenseID):
    """
    Deletes an expense by its ID.
    """
    try:
        with engine.connect() as conn:
            # Check if the expense exists
            expense_to_delete = conn.execute(select(expenses).where(expenses.c.ExpenseID == ExpenseID)).fetchone()
            if not expense_to_delete:
                flash("Error: Expense not found!", 'danger')
                return redirect(url_for('show_expenses'))

            # Delete the expense
            conn.execute(expenses.delete().where(expenses.c.ExpenseID == ExpenseID))
            conn.commit()

            flash("Expense deleted successfully!", 'success')
            return redirect(url_for('show_expenses'))

    except Exception as e:
        flash(f"Error deleting expense: {str(e)}", 'danger')
        return redirect(url_for('show_expenses'))
    
    
@app.route('/savings_goals', methods=['GET', 'POST'])
def savings_goals():
    user_id = session.get('user_id')
    family_head_id = session.get('family_head_id')

    if not user_id:
        flash("User not logged in.")
        return redirect(url_for('login'))

    # Update expired goals
    sql_update = text("""
        UPDATE Savings_goals
        SET Goal_status = 'Not Achieved'
        WHERE End_date < CURRENT_DATE
          AND Goal_status NOT IN ('Achieved', 'Cancelled');
    """)
    db.session.execute(sql_update)
    db.session.commit()

    # Get min and max target values from the database
    max_target_query = text("SELECT MAX(Target_amount) FROM Savings_goals WHERE Target_amount IS NOT NULL")
    min_target_query = text("SELECT MIN(Target_amount) FROM Savings_goals WHERE Target_amount IS NOT NULL")
    db_max_target = db.session.execute(max_target_query).scalar() or 100000  # Default to 100,000 if None
    db_min_target = db.session.execute(min_target_query).scalar() or 0       # Default to 0 if None

    # Retrieve filter parameters from the request
    goal_type = request.args.get('goal_type', 'all')
    goal_status = request.args.get('goal_status', 'all')
    min_target = request.args.get('min_target', db_min_target)
    max_target = request.args.get('max_target', db_max_target)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    search_query = request.args.get('search_query', '').strip()

    # Sorting
    sort_by = request.args.get('sort_by', 'priority')
    sort_order = request.args.get('sort_order', 'desc')
    valid_sort_columns = ['goal_id', 'priority', 'start_date', 'end_date', 'target_amount', 'Achieved_amount']

    # Validate sorting columns and order
    if sort_by not in valid_sort_columns:
        sort_by = 'priority'
    if sort_order not in ['asc', 'desc']:
        sort_order = 'desc'

    
    # Ensure min_target and max_target are integers and fall back to defaults if invalid
    try:
        min_target = int(min_target)
    except (ValueError, TypeError):
        min_target = db_min_target

    try:
        max_target = int(max_target)
    except (ValueError, TypeError):
        max_target = db_max_target

    # Sanitize search query
    if search_query:
        search_query = re.sub(r"[^a-zA-Z0-9\s]", "", search_query)  # Remove special characters
        search_query = f"%{search_query}%"  # Add wildcard for SQL LIKE

    # Build SQL query with filters
    base_query = """
        SELECT * FROM Savings_goals
        WHERE ((Goal_type = 'Personal' AND User_id = :user_id)
            OR (Goal_type = 'Family' AND (Family_head_id = :family_head_id OR Family_head_id IS NULL)))
    """
    query_params = {"user_id": user_id, "family_head_id": family_head_id}

    if goal_type != "all":
        base_query += " AND Goal_type = :goal_type"
        query_params["goal_type"] = goal_type

    if goal_status != "all":
        base_query += " AND Goal_status = :goal_status"
        query_params["goal_status"] = goal_status

    

    # Add range filter for target amount
    base_query += " AND Target_amount BETWEEN :min_target AND :max_target"
    query_params["min_target"] = min_target
    query_params["max_target"] = max_target

    if start_date:
        base_query += " AND Start_date >= :start_date"
        query_params["start_date"] = start_date

    if end_date:
        base_query += " AND End_date <= :end_date"
        query_params["end_date"] = end_date

    if search_query:
        base_query += " AND Goal_description LIKE :search_query"
        query_params["search_query"] = search_query

    base_query += f" ORDER BY {sort_by} {sort_order}"

    

    sql = text(base_query)
    savings_goals = db.session.execute(sql, query_params).fetchall()

    return render_template(
        "savings_goals.html",
        datas=savings_goals,
        goal_type=goal_type,
        goal_status=goal_status,
        min_target=min_target,
        max_target=max_target,
        start_date=start_date,
        end_date=end_date,
        search_query=search_query,
        db_min=db_min_target,
        db_max=db_max_target,
        sort_by=sort_by,
        sort_order=sort_order,
    )



@app.route("/add_amount/<int:id>", methods=["GET", "POST"])
def add_amount(id):
    user_id = session.get("user_id")
    family_head_id = session.get("family_head_id")

    sql = text("""
        SELECT * FROM Savings_goals 
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()

    if not goal:
        flash("Goal not found")
        return redirect(url_for("savings_goals"))

    goal_status = goal._mapping["Goal_status"]

    if goal_status != "Active":
        flash("Amount can only be added to active goals.")
        return redirect(url_for("savings_goals"))

    if request.method == "POST":
        additional_amount = float(request.form["additional_amount"])

        # Insert or Update the contribution in the contributions table
        contribution_sql = text("""
            INSERT INTO contributions (user_id, goal_id, contribution_amount)
            VALUES (:user_id, :goal_id, :contribution_amount)
            ON DUPLICATE KEY UPDATE contribution_amount = contribution_amount + :contribution_amount
        """)
        db.session.execute(contribution_sql, {
            "user_id": user_id,
            "goal_id": id,
            "contribution_amount": additional_amount
        })

        # Update achieved_amount in the Savings_goals table
        update_sql = text("""
            UPDATE Savings_goals 
            SET Achieved_amount = COALESCE(Achieved_amount, 0) + :amount
            WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
        """)
        db.session.execute(update_sql, {
            "amount": additional_amount,
            "goal_id": id,
            "user_id": user_id,
            "family_head_id": family_head_id
        })

        # Retrieve updated goal data to check if the goal is now "Achieved"
        goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()
        achieved_amount = goal._mapping["Achieved_amount"]
        target_amount = goal._mapping["Target_amount"]

        # Update goal status based on achieved amount
        if achieved_amount >= target_amount:
            status = "Achieved"
        elif goal_status == "Cancelled":
            status = "Cancelled"
        else:
            status = "Active"

        status_sql = text("""
            UPDATE Savings_goals 
            SET Goal_status = :status
            WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
        """)
        db.session.execute(status_sql, {"status": status, "goal_id": id, "user_id": user_id, "family_head_id": family_head_id})
        db.session.commit()

        flash("Amount Added Successfully!")
        return redirect(url_for("savings_goals"))

    return render_template("add_amount.html", data=goal)

@app.route("/add_goal", methods=['GET', 'POST'])
def add_goal():
    family_head_id = session.get('family_head_id')
    user_id = session.get('user_id')

    if request.method == "POST":
        target_amount = request.form['target_amount']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        goal_description = request.form['goal_description']
        goal_type = request.form['goal_type']
        priority = int(request.form.get('priority', 0))  # Default priority to 0 if not provided

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        today = datetime.now().date()
        goal_status = "Not Achieved" if today > end_date.date() else "Active"

        sql = text("""
            INSERT INTO Savings_goals 
            (User_id, family_head_id, Target_amount, start_date, end_date, Goal_description, Goal_type, Goal_status, priority)
            VALUES (:user_id, :family_head_id, :target_amount, :start_date, :end_date, :goal_description, :goal_type, :goal_status, :priority)
        """)
        db.session.execute(sql, {
            "user_id": user_id,
            "family_head_id": family_head_id,
            "target_amount": target_amount,
            "start_date": start_date,
            "end_date": end_date,
            "goal_description": goal_description,
            "goal_type": goal_type,
            "goal_status": goal_status,
            "priority": priority
        })
        db.session.commit()

        flash("Goal Added Successfully")
        return redirect(url_for('savings_goals'))

    return render_template("addgoals.html")


@app.route("/edit_goals/<id>", methods=['GET', 'POST'])
def edit_goals(id):
    user_id = session.get('user_id')
    family_head_id = session.get('family_head_id')

    if not user_id:
        flash("User not authenticated.")
        return redirect(url_for("login"))

    if request.method == 'POST':
        target_amount = request.form['target_amount']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        goal_description = request.form['goal_description']
        goal_type = request.form['goal_type']
        achieved_amount = request.form.get('Achieved_amount', 0)
        priority = int(request.form.get('priority', 0))  # Get priority from form

        # Update goal details
        sql_update = text("""
            UPDATE Savings_goals
            SET Target_amount = :target_amount, start_date = :start_date, end_date = :end_date, 
                Goal_description = :goal_description, Goal_type = :goal_type, Achieved_amount = :achieved_amount, priority = :priority
            WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
        """)
        db.session.execute(sql_update, {
            "target_amount": target_amount,
            "start_date": start_date,
            "end_date": end_date,
            "goal_description": goal_description,
            "goal_type": goal_type,
            "achieved_amount": achieved_amount,
            "goal_id": id,
            "user_id": user_id,
            "family_head_id": family_head_id,
            "priority": priority
        })

        # Insert or Update the contribution in the contributions table
        contribution_sql = text("""
            INSERT INTO contributions (user_id, goal_id, contribution_amount)
            VALUES (:user_id, :goal_id, :contribution_amount)
            ON DUPLICATE KEY UPDATE contribution_amount = :contribution_amount
        """)
        db.session.execute(contribution_sql, {
            "user_id": user_id,
            "goal_id": id,
            "contribution_amount": achieved_amount  # Assuming you're modifying the achieved_amount
        })

        # Update goal status based on achieved amount
        status = 'Achieved' if float(achieved_amount) >= float(target_amount) else 'Active'
        sql_status_update = text("""
            UPDATE Savings_goals
            SET goal_status = :status
            WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
        """)
        db.session.execute(sql_status_update, {"status": status, "goal_id": id, "user_id": user_id, "family_head_id": family_head_id})
        db.session.commit()
        flash("Goal Updated Successfully")
        return redirect(url_for("savings_goals"))

    sql_fetch_goal = text("SELECT * FROM Savings_goals WHERE Goal_id = :goal_id")
    goal = db.session.execute(sql_fetch_goal, {"goal_id": id}).fetchone()

    if not goal:
        flash("Goal not found!")
        return redirect(url_for("savings_goals"))
    
    return render_template("editgoals.html", datas=goal._mapping)



@app.route("/delete_goal/<int:id>", methods=["POST", "GET"])
def delete_goal(id):
    user_id = session.get("user_id")
    family_head_id = session.get("family_head_id")

    if not user_id:
        flash("User not authenticated.")
        return redirect(url_for("login"))

    sql_goal_check = text("""
        SELECT Goal_type, Family_head_id, user_id FROM Savings_goals WHERE Goal_id = :goal_id
    """)
    goal_data = db.session.execute(sql_goal_check, {"goal_id": id}).mappings().first()

    if not goal_data:
        flash("Goal not found.")
        return redirect(url_for("savings_goals"))

    goal_type = goal_data.Goal_type 
    goal_owner_id = goal_data.user_id  
    goal_family_head_id = goal_data.Family_head_id  
    if goal_type == "Personal":
        if goal_owner_id != user_id:
            flash("You can only delete your own personal goals.")
            return redirect(url_for("savings_goals"))
    
    elif goal_type == "Family":
        if goal_owner_id != user_id and goal_family_head_id != family_head_id:
            flash("Only the family head or the goal owner can delete this goal.")
            return redirect(url_for("savings_goals"))

    try:
        sql_delete_contributions = text("DELETE FROM Contributions WHERE goal_id = :goal_id")
        db.session.execute(sql_delete_contributions, {"goal_id": id})

        sql_delete_goal = text("DELETE FROM Savings_goals WHERE Goal_id = :goal_id")
        db.session.execute(sql_delete_goal, {"goal_id": id})

        db.session.commit()

        flash("Goal and its related contributions deleted successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting goal: {e}")

    return redirect(url_for("savings_goals"))





@app.route('/family_goals_dashboard')
def family_goals_dashboard():
    user_id = session.get('user_id')
    family_head_id = session.get('family_head_id')

    if not user_id:
        flash("User not logged in.")
        return redirect(url_for('login'))

    # Query to get each family member's total contribution to family goals
    contributions_query = text("""
        SELECT u.name, COALESCE(SUM(c.contribution_amount), 0) AS total_contribution
        FROM users u
        LEFT JOIN contributions c ON u.user_id = c.user_id
        INNER JOIN savings_goals g ON c.goal_id = g.goal_id
        WHERE g.goal_type = 'Family' AND g.family_head_id = :family_head_id
        GROUP BY u.name
        ORDER BY total_contribution DESC;
    """)

    family_contributions = db.session.execute(contributions_query, {"family_head_id": family_head_id}).fetchall()

    return render_template("family_dashboard.html", family_contributions=family_contributions)


@app.route("/cancel_goal/<id>", methods=["POST"])
def cancel_goal(id):
    user_id = session.get("user_id")
    family_head_id = session.get("family_head_id")

    if not user_id or not family_head_id:
        flash("User not logged in or family information unavailable.")
        return redirect(url_for("login"))

    # Check if goal exists and belongs to the user or family
    sql_check = text("""
        SELECT * FROM Savings_goals 
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql_check, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()

    if not goal:
        flash("Goal not found or access denied.")
        return redirect(url_for("savings_goals"))

    # Update goal status to "Cancelled"
    sql_update = text("""
        UPDATE Savings_goals 
        SET Goal_status = 'Cancelled' 
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """)
    db.session.execute(sql_update, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id})
    db.session.commit()

    flash("Goal cancelled successfully!")
    return redirect(url_for("savings_goals"))


@app.route("/restart_goal/<int:id>", methods=["POST"])
def restart_goal(id):
    user_id = session.get("user_id")
    family_head_id = session.get("family_head_id")

    if not user_id:
        flash("User not authenticated.")
        return redirect(url_for("login"))

    # Fetch the current goal's start_date and end_date
    sql_fetch = text("""
        SELECT start_date, end_date 
        FROM Savings_goals
        WHERE goal_id = :goal_id AND (user_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql_fetch, {
        "goal_id": id,
        "user_id": user_id,
        "family_head_id": family_head_id
    }).fetchone()

    if not goal:
        flash("Goal not found.")
        return redirect(url_for("savings_goals"))

    # Extract start and end dates
    goal_data = goal._mapping
    original_start_date = goal_data["start_date"]
    original_end_date = goal_data["end_date"]
    goal_duration = (original_end_date - original_start_date).days

    # Calculate new start and end dates
    new_start_date = datetime.now().date()
    new_end_date = new_start_date + timedelta(days=goal_duration)

    # Update the goal: reset achieved amount, set status to 'Active', and update dates
    sql_update = text("""
        UPDATE Savings_goals 
        SET achieved_amount = 0, goal_status = 'Active', start_date = :new_start_date, end_date = :new_end_date
        WHERE goal_id = :goal_id AND (user_id = :user_id OR family_head_id = :family_head_id)
    """)
    db.session.execute(sql_update, {
        "new_start_date": new_start_date,
        "new_end_date": new_end_date,
        "goal_id": id,
        "user_id": user_id,
        "family_head_id": family_head_id
    })
    db.session.commit()

    flash("Goal restarted successfully with updated start and end dates!")
    return redirect(url_for("savings_goals"))



# Route for progress bar
@app.route("/progress_bar/<int:id>", methods=["GET" , "POST"])
def progress_bar(id):
    user_id = session.get("user_id")
    family_head_id = session.get("family_head_id")
    sql = text("""
        SELECT * FROM Savings_goals 
        WHERE goal_id = :goal_id AND (user_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()

    if not goal:
        flash("Goal not found")
        return redirect(url_for("savings_goals"))
        
    achieved_amount = goal._mapping["Achieved_amount"] or 0
    target_amount = goal._mapping["Target_amount"]
    progress_percentage = round((achieved_amount / target_amount) * 100, 2) if target_amount > 0 else 0

    motivational_message = get_motivational_message(progress_percentage)
    
    progress_bar_color = get_progress_bar_color(progress_percentage)

    return render_template(
        "progressbar.html",
        goal=goal,
        progress_percentage=progress_percentage,
        motivational_message=motivational_message,
        progress_bar_color=progress_bar_color
    )
    
#function for motivational message
def get_motivational_message(progress_percentage):
    """
    Returns a motivational message based on progress percentage.
    """
    if progress_percentage == 0:
        return "Every journey starts with a single step. Begin today!"
    elif progress_percentage < 25:
        return "Great start! Keep pushing forward!"
    elif progress_percentage < 50:
        return "You're making progress! Keep the momentum going!"
    elif progress_percentage < 75:
        return "You're more than halfway there. Keep it up!"
    elif progress_percentage < 100:
        return "So close to the finish line! Don't stop now!"
    elif progress_percentage == 100:
        return "Congratulations! You've achieved your goal!"
    else:
        return "Keep striving for greatness!"

def get_progress_bar_color(progress_percentage):
    """
    Returns the appropriate color for the progress bar based on the progress percentage.
    """
    if progress_percentage == 100:
        return "green"
    elif progress_percentage >= 75:
        return "blue"
    elif progress_percentage >= 50:
        return "orange"
    elif progress_percentage >= 25:
        return "purple"
    else:
        return "red"
@app.route('/filter_savings_goals')
def filter_savings_goals():
    return render_template('filter_savings_goals.html')

@app.route('/investments', methods=['GET'])
def view_investments():
    user_id = session.get('user_id')
    
    if not user_id:
        flash("User not logged in.")
        return redirect(url_for('login'))
    
    investments = Investments.query.filter_by(User_id=user_id).all()
    
    return render_template('investments.html', investments=investments)
@app.route('/add_investment', methods=['GET', 'POST'])
def add_investment():
    user_id = session.get('user_id')

    if not user_id:
        flash("User not logged in.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        investment_type = request.form['investment_type']
        investment_name = request.form['investment_name']
        purchase_date = request.form['purchase_date']
        purchase_price = request.form['purchase_price']
        quantity = request.form['quantity']
        roi = request.form.get('roi') or None
        info = request.form.get('info') or None
        current_value = request.form.get('current_value') or None
        end_date = request.form.get('end_date') or None

        new_investment = Investments(
            User_id=user_id,
            investment_type=investment_type,
            investment_name=investment_name,
            purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d').date(),
            purchase_price=purchase_price,
            quantity=quantity,
            roi=roi,
            info=info,
            current_value=current_value,
            end_date=end_date and datetime.strptime(end_date, '%Y-%m-%d').date()
        )

        db.session.add(new_investment)
        db.session.commit()

        flash("Investment added successfully!", "success")
        return redirect(url_for('view_investments'))

    return render_template('add_investment.html')

@app.route('/edit_investment/<int:investment_id>', methods=['GET', 'POST'])
def edit_investment(investment_id):
    investment = Investments.query.get_or_404(investment_id)

    if request.method == 'POST':
        
        investment.investment_name = request.form['investment_name']
        investment.investment_type = request.form['investment_type']
        investment.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date()
        investment.purchase_price = request.form['purchase_price']
        investment.quantity = request.form.get('quantity') or 1
        investment.roi = request.form.get('roi') or None
        investment.current_value = request.form.get('current_value') or None
        investment.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form.get('end_date') else None
        investment.info = request.form.get('info') or None 
        
        db.session.commit()
        flash("Investment updated successfully!", "success")
        return redirect(url_for('view_investments'))

    return render_template('edit_investment.html', investment=investment)

@app.route('/delete_investment/<int:investment_id>', methods=['POST'])
def delete_investment(investment_id):
    
    investment = Investments.query.get_or_404(investment_id)

    try:
        
        db.session.delete(investment)
        db.session.commit()
        flash('Investment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting investment: ' + str(e), 'danger')

    return redirect(url_for('view_investments'))

@app.route('/calculate_returns/<int:investment_id>', methods=['GET', 'POST'])
def calculate_returns(investment_id):
    user_id = session.get('user_id')

    if not user_id:
        flash("User not logged in.")
        return redirect(url_for('login'))

    investment = Investments.query.filter_by(investment_id=investment_id, User_id=user_id).first()

    if not investment:
        flash("Investment not found.")
        return redirect(url_for('show_investments'))

    results = []

    interest_rate = 0
    face_value = 0
    accrued_interest = 0
    dividend_yield = 0
    capital_appreciation = 0
    expense_ratio = 0
    nav_growth = 0
    rental_income = 0
    property_appreciation = 0

    if request.method == 'POST':
        investment_type = investment.investment_type
        purchase_value = investment.purchase_price
        current_value = investment.current_value
        

        interest_rate = Decimal(request.form.get("interest_rate", 0))
        face_value = Decimal(request.form.get("face_value", 0))
        accrued_interest = Decimal(request.form.get("accrued_interest", 0))
        dividend_yield = Decimal(request.form.get("dividend_yield", 0))
        capital_appreciation = Decimal(request.form.get("capital_appreciation", 0))
        expense_ratio = Decimal(request.form.get("expense_ratio", 0))
        nav_growth = Decimal(request.form.get("nav_growth", 0))
        rental_income = Decimal(request.form.get("rental_income", 0))
        property_appreciation = Decimal(request.form.get("property_appreciation", 0))
        
        if investment_type == 'fixed_deposit':
            returns = purchase_value * ((1 + interest_rate / 100) ** 1) - purchase_value
        elif investment_type == 'stocks':
            returns = (purchase_value * (dividend_yield / 100)) + (current_value - purchase_value)
        elif investment_type == 'mutual_funds':
            returns = current_value * (1 + nav_growth / 100) - purchase_value
        elif investment_type == 'bonds':
            returns = (face_value + accrued_interest) - purchase_value
        elif investment_type == 'real_estate':
            returns = (rental_income + property_appreciation)
        elif investment_type == 'savings_account':
            returns = purchase_value * (interest_rate / 100)
        else:
            returns = 0
        roi = (returns / purchase_value) * 100
        investment.roi = roi
        db.session.commit()
        
        results.append({
            'investment_name': investment.investment_name,
            'returns': returns,
            'roi':roi
        })

        interest_rate = 0
        face_value = 0
        accrued_interest = 0
        dividend_yield = 0
        capital_appreciation = 0
        expense_ratio = 0
        nav_growth = 0
        rental_income = 0
        property_appreciation = 0
        

    return render_template('show_returns.html', investment=investment, results=results,
                           interest_rate=interest_rate, face_value=face_value, accrued_interest=accrued_interest,
                           dividend_yield=dividend_yield, capital_appreciation=capital_appreciation, 
                           expense_ratio=expense_ratio, nav_growth=nav_growth, rental_income=rental_income, 
                           property_appreciation=property_appreciation,roi=investment.roi)

@app.route('/budgethome')
def budgethome():
    return render_template('index.html')


@app.route('/addBudget')
def bud():
    user_id=flask_session.get("user_id")
    sql=text("SELECT name from users WHERE user_id=:id")
    user_name=db.session.execute(sql,{
        "id":user_id
    }).scalar()
    cat=db.session.execute(text("Select category_id,category_name from categories"))
    family_head_id=flask_session.get("family_head_id")
    return render_template('addBudget.html',data=user_name,categories=cat)

@app.route('/viewAlerts')
def ale():
    user_id=flask_session.get("user_id")
    family_head_id=flask_session.get("family_head_id")
    with db.engine.connect() as conn:
        alerts=conn.execute(text("select * from alert"))
        alerts=[[a.alert_id,a.budget_id,a.alert_type,a.alert_message,a.alert_date,a.is_resolved] for a in alerts]
        return render_template('Alerts.html',alerts=alerts)
    
@app.route("/BudgetPercentage", methods=["GET"])
def BudgetPercentage():
    user_id = flask_session.get("user_id")
    family_head_id = flask_session.get("family_head_id")
    sql = text("""SELECT (SUM(e.amount) /b.limit) * 100 
            FROM budgets b 
            INNER JOIN expenses e ON b.category_id = e.categoryid 
            WHERE b.user_id = :user AND e.UserID = :user AND e.expensedate BETWEEN b.start_date AND b.end_date
            GROUP BY b.budget_id
        """)
    percentage = db.session.execute(sql, {"user": user_id}).scalar()
    return jsonify({"percent": percentage}), 200

    

@app.route('/Budget',methods=['GET'])
def getall_budget():
    user_id=flask_session.get("user_id")
    family_head_id=flask_session.get("family_head_id")
    users_dict={0:None}
    users=db.session.execute(text("Select user_id,name from users where user_id in (SELECT user_id from users where family_head_id=:head)")
    ,{"head":family_head_id})
    for user in users:
        users_dict[user.user_id]=user.name
    print(user_id,family_head_id)
    if user_id==family_head_id:
        sql=(text("SELECT * FROM budgets where user_id in (SELECT user_id from users where family_head_id=:head)"))
        budgets=db.session.execute(sql,{
            'head':family_head_id
        })
    else:
        sql=text("SELECT * FROM  budgets where user_id =:user")
        budgets=db.session.execute(sql,{
            'user':user_id
        })
    budgets=[[budget.budget_id,budget.category_id,budget.limit,budget.start_date,budget.end_date,users_dict[budget.user_id]] for budget in budgets]
    return render_template('viewBudget.html',budgets=budgets)

@app.route('/Budget',methods=['POST'])
def add_budget():
    user=flask_session.get("user_id")
    data=request.get_json()
    budget=Budget(category_id=data['category_id'],user_id=user,limit=data['limit'],start_date=data['start_date'],end_date=data['end_date'])
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
    user_id=flask_session.get("user_id")
    family_head_id=flask_session.get("family_head_id")
    if user_id==family_head_id:
        sql=text(""" 
            SELECT * FROM  alert WHERE  
             budget_id  IN (SELECT budget_id FROM budgets
             WHERE user_id IN (select user_id from users where user_id=:user or family_head_id=:head))
             AND is_resolved=0
        """)
        alerts=db.session.execute(sql,{
            "user":user_id,
            "head":family_head_id
        })
    else:
        sql=text(""" 
             SELECT * FROM  alert WHERE  
             budget_id  IN (SELECT budget_id FROM budgets
             WHERE user_id=:user)
             AND is_resolved=0
        """)
        alerts=db.session.execute(sql,{
            "user":user_id,
        })
    alert=[]
    for i in alerts:
        alert.append([i.alert_id,i.alert_date.strftime('%Y-%m-%d'),i.alert_message,i.alert_type,i.budget_id,i.is_resolved])
    return jsonify({"alerts":alert}),200

@app.route('/MarkAlert',methods=["PUT"])
def MarkAlert():
    data=request.get_json()
    print(data)
    try:
        alert = db.session.execute(text("UPDATE alert SET is_resolved = 1 WHERE alert_id = :id"),{"id":data["alert_id"]})
        db.session.commit()
        return jsonify({"ok":1}),200
    except Exception as e:
        print(str(e))
        return jsonify({"ok":0}),400


#MODULE 5 
@app.route('/mod5sprint2')
def mod5sprint2():
    return render_template('sprint2mod5.html')

def get_user_data(query, user_id=None, is_family_head=False):
    if is_family_head:
        return query.all()
    else:
        return query.filter_by(user_id=user_id).all()

def fetch_budgets(start_date=None, end_date=None, category_id=None):
    user_id = flask_session.get('user_id')  # Retrieving user_id from session
    query = Budget.query.filter_by(user_id=user_id)

    # Apply filters
    if start_date:
        query = query.filter(Budget.start_date >= start_date)
    if end_date:
        query = query.filter(Budget.end_date <= end_date)
    if category_id:
        query = query.filter(Budget.category_id == category_id)

    budgets = query.all()
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

def fetch_savings_goals(start_date=None, end_date=None, status=None):
    user_id=flask_session.get('user_id')
    query = SavingsGoal.query.filter_by(User_id=user_id)
    if start_date:
        query = query.filter(SavingsGoal.start_date >= start_date)
    if end_date:
        query = query.filter(SavingsGoal.end_date <= end_date)
    if status:
        query = query.filter(SavingsGoal.Goal_status == status)
    
    goals = query.all()
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
    print(data)
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
    return render_template('budgetfilter.html', categories=categories, budgets=filtered_budgets)


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
    return render_template('saving_goalsfilter.html', statuses=statuses, savings_goals=filtered_savings)

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




@app.route('/filter_budgets', methods=['POST'])
def filter_budgets():

    filters = request.json
    flask_session['filters'] = filters
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    category_id = filters.get('category_id')

    df = fetch_budgets(start_date=start_date, end_date=end_date, category_id=category_id)
    return jsonify(df.to_dict(orient='records'))


# Route to generate and send plots
@app.route('/generate_budget_plot', methods=['POST'])
def generate_budget_plot():
    plot_type = request.json['plot_type']
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    category_id = filters.get('category_id')
    df = fetch_budgets(start_date=start_date, end_date=end_date, category_id=category_id)
    

    # Pie Chart: Budget distribution by category
    if plot_type == 'pie':
        category_sums = df.groupby('category_id')['limit'].sum()
        print("category_sums",category_sums)
        plt.figure(figsize=(8, 6))
        category_sums.plot.pie(autopct='%1.1f%%', startangle=90, cmap='tab20', ylabel='')
        plt.title('Budget Distribution by Category')
    
    # Bar Chart: Budget limit comparison by category
    elif plot_type == 'bar':
        category_sums = df.groupby('category_id')['limit'].sum()
        plt.figure(figsize=(8, 6))
        category_sums.plot.bar(color='skyblue', edgecolor='black')
        plt.title('Budget Limit by Category')
        plt.xlabel('category')
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

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')



# Route to download CSV
@app.route('/export_budget_csv', methods=['POST'])
def export_budget_csv():
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    category_id = filters.get('category_id')

    df = fetch_budgets(start_date=start_date, end_date=end_date, category_id=category_id)
    file_path = 'data/filtered_budgets.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)





@app.route('/filter_expenses', methods=['POST'])
def filter_expenses():
    filters = request.json
    flask_session['filters'] = filters  # Store filters in session for plot endpoints
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




@app.route('/filter_savings', methods=['POST'])
def filter_savings():
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    status = filters.get('status')
    df = fetch_savings_goals(start_date=start_date, end_date=end_date, status=status)
    return jsonify(df.to_dict(orient='records'))

@app.route('/export_goal_csv', methods=['POST'])
def export_goal_csv():
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    status = filters.get('status')
    df = fetch_savings_goals(start_date=start_date, end_date=end_date, status=status)
    file_path = 'data/filtered_savings.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)

# Route to generate and send plots
@app.route('/generate_goal_plot', methods=['POST'])
def generate_goal_plot():
    plot_type = request.json['plot_type']
    filters = request.json
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    status = filters.get('status')

    df = fetch_savings_goals(start_date=start_date, end_date=end_date, status=status)

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

if __name__ == '__main__':
    app.run(debug=True)
