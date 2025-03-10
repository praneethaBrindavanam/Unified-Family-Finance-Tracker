from flask import *
from flask_mail import *
from random import *

app = Flask(__name__)
#mail = Mail(app)


app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = '587'
app.config["MAIL_USERNAME"] = 'family005778@gmail.com'
app.config["MAIL_PASSWORD"]= 'btyx smvk ubdl mkdc'
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False


mail = Mail(app)
otp = randint(000000,999999)

@app.route("/")
def index():
    return render_template("verification.html")

@app.route('/verify',methods = ["POST"])
def verify():
    email = request.form["email"]

    msg = Message('OTP',sender = 'family005778@gmail.com', recipients = [email])
    msg.body = str(otp)
    mail.send(msg)
    return render_template('verify.html')

@app.route('/validate',methods = ["POST"])
def validate():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        return "<h3>Email verified successfully</h3>"
    return "<h3>failure</h3>"
    
    
if __name__ == "__main__":
    app.run(debug = True)
