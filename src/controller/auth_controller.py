from models.account import Account

class AuthController:
    def __init__(self):
        self.account_model = Account()
        self.current_user = None
    
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
    
    def recover_password(self, email):
        """Handle password recovery"""
        user = self.account_model.get_by_email(email)
        if user:
            # TODO: Send recovery email
            return {"success": True, "message": "Recovery email sent"}
        else:
            return {"success": False, "message": "Email not found"}
    
    def is_authenticated(self):
        """Check if user is logged in"""
        return self.current_account is not None