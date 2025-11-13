from models.database import db
from bson.objectid import ObjectId
import datetime
import hashlib
import os

# Load collection once
try:
    ACCOUNTS_COLLECTION = db.get_db()["accounts"]
except Exception as e:
    print(f"Error connecting to 'accounts' collection: {e}")
    exit(1)


def hash_password(password):
    """Hash password securely with salt using hashlib.SHA256"""
    salt = os.urandom(16).hex()
    hashed_password = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${hashed_password}"


def safe_compare(a, b):
    """Safe string comparison to prevent timing attacks."""
    try:
        a_bytes = a.encode("utf-8")
        b_bytes = b.encode("utf-8")
    except AttributeError:
        return False

    if len(a_bytes) != len(b_bytes):
        return False

    result = 0
    for x, y in zip(a_bytes, b_bytes):
        result |= x ^ y
    return result == 0


def check_password(password, stored_hash):
    """Check if password matches stored hash"""
    try:
        salt, hash_key = stored_hash.split("$")
        password_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return safe_compare(password_hash, hash_key)
    except Exception as e:
        print(f"Error checking password: {e}")
        return False


class Account:
    """Base class for all account types (Admin, Student)"""

    def __init__(
        self, username, email, role, password=None, _id=None, createAt=None, **kwargs
    ):
        self._id = _id
        self.username = username
        self.email = email
        self.role = role

        # Assign other attributes from child classes
        for key, value in kwargs.items():
            if key not in ("password_hash"):
                setattr(self, key, value)

        # Handle password
        if password:
            self.password_hash = hash_password(password)
        elif _id is None:
            raise ValueError("Password is required when creating new account.")
        else:
            if not hasattr(self, "password_hash"):
                account_data = ACCOUNTS_COLLECTION.find_one({"_id": self._id})
                self.password_hash = account_data.get("password_hash")

        self.createAt = createAt or datetime.datetime.utcnow()

    def save(self):
        """Save or update account data to 'accounts' collection"""
        account_data = vars(self).copy()

        if self._id is None:
            account_data.pop("_id", None)

        if self._id:
            # Update
            ACCOUNTS_COLLECTION.update_one({"_id": self._id}, {"$set": account_data})
        else:
            # Insert new
            account_data.pop("password", None)
            result = ACCOUNTS_COLLECTION.insert_one(account_data)
            self._id = result.inserted_id
        return self._id

    @classmethod
    def find_by_username(cls, username):
        """Find account by username."""
        account_data = ACCOUNTS_COLLECTION.find_one({"username": username})
        if account_data:
            return cls._instantiate_correct_class(account_data)
        return None

    @classmethod
    def find_by_id(cls, account_id):
        """Find account by ID."""
        try:
            account_data = ACCOUNTS_COLLECTION.find_one({"_id": ObjectId(account_id)})
            if account_data:
                return cls._instantiate_correct_class(account_data)
            return None
        except Exception as e:
            print(f"Error finding by ID: {e}")
            return None

    @classmethod
    def find_by_email(cls, email):
        """Find account by email - MODEL ONLY FINDS DATA"""
        account_data = ACCOUNTS_COLLECTION.find_one({"email": email})
        if account_data:
            return cls._instantiate_correct_class(account_data)
        return None

    @classmethod
    def find_all_by_role(cls, role):
        """
        Find all accounts by role (e.g., 'student', 'admin')

        Args:
            role (str): The role to filter by ('student' or 'admin')

        Returns:
            list: List of Account objects (Student or Admin instances)
        """
        try:
            accounts_data = ACCOUNTS_COLLECTION.find({"role": role})
            accounts = []

            for account_data in accounts_data:
                account = cls._instantiate_correct_class(account_data)
                accounts.append(account)

            return accounts
        except Exception as e:
            print(f"Error finding accounts by role: {e}")
            return []

    @classmethod
    def find_all_students(cls):
        """
        Convenience method to find all student accounts.

        Returns:
            list: List of Student objects
        """
        return cls.find_all_by_role("student")

    @classmethod
    def find_all_admins(cls):
        """
        Convenience method to find all admin accounts.

        Returns:
            list: List of Admin objects
        """
        return cls.find_all_by_role("admin")

    @classmethod
    def count_by_role(cls, role):
        """
        Count accounts by role.

        Args:
            role (str): The role to count

        Returns:
            int: Number of accounts with that role
        """
        try:
            return ACCOUNTS_COLLECTION.count_documents({"role": role})
        except Exception as e:
            print(f"Error counting accounts: {e}")
            return 0

    def delete(self):
        """
        Delete this account from database.

        Returns:
            bool: True if deleted successfully
        """
        try:
            if self._id:
                result = ACCOUNTS_COLLECTION.delete_one({"_id": self._id})
                return result.deleted_count > 0
            return False
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False

    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user and return object (Student or Admin)"""
        account = cls.find_by_username(username)

        if account and check_password(password, account.password_hash):
            return account

        return None

    def update_password(self, new_password):
        """Update password for account (instance method)"""
        self.password_hash = hash_password(new_password)
        ACCOUNTS_COLLECTION.update_one(
            {"_id": self._id}, {"$set": {"password_hash": self.password_hash}}
        )
        print(f"Password updated for {self.username}")
        return True

    @staticmethod
    def _instantiate_correct_class(account_data):
        """
        Helper function: Decide whether to instantiate Student or Admin
        based on 'role' field.
        """
        role = account_data.get("role")

        from models.student import Student
        from models.admin import Admin

        if role == "student":
            return Student(**account_data)
        elif role == "admin":
            return Admin(**account_data)
        else:
            return Account(**account_data)

    def __repr__(self):
        return f"<{self.role.capitalize()} {self.username} ({self._id})>"
