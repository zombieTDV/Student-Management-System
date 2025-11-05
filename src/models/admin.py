from datetime import datetime
from typing import Dict


class Admin:
    """
    Model class đại diện cho Admin trong hệ thống
    Chứa các thuộc tính và phương thức xử lý nghiệp vụ liên quan đến Admin
    """

    def __init__(self, db_connection):
        """
        Khởi tạo Admin model với kết nối database

        Args:
            db_connection: MongoDB database connection
        """
        self.db = db_connection
        self.collection = self.db["admins"]

    def create_admin(self, username: str, password: str, email: str) -> Dict:
        """
        Tạo mới một admin account

        Args:
            username: Tên đăng nhập
            password: Mật khẩu (đã được hash)
            email: Email admin

        Returns:
            Dict chứa thông tin admin vừa tạo
        """
        admin_data = {
            "username": username,
            "password": password,
            "email": email,
            "role": "admin",
            "createAt": datetime.now(),
        }

        result = self.collection.insert_one(admin_data)
        admin_data["_id"] = result.inserted_id

        return admin_data
