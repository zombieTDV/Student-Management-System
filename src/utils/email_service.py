import ssl
import smtplib
from email.message import EmailMessage
import secrets
import string
from bson.objectid import ObjectId

from models.database import db

# Load collection once
try:
    CONFIG_COLLECTION = db.get_db()["config"]
except Exception as e:
    print(f"Error connecting to 'config' collection: {e}")
    exit(1)


def generate_random_password(length=6):
    """Generate secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for i in range(length))


def send_password_reset_email(email, username, new_password):
    """
    Send email containing new password to user.

    Returns:
        dict: {"success": bool, "message": str}
    """
    email_id = "691128287956cc411169ab56"
    email_account_data = CONFIG_COLLECTION.find_one({"_id": ObjectId(email_id)})

    EMAIL_USER = email_account_data.get("email")
    EMAIL_PASSWORD = email_account_data.get("password")  # Must be App Password

    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("\n*** WARNING: EMAIL_USER or EMAIL_PASSWORD not set in .env.")
        print(f"*** Email not sent to {email}.")
        print(f"*** New password (for testing): {new_password}\n")
        return {
            "success": False,
            "message": "Email configuration not set. Password not sent.",
            "password": new_password,  # For testing only
        }

    # Create email content
    msg = EmailMessage()
    msg.set_content(
        f"""
Hello {username},

Your password reset request has been processed.
Your new password is: {new_password}

Please login and do not share this password with anyone.

Best regards,
Student Management System
    """
    )
    msg["Subject"] = "New Password for Student Management System"
    msg["From"] = EMAIL_USER
    msg["To"] = email

    try:
        # Send email via Gmail (using SSL)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"New password sent to {email}")
        return {"success": True, "message": f"New password sent to {email}"}
    except Exception as e:
        print(f"ERROR sending email: {e}")
        print(f"New password (NOT SENT): {new_password}")
        return {
            "success": False,
            "message": f"Failed to send email: {str(e)}",
            "password": new_password,  # For debugging
        }
