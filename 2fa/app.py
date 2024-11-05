import bcrypt
import random
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a strong secret key here

# Twilio credentials (replace with your credentials or use environment variables)
TWILIO_ACCOUNT_SID = 'AC9ea11a83d033ae58512f5cd04e4f40ca'
TWILIO_AUTH_TOKEN = '837f93ae18257cb2b5e29c544926e795'
TWILIO_PHONE_NUMBER = '+18478071252'

# In-memory user database and OTP storage
users_db = {}
otp_store = {}

# Twilio client setup
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Password hashing and verification
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password)

# OTP generation and sending
def generate_otp():
    return random.randint(100000, 999999)

def send_otp(phone_number, otp):
    message_body = f"Your login OTP is: {otp}"
    try:
        twilio_client.messages.create(
            body=message_body,
            from_=+18478071252,
            to=+919902989020
        )
        print(f"Message sent to {phone_number}")
    except TwilioRestException as e:
        print(f"TwilioRestException: {e}")

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone']
        hashed_password = hash_password(password)
        users_db[username] = {'password': hashed_password, 'phone': phone_number}
        flash("User registered successfully!")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_db.get(username)
        if user and verify_password(user['password'], password):
            otp = generate_otp()
            otp_store[username] = {'otp': otp, 'expires_at': time.time() + 300}
            send_otp(user['phone'], otp)
            session['username'] = username
            flash("Password verified! OTP sent to your phone.")
            return redirect(url_for('verify_otp'))
        else:
            flash("Invalid username or password.")
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp_input = request.form['otp']
        username = session.get('username')
        otp_data = otp_store.get(username)
        if otp_data and time.time() < otp_data['expires_at'] and otp_data['otp'] == int(otp_input):
            del otp_store[username]
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Invalid or expired OTP.")
    return render_template('verify_otp.html')

if __name__ == '__main__':
    app.run(debug=True)
