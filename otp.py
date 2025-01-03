from flask import Flask, render_template, request, jsonify
import smtplib
import random
from email.message import EmailMessage

app = Flask(__name__)

# Generate OTP
def generate_otp():
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return otp

# Email sending function
def send_email(to_email, otp):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        from_mail = 'family005778@gmail.com'
        server.login(from_mail, 'bwde dnao axmg wdxz')

        msg = EmailMessage()
        msg['Subject'] = "OTP Verification"
        msg['From'] = from_mail
        msg['To'] = to_email
        msg.set_content(f"Your OTP is: {otp}")

        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/')
def index():
    return render_template('verification.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    to_email = data.get('email')
    otp = generate_otp()

    if send_email(to_email, otp):
        return jsonify({"status": "success", "message": "OTP sent successfully!", "otp": otp})
    else:
        return jsonify({"status": "error", "message": "Failed to send OTP."})

if __name__ == '__main__':
    app.run(debug=True)
