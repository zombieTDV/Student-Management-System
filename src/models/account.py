# models/user.py
from models.database import db
import hashlib
from datetime import datetime

class Account:
    def __init__(self):
        self.collection = db.get_db()['users']
    
    def create_indexes(self):
        """Create unique indexes"""
        self.collection.create_index("username", unique=True)
        self.collection.create_index("email", unique=True)
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, email, password):
        """Create new user"""
        try:
            user = {
                "username": username,
                "email": email,
                "password_hash": self.hash_password(password),
                "created_at": datetime.now(),
                "last_login": None
            }
            
            result = self.collection.insert_one(user)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def authenticate(self, username, password):
        """Authenticate user"""
        password_hash = self.hash_password(password)
        
        user = self.collection.find_one({
            "username": username,
            "password_hash": password_hash
        })
        
        if user:
            # Update last login
            self.collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.now()}}
            )
            
            # Convert ObjectId to string
            user['_id'] = str(user['_id'])
            # Remove password hash from returned data
            del user['password_hash']
            
            return user
        
        return None
    
    def get_by_email(self, email):
        """Get user by email"""
        user = self.collection.find_one({"email": email})
        
        if user:
            user['_id'] = str(user['_id'])
            if 'password_hash' in user:
                del user['password_hash']
        
        return user
    
    def get_by_username(self, username):
        """Get user by username"""
        user = self.collection.find_one({"username": username})
        
        if user:
            user['_id'] = str(user['_id'])
            if 'password_hash' in user:
                del user['password_hash']
        
        return user
    
    def update_password(self, email, new_password):
        """Update user password"""
        try:
            self.collection.update_one(
                {"email": email},
                {"$set": {"password_hash": self.hash_password(new_password)}}
            )
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False