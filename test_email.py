import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText

# === 1. Initialize Firebase Admin SDK ===
cred = credentials.Certificate('wevolt-4d8a8-2e9079117595.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

# === 2. Fetch the first user from 'sorted_users' ===
def get_first_sorted_user():
    users_ref = db.collection('sorted_users')
    users = users_ref.limit(1).get()  # Get first document
    if users:
        user_data = users[0].to_dict()
        print(f"✅ First user fetched: {user_data}")
        return user_data
    else:
        print("🚫 No users found in 'sorted_users' collection.")
        return None

# === 3. Send an email to the user via Outlook ===
def send_email_outlook(email, hrs, username):
    
    subject = "WeVolt Notification"
    body = f"""
    Hi {username},

    This is a notification from WeVolt. 
    Wevolt charged your car for {hrs} hrs and your final bill is {hrs*10} $. 
    Thank you for being part of our platform!

    Best regards,
    WeVolt Team
    """

    # Outlook account details
    sender_email = "vanessahanna03@gmail.com"  # 🔥 Replace this
    sender_password = "mhpz cbqa mclp itbb"         # 🔥 Replace this

    try:
        # Create email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = f"WeVolt Team <{sender_email}>"
        msg['To'] = email

        # Connect to Outlook SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {email}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# === 4. Main execution ===
if __name__ == "__main__":
    user = get_first_sorted_user()
    if user:
        send_email_outlook(user["email"],user["duration"],user["username"])
