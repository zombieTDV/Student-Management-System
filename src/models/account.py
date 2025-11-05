from models.database import db
import hashlib
from datetime import datetime
from bson import ObjectId

# 2. Lấy CSDL thực sự bằng cách gọi phương thức .get_db()
# _db này là kết nối CSDL (tương đương với client[MONGO_DB])
_db = db.get_db() 

class Account:
    """
    Lớp Cha (Base Class) cho tất cả các loại tài khoản.
    Quản lý collection 'users'.
    """
    
    # 3. Sử dụng _db để trỏ tới collection
    collection = _db["users"] 

    def __init__(self, username, email, role, _id=None, accountID=None, created_at=None, **kwargs):
        self._id = _id
        self.username = username
        self.email = email
        self.role = role
        self.accountID = accountID
        self.created_at = created_at or datetime.now()
        # **kwargs sẽ chứa các trường khác từ CSDL

    @staticmethod
    def _hash_password(password):
        """Hàm static để hash password"""
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def authenticate(cls, username, password):
        """
        Logic cho hàm 'login()'.
        """
        password_hash = cls._hash_password(password)
        doc = cls.collection.find_one(
            {"username": username, "password_hash": password_hash}
        )

        if doc:
            cls.collection.update_one(
                {"_id": doc["_id"]}, {"$set": {"last_login": datetime.now()}}
            )
            return cls.build_object_from_doc(doc)
        
        return None

    @classmethod
    def find_by_username(cls, username):
        doc = cls.collection.find_one({"username": username})
        return cls.build_object_from_doc(doc)

    @classmethod
    def find_by_id(cls, user_id):
        try:
            doc = cls.collection.find_one({"_id": ObjectId(user_id)})
            return cls.build_object_from_doc(doc)
        except Exception:
            return None # Nếu user_id không phải ObjectId hợp lệ

    @classmethod
    def build_object_from_doc(cls, doc):
        """
        Quyết định tạo object Admin hay Student dựa trên 'role'
        """
        if not doc:
            return None
        
        # Import BÊN TRONG hàm để tránh lỗi Circular Import
        from models.admin import Admin
        from models.student import Student

        if doc.get("role") == "admin":
            return Admin(**doc)
        elif doc.get("role") == "student":
            return Student(**doc)
        
        return None

    def update_password(self, new_password):
        """
        Cập nhật password cho chính user này
        """
        if not self._id:
            raise ValueError("Không thể cập nhật password cho user chưa được lưu")
            
        new_hash = self._hash_password(new_password)
        self.collection.update_one(
            {"_id": self._id},
            {"$set": {"password_hash": new_hash}}
        )