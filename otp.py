from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import pymysql
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, func, text
from sqlalchemy.orm import sessionmaker

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = ''  # Your email
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

# Set up database connection and session (same as your current database setup)
DB_USERNAME = "root"
DB_PASSWORD = "mysql123"
DB_HOST = "127.0.0.1:3306"
DB_NAME = "familyfinance1"

DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

# Define users table schema (as in your current code)
users = Table(
    'users', metadata,
    Column('user_id', Integer, primary_key=True, autoincrement=True), 
    Column('name', String(255), nullable=False),
    Column('email', String(255), unique=True, nullable=False),
    Column('password_hash', String(255), nullable=False),
    Column('phone_number', String(20), nullable=True),
    Column('role', String(50), nullable=False),
    Column('created_at', String(50), nullable=False, default=func.now())
)

# Generate a password reset token
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset')

# Verify the password reset token
def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
    except:
        return None  # Invalid or expired token
    return email

# Route for forgot password page
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Check if the email exists in the database
        user = session.execute(users.select().where(users.c.email == email)).fetchone()
        if user:
            token = generate_reset_token(email)
            reset_link = url_for('reset_password', token=token, _external=True)
            # Send email with the reset link
            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_link}"
            mail.send(msg)
            flash('An email with instructions to reset your password has been sent!', 'info')
        else:
            flash('Email not found!', 'error')
    return render_template('forgot_password.html')

# Route for the password reset link
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        # Update the user's password in the database
        hashed_password = new_password  # You should hash the password here
        session.execute(
            users.update().where(users.c.email == email).values(password_hash=hashed_password)
        )
        session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# Route for login page (as a placeholder)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check login logic (e.g., match password hash)
        # Implement your login logic here
        return "Login successful"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
