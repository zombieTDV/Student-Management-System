from models.account import Account
from utils.email_service import generate_random_password, send_password_reset_email


class AuthController:
    def __init__(self):
        self.account_model = Account(username="", email="", role="", password="123")
        self.current_account = None

    def login(self, username, password):
        """Handle login logic"""
        if not username or not password:
            return {"success": False, "message": "Username and password required"}

        account = self.account_model.authenticate(username, password)
        if account:
            self.current_account = account
            return {"success": True, "message": "Login successful", "user": account}
        else:
            return {"success": False, "message": "Invalid credentials"}

    def logout(self):
        """Handle logout"""
        self.current_account = None

    def is_authenticated(self):
        """Check if user is logged in"""
        return self.current_account is not None

    def recover_password(self, email):
        """
        Handle password recovery - Complete flow:
        1) User enters email
        2) Find email in database and get account
        3) If email exists, generate new password, update DB, and send email
        """
        if not email:
            return {"success": False, "message": "Email is required"}

        account = Account.find_by_email(email)

        if not account:
            return {"success": False, "message": "Email not found in system"}

        try:
            new_password = generate_random_password()
            account.update_password(new_password)

            email_result = send_password_reset_email(
                email=account.email,
                username=account.username,
                new_password=new_password,
            )

            if email_result["success"]:
                return {
                    "success": True,
                    "message": f"New password has been sent to {email}",
                }
            else:
                return {
                    "success": False,
                    "message": email_result["message"],
                    "note": "Password was updated but email failed to send",
                }

        except Exception as e:
            print(f"Error in password recovery: {e}")
            return {"success": False, "message": f"Password recovery failed: {str(e)}"}
