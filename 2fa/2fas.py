import bcrypt
import random
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Twilio credentials (replace with your credentials or use environment variables)
TWILIO_ACCOUNT_SID = 'AC9ea11a83d033ae58512f5cd04e4f40ca'
TWILIO_AUTH_TOKEN = '837f93ae18257cb2b5e29c544926e795'
TWILIO_PHONE_NUMBER = '+18478071252'

# User database (for demonstration purposes)
users_db = {}

# OTP storage with expiration times
otp_store = {}

# Twilio client setup
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Function to hash passwords
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed

# Function to verify passwords
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password)

# Function to generate a random OTP
def generate_otp():
    return random.randint(100000, 999999)

# Function to send OTP via SMS
def send_otp(phone_number, otp):
    message_body = f"Your login OTP is: {otp}"
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"Message sent: {message.sid}")
    except TwilioRestException as e:
        print(f"TwilioRestException: {e}")

# Function to register a new user
def register_user(username, password, phone_number):
    hashed_password = hash_password(password)
    users_db[username] = {'password': hashed_password, 'phone': phone_number}
    print(f"User {username} registered successfully!")

# Function to initiate login (first step: password check)
def login_step1(username, password):
    user = users_db.get(username)
    if user and verify_password(user['password'], password):
        otp = generate_otp()
        otp_store[username] = {'otp': otp, 'expires_at': time.time() + 300}  # OTP expires in 5 minutes
        send_otp(user['phone'], otp)
        print("Password verified! OTP sent to your phone.")
        return True
    else:
        print("Invalid username or password.")
        return False

# Function to verify OTP (second step: 2FA)
def login_step2(username, otp):
    otp_data = otp_store.get(username)
    if otp_data:
        if time.time() < otp_data['expires_at'] and otp_data['otp'] == otp:
            del otp_store[username]  # Remove OTP after successful verification
            print("Login successful!")
            return True
        else:
            print("Invalid or expired OTP.")
    else:
        print("No OTP found. Please initiate login again.")
    return False

# Example usage
if __name__ == "__main__":
    # Register a user
    register_user("testuser", "securepassword", "+919902989020")

    # Simulate login process
    if login_step1("testuser", "securepassword"):
        print("Sending OTP to:", users_db["testuser"]["phone"])
        print("Twilio Phone Number:", TWILIO_PHONE_NUMBER)

        # Prompt for OTP input
        print("Please enter the OTP you received:")

        # Input handling for the OTP
        max_attempts = 3  # Limit the number of attempts
        for attempt in range(max_attempts):
            user_input = input(f"Attempt {attempt + 1}/{max_attempts} - Enter OTP: ")
            if user_input.isdigit() and len(user_input) == 6:  # Check if input is all digits and 6 characters long
                user_otp = int(user_input)  # Convert to integer
                if login_step2("testuser", user_otp):
                    break  # Exit loop on successful login
            else:
                print("Invalid input. Please enter a 6-digit numeric OTP.")
        else:
            print("Max attempts reached. Please try again later.")
