from datetime import datetime
from typing import Optional, Dict
from bson.objectid import ObjectId


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

    def createStudent(self, student_data: Dict) -> bool:
        """
        Tạo mới sinh viên (Theo Class Diagram)

        Args:
            student_data: Dictionary chứa thông tin sinh viên
                - username: string
                - password: string (đã hash)
                - email: string
                - fullName: string
                - dob: Date
                - gender: string
                - address: string
                - contact: string (phone)
                - major: string
                - imageURL: string (optional)

        Returns:
            True nếu tạo thành công, False nếu thất bại
        """
        try:
            students_collection = self.db["students"]

            # Thêm thông tin mặc định
            student_data["createAt"] = datetime.now()
            student_data["role"] = "student"

            result = students_collection.insert_one(student_data)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Error creating student: {e}")
            return False

    def editStudent(self, student_id: str, updated_data: Dict) -> bool:
        """
        Chỉnh sửa thông tin sinh viên (Theo Class Diagram)

        Args:
            student_id: ID của sinh viên cần sửa (ObjectId hoặc accountID)
            updated_data: Dictionary chứa dữ liệu cập nhật
                - Có thể cập nhật: fullName, dob, gender, address,
                  contact, major, imageURL, email

        Returns:
            True nếu cập nhật thành công, False nếu thất bại
        """
        try:
            students_collection = self.db["students"]

            # Thử tìm theo ObjectId trước
            try:
                query = {"_id": ObjectId(student_id)}
            except Exception:
                # Nếu không phải ObjectId, tìm theo accountID
                query = {"accountID": student_id}

            result = students_collection.update_one(query, {"$set": updated_data})

            return result.modified_count > 0
        except Exception as e:
            print(f"Error editing student: {e}")
            return False

    def softDeleteStudent(self, student_id: str) -> bool:
        """
        Xóa mềm sinh viên (Theo Class Diagram)
        Đánh dấu sinh viên là đã xóa, không xóa khỏi database

        Args:
            student_id: ID của sinh viên cần xóa

        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        try:
            students_collection = self.db["students"]

            # Thử tìm theo ObjectId trước
            try:
                query = {"_id": ObjectId(student_id)}
            except Exception:
                # Nếu không phải ObjectId, tìm theo accountID
                query = {"accountID": student_id}

            result = students_collection.update_one(
                query, {"$set": {"isDeleted": True, "deletedAt": datetime.now()}}
            )

            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False

    def postAnnouncement(self, announcement_data: Dict) -> bool:
        """
        Đăng thông báo mới (Theo Class Diagram)

        Args:
            announcement_data: Dictionary chứa thông tin thông báo
                - title: string (tiêu đề)
                - content: string (nội dung)
                - accountID: string (ID của admin tạo, optional)

        Returns:
            True nếu đăng thành công, False nếu thất bại
        """
        try:
            announcements_collection = self.db["announcements"]

            # Thêm thông tin người tạo và thời gian
            announcement_data["createBy"] = self.username or "admin"
            announcement_data["createAt"] = datetime.now()

            # Nếu có accountID của admin hiện tại, thêm vào
            if self.accountID:
                announcement_data["accountID"] = self.accountID

            result = announcements_collection.insert_one(announcement_data)
            return result.inserted_id is not None
        except Exception as e:
            print(f"Error posting announcement: {e}")
            return False

    def editPayment(self, payment_id: str, updated_data: Dict) -> bool:
        """
        Chỉnh sửa thông tin thanh toán (Theo Class Diagram)

        Args:
            payment_id: ID của giao dịch thanh toán (Transaction)
            updated_data: Dictionary chứa dữ liệu cập nhật
                - Có thể cập nhật: amount, status, method, date

        Returns:
            True nếu cập nhật thành công, False nếu thất bại
        """
        try:
            transactions_collection = self.db["transactions"]

            # Thử tìm theo ObjectId
            try:
                query = {"_id": ObjectId(payment_id)}
            except Exception:
                # Nếu không phải ObjectId, tìm theo transactionID
                query = {"transactionID": payment_id}

            result = transactions_collection.update_one(query, {"$set": updated_data})

            return result.modified_count > 0
        except Exception as e:
            print(f"Error editing payment: {e}")
            return False

    @staticmethod
    def authenticate(db_connection, username: str, password: str) -> Optional["Admin"]:
        """
        Xác thực đăng nhập admin
        (Không có trong Class Diagram nhưng cần thiết cho chức năng đăng nhập)

        Args:
            db_connection: MongoDB database connection
            username: Tên đăng nhập
            password: Mật khẩu (đã hash)

        Returns:
            Admin object nếu xác thực thành công, None nếu thất bại
        """
        try:
            admins_collection = db_connection["admins"]
            admin_data = admins_collection.find_one(
                {"username": username, "password": password}
            )

            if admin_data:
                admin = Admin(db_connection)
                admin.accountID = str(admin_data["_id"])
                admin.username = admin_data["username"]
                admin.email = admin_data.get("email")
                admin.role = admin_data.get("role", "admin")
                admin.createAt = admin_data.get("createAt")
                return admin

            return None
        except Exception as e:
            print(f"Error authenticating admin: {e}")
            return None

    def to_dict(self) -> Dict:
        """
        Chuyển đối tượng Admin thành dictionary

        Returns:
            Dictionary chứa thông tin admin
        """
        return {
            "accountID": self.accountID,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "createAt": self.createAt,
        }
