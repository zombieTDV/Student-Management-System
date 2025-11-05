# models/admin.py
from models.account import Account # Import lớp Cha
from datetime import datetime

class Admin(Account):
    def __init__(self, createdAt=None, **kwargs):
        """
        Khởi tạo Admin.
        **kwargs sẽ chứa các trường của Account (username, email...)
        """
        # Gán cứng role='admin' và gọi hàm __init__ của Cha
        super().__init__(role="admin", **kwargs)
        
        # Thuộc tính riêng của Admin từ sơ đồ
        self.createdAt = createdAt or self.created_at 

    def to_doc(self):
        """
        Chuyển object Admin thành 1 document để lưu vào DB
        """
        return {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "accountID": self.accountID,
            "createdAt": self.createdAt
        }

    @classmethod
    def create_admin(cls, username, email, password, accountID):
        """
        Hàm Model để TẠO MỚI một admin trong CSDL
        """
        password_hash = cls._hash_password(password)
        admin_doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": "admin",
            "accountID": accountID,
            "createdAt": datetime.now(),
            "last_login": None
        }
        try:
            # Dùng 'cls.collection' kế thừa từ Account
            result = cls.collection.insert_one(admin_doc)
            admin_doc["_id"] = result.inserted_id
            return Admin(**admin_doc) # Trả về 1 đối tượng Admin
        except Exception as e:
            print(f"Error creating admin: {e}")
            return None