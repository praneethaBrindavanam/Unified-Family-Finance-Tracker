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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/unified_family'

#change the password and databasename as per your system
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)
DATABASE_URI = 'mysql+pymysql://root:root@localhost/unified_family'
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


class Profile(db.Model):  
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    family_head_id = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"Username: {self.username}, Family: {self.family_name}, Role: {self.role}"


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.Enum('HoF', 'Member', 'Viewer'), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    family_code = db.Column(db.String(6), unique=True, nullable=False)

    def __repr__(self):
        return f"Role: {self.role_name}, Family: {self.family_name}, Code: {self.family_code}"

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


# Home
@app.route('/')
def home():
    return render_template('home.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate the user credentials
        user = Profile.query.filter_by(username=username, password=password).first()
        if user:
            flash(f"Welcome, {user.username}!", "success")
            return redirect('/welcome')  # Redirect to the welcome page
        else:
            flash("Invalid username or password. Please try again.", "error")
            return redirect('/login')  # Redirect back to the login page for retry
    return render_template('login.html')



# Route for profiles table
@app.route('/profiles')
def profiles():
    profiles = Profile.query.all()
    return render_template('index.html', profiles=profiles)


# Route for add profile page
@app.route('/add_data')
def add_data():
    return render_template('add_profile.html')


# Function to handle profile addition
@app.route('/add', methods=["POST"])
def add_profile():
    username = request.form.get("username")
    email = request.form.get("email")
    family_name = request.form.get("family_name")
    role = request.form.get("role")
    family_head_id = request.form.get("family_head_id")
    password = request.form.get("password")

    if username and email and family_name and role and family_head_id and password:
        new_profile = Profile(
            username=username,
            email=email,
            family_name=family_name,
            role=role,
            family_head_id=family_head_id,
            password=password
        )
        db.session.add(new_profile)
        db.session.commit()
        return redirect('/add_role_data')
    else:
        return redirect('/add_data')


# Function to delete a profile
@app.route('/delete/<int:id>')
def delete_profile(id):
    profile = Profile.query.get(id)
    if profile:
        db.session.delete(profile)
        db.session.commit()
    return redirect('/profiles')


# Route for roles table
@app.route('/roles')
def roles():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)


# Route for add role page
@app.route('/add_role_data')
def add_role_data():
    return render_template('add_role.html')


@app.route('/add_role', methods=["POST"])
def add_role():
    role_name = request.form.get("role_name")
    family_name = request.form.get("family_name")
    family_code = request.form.get("family_code")

    if not family_code:  # Auto-generate a 6-digit code if not provided
        family_code = str(random.randint(100000, 999999))

    if role_name and family_name and family_code:
        try:
            new_role = Role(role_name=role_name, family_name=family_name, family_code=family_code)
            db.session.add(new_role)
            db.session.commit()
        except Exception as e:
            print(f"Error: {e}")  # Debugging
            db.session.rollback()
        return redirect('/welcome')
    else:
        return redirect('/add_role_data')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')


# Function to delete a role
@app.route('/delete_role/<int:id>')
def delete_role(id):
    role = Role.query.get(id)
    if role:
        db.session.delete(role)
        db.session.commit()
    return redirect('/roles')


# Function to delete all roles and profiles
@app.route('/delete_roles', methods=["GET", "POST"])
def delete_all_roles():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        family_code = request.form.get("family_code")

        if not username or not password or not family_code:
            flash("All fields are required.", "error")
            return redirect('/delete')

        # Check if the credentials and family code match any profile and role
        profile = Profile.query.filter_by(username=username, password=password).first()
        role = Role.query.filter_by(family_code=family_code).first()

        if profile and role and profile.family_name == role.family_name:
            # Delete all profiles and roles associated with the family
            Profile.query.filter_by(family_name=profile.family_name).delete()
            Role.query.filter_by(family_name=role.family_name).delete()
            db.session.commit()
            flash("All roles and profiles deleted successfully.", "success")
            return redirect('/')#home
        
        else:
            flash("Invalid credentials or family code. Please try again.", "error")
            return redirect('/delete')

    return render_template('delete.html')

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
    
@app.route("/cancel_goal/<string:id>", methods=["POST"])
def cancel_goal(id):
    user_id = flask_session.get("user_id")
    family_head_id = flask_session.get("family_head_id")

    if not user_id or not family_head_id:
        flash("User not logged in or family information unavailable.")
        return redirect(url_for("login"))

    # Check if goal exists and belongs to the user or family
    sql_check = text("""
        SELECT * FROM Savings_goals 
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)""")
    goal = db.session.execute(sql_check, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()

    if not goal:
        flash("Goal not found or access denied.")
        return redirect(url_for("savings_goals"))

    # Update goal status to "Cancelled"
    sql_update = text("""
        UPDATE Savings_goals 
        SET Goal_status = 'Cancelled' 
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """
    )
    db.session.execute(sql_update, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id})
    db.session.commit()

    flash("Goal cancelled successfully!")
    return redirect(url_for("savings_goals"))
    

@app.route('/savings_goals', methods=['GET', 'POST'])
def savings_goals():
    user_id = flask_session.get('user_id')
    family_head_id = flask_session.get('family_head_id')

    if not user_id or not family_head_id:
        flash("User not logged in or family information unavailable.")
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

    # Filters and search
    status_filter = request.args.get('status', 'all')
    search_query = request.form.get('search_query', '').strip()

    # Build query dynamically
    base_query = """
        SELECT * 
        FROM Savings_goals
        WHERE 
            ((Goal_type = 'Personal' AND User_id = :user_id)
            OR
            (Goal_type = 'Family' AND Family_head_id = :family_head_id))
    """

    if status_filter != 'all':
        base_query += " AND Goal_status = :status_filter"

    if search_query:
        base_query += " AND Goal_description LIKE :search_query"

    sql = text(base_query)

    query_params = {
        "user_id": user_id,
        "family_head_id": family_head_id,
        "status_filter": status_filter if status_filter != 'all' else None,
        "search_query": f"%{search_query}%" if search_query else None
    }

    savings_goals = db.session.execute(sql, {k: v for k, v in query_params.items() if v is not None}).fetchall()

    return render_template(
        "savings_goals.html",
        datas=savings_goals,
        status_filter=status_filter,
        search_query=search_query
    )


@app.route("/add_amount/<string:id>", methods=["GET", "POST"])
def add_amount(id):
    user_id = flask_session.get("user_id")
    family_head_id = flask_session.get("family_head_id")

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

        # Update achieved_amount
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

        # Update goal status
        goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()
        achieved_amount = goal._mapping["Achieved_amount"]
        target_amount = goal._mapping["Target_amount"]

        status = "Achieved" if achieved_amount >= target_amount else "Active"
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



@app.route("/addgoal", methods=['GET', 'POST'])
def add_Goal():
    family_head_id = flask_session.get('family_head_id')
    user_id = flask_session.get('user_id')

    if request.method == "POST":
        target_amount = request.form['target_amount']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        goal_description = request.form['goal_description']
        goal_type = request.form['goal_type']

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        today = datetime.now().date()
        goal_status = "Not Achieved" if today > end_date.date() else "Active"

        sql = text("""
            INSERT INTO Savings_goals 
            (User_id, family_head_id, Target_amount, start_date, end_date, Goal_description, Goal_type, Goal_status)
            VALUES (:user_id, :family_head_id, :target_amount, :start_date, :end_date, :goal_description, :goal_type, :goal_status)
        """)
        db.session.execute(sql, {
            "user_id": user_id,
            "family_head_id": family_head_id,
            "target_amount": target_amount,
            "start_date": start_date,
            "end_date": end_date,
            "goal_description": goal_description,
            "goal_type": goal_type,
            "goal_status": goal_status
        })
        db.session.commit()

        flash("Goal Added Successfully")
        return redirect(url_for('savings_goals'))

    return render_template("addgoals.html")


@app.route("/edit_Goals/<string:id>", methods=['GET', 'POST'])
def edit_Goals(id):
    user_id = flask_session.get('user_id')

    if request.method == 'POST':
        target_amount = request.form['target_amount']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        goal_description = request.form['goal_description']
        goal_type = request.form['goal_type']
        achieved_amount = request.form.get('Achieved_amount', 0)

        sql = text("""
            UPDATE Savings_goals 
            SET Target_amount = :target_amount, start_date = :start_date, end_date = :end_date, 
                Goal_description = :goal_description, Goal_type = :goal_type, Achieved_amount = :achieved_amount
            WHERE Goal_id = :goal_id AND User_id = :user_id
        """)
        db.session.execute(sql, {
            "target_amount": target_amount,
            "start_date": start_date,
            "end_date": end_date,
            "goal_description": goal_description,
            "goal_type": goal_type,
            "achieved_amount": achieved_amount,
            "goal_id": id,
            "user_id": user_id
        })
        db.session.commit()

        flash("Goal Updated Successfully")
        return redirect(url_for("savings_goals"))

    sql = text("SELECT * FROM Savings_goals WHERE Goal_id = :goal_id")
    goal = db.session.execute(sql, {"goal_id": id}).fetchone()

    return render_template("editgoals.html", datas=goal)


@app.route("/delete_Goals/<string:id>", methods=['POST' , 'GET'])
def delete_Goals(id):
    user_id = flask_session.get('user_id')

    sql = text("DELETE FROM Savings_goals WHERE Goal_id = :goal_id AND User_id = :user_id")
    db.session.execute(sql, {"goal_id": id, "user_id": user_id})
    db.session.commit()

    flash('Goal Deleted Successfully')
    return redirect(url_for("savings_goals"))



@app.route("/restart_goal/<int:goal_id>", methods=["POST"])
def restart_goal(goal_id):
    user_id = flask_session.get("user_id")
    family_head_id = flask_session.get("family_head_id")

    if not user_id or not family_head_id:
        flash("User not logged in or family information unavailable.")
        return redirect(url_for("login"))

    # Fetch the current goal's start_date and end_date
    sql_fetch = text("""
        SELECT start_date, end_date 
        FROM Savings_goals
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql_fetch, {
        "goal_id": goal_id,
        "user_id": user_id,
        "family_head_id": family_head_id
    }).fetchone()

    if not goal:
        flash("Goal not found.")
        return redirect(url_for("savings_goals"))

    # Calculate the duration of the goal
    original_start_date = goal._mapping["start_date"]
    original_end_date = goal._mapping["end_date"]
    goal_duration = (original_end_date - original_start_date).days

    # Set the new start_date to today and calculate the new end_date
    new_start_date = datetime.now().date()
    new_end_date = new_start_date + timedelta(days=goal_duration)

    # Update the goal: reset achieved amount, set status to 'Active', and update start_date and end_date
    sql_update = text("""
        UPDATE Savings_goals 
        SET Achieved_amount = 0, Goal_status = 'Active', start_date = :new_start_date, end_date = :new_end_date
        WHERE Goal_id = :goal_id AND (User_id = :user_id OR family_head_id = :family_head_id)
    """)
    db.session.execute(sql_update, {
        "new_start_date": new_start_date,
        "new_end_date": new_end_date,
        "goal_id": goal_id,
        "user_id": user_id,
        "family_head_id": family_head_id
    })
    db.session.commit()

    flash("Goal restarted successfully with updated start and end dates!")
    return redirect(url_for("savings_goals"))

@app.route("/progress_bar/<string:id>", methods=["GET"])
def progress_bar(id):
    user_id = flask_session.get("user_id")
    family_head_id = flask_session.get("family_head_id")

    # Fetch goal details
    sql = text("""
        SELECT * FROM Savings_goals 
        WHERE goal_id = :goal_id AND (user_id = :user_id OR family_head_id = :family_head_id)
    """)
    goal = db.session.execute(sql, {"goal_id": id, "user_id": user_id, "family_head_id": family_head_id}).fetchone()

    if not goal:
        flash("Goal not found")
        return redirect(url_for("savings_goals"))

    # Calculate progress percentage with rounding
    achieved_amount = goal._mapping["Achieved_amount"]
    target_amount = goal._mapping["Target_amount"]
    progress_percentage = round((achieved_amount / target_amount) * 100, 2) if target_amount > 0 else 0

    return render_template(
        "progressbar.html",
        goal=goal,
        progress_percentage=progress_percentage
    )

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
        expenses = db.session.execute(
                text(
                    "SELECT e.amount AS amt, e.expensedate AS exp_date "
                    "FROM expenses e "
                    "INNER JOIN budgets b ON e.categoryid = b.category_id "
                    "AND e.expensedate BETWEEN b.start_date AND b.end_date "
                    "WHERE b.budget_id = :BUD;"
                ),
                {"BUD": alert[-1][4]}
            )
        expense_list = [[expense.amt, expense.exp_date.strftime('%Y-%m-%d')] for expense in expenses]
        alert[-1].append(expense_list)
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
