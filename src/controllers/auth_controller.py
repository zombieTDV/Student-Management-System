import os
import json
import uuid
import time
from models.account import Account

TOKEN_FILE = ".token.json"  # file lưu token trên máy
TOKEN_LIFETIME = 120  # 2 phút = 120 giây


class AuthController:
    def __init__(self):
        # Note: keep this as before if your Account ctor requires fields
        self.account_model = Account(username="", email="", role="", password="123")
        self.current_account = None

    def _save_token(self, account):
        """Save token + account_id + expiry (overwrite existing)."""
        token_data = {
            "token": str(uuid.uuid4()),
            "account_id": str(account._id),
            "expiry": time.time() + TOKEN_LIFETIME,
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        return token_data

    def _load_token(self):
        """Return token_data if exists and valid, else remove it and return None."""
        if not os.path.exists(TOKEN_FILE):
            return None
        try:
            with open(TOKEN_FILE, "r") as f:
                token_data = json.load(f)
            if time.time() < token_data.get("expiry", 0):
                return token_data
            # expired -> remove and return None
            try:
                os.remove(TOKEN_FILE)
            except OSError:
                pass
            return None
        except Exception:
            # malformed -> remove and return None
            try:
                os.remove(TOKEN_FILE)
            except OSError:
                pass
            return None

    def logout(self):
        """Clear session and remove token file."""
        self.current_account = None
        try:
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
        except Exception:
            pass

    def login(self, username=None, password=None):
        """
        Login logic (credential-first, then fallback to token):
        - If username and password are provided (non-empty), try to authenticate them.
          If success: set current_account, overwrite token to that account_id, return user as before.
        - If credentials not provided or blank, try token auto-login.
        """
        # Normalize empty strings to None for clarity
        if username is not None and username == "":
            username = None
        if password is not None and password == "":
            password = None

        # 1) If credentials provided -> try authenticate them first
        if username and password:
            account = self.account_model.authenticate(username, password)
            if account:
                self.current_account = account
                # overwrite token for this account
                try:
                    self._save_token(account)
                except Exception:
                    # token saving shouldn't block login; ignore errors
                    pass
                return {
                    "success": True,
                    "message": "Login successful",
                    "user": account,
                    "auto_login": False,
                }
            else:
                return {"success": False, "message": "Invalid credentials"}

        # 2) No credentials provided -> attempt token-based auto-login
        token_data = self._load_token()
        if token_data:
            account_id = token_data.get("account_id")
            # Try to fetch real account from DB
            account = Account.find_by_id(account_id)
            if account:
                self.current_account = account
                return {
                    "success": True,
                    "message": f"Auto-login successful for {account.username}",
                    "user": account,
                    "auto_login": True,
                }
            else:
                # invalid token (account deleted) -> ensure token removed and require login
                try:
                    os.remove(TOKEN_FILE)
                except Exception:
                    pass
                return {
                    "success": False,
                    "message": "Auto-login failed, please sign in.",
                }

        # 3) No credentials and no valid token
        return {"success": False, "message": "Username and password required"}

    def is_authenticated(self):
        return self.current_account is not None
