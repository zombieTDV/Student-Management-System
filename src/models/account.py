# models/account.py
import hashlib
from datetime import datetime


class Account:
    def __init__(self):
        pass

    def create_indexes(self):
        """Create unique indexes"""
        self.collection.create_index("accountname", unique=True)
        self.collection.create_index("email", unique=True)

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_account(self, accountname, email, password):
        """Create new account"""
        try:
            account = {
                "accountname": accountname,
                "email": email,
                "password_hash": self.hash_password(password),
                "created_at": datetime.now(),
                "last_login": None,
            }

            result = self.collection.insert_one(account)
            return str(result.inserted_id)

        except Exception as e:
            print(f"Error creating account: {e}")
            return None

    def authenticate(self, accountname, password):
        """Authenticate account"""
        password_hash = self.hash_password(password)
        account = self.collection.find_one(
            {"accountname": accountname, "password_hash": password_hash}
        )

        if account:
            # Update last login
            self.collection.update_one(
                {"_id": account["_id"]}, {"$set": {"last_login": datetime.now()}}
            )

            # Convert ObjectId to string
            account["_id"] = str(account["_id"])
            # Remove password hash from returned data
            del account["password_hash"]
            print(account)
            return account

        return None

    def get_by_email(self, email):
        """Get account by email"""
        account = self.collection.find_one({"email": email})

        if account:
            account["_id"] = str(account["_id"])
            if "password_hash" in account:
                del account["password_hash"]

        return account

    def get_by_accountname(self, accountname):
        """Get account by accountname"""
        account = self.collection.find_one({"accountname": accountname})

        if account:
            account["_id"] = str(account["_id"])
            if "password_hash" in account:
                del account["password_hash"]

        return account

    def update_password(self, accountname, new_password):
        """Update account password"""
        try:
            self.collection.update_one(
                {"accountname": accountname},
                {"$set": {"password_hash": self.hash_password(new_password)}},
            )
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False


# a = Account()
# a.create_account("sv", "sv@", "sv123")
# print(a.authenticate("admin", "admin123"))

# print(a.hash_password("admin123"))
