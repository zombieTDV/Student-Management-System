# models/student.py
from models.database import db
from datetime import datetime
from bson import ObjectId  # Rất quan trọng để làm việc với _id

class Student:
    def __init__(self):
        """
        Khởi tạo đối tượng quản lý collection 'students'
        """
        self.collection = db.get_db()["students"]

    def create_indexes(self):
        """
        Tạo các index để tối ưu truy vấn
        """
        # account_id phải là duy nhất, vì 1 account chỉ link tới 1 student
        self.collection.create_index("account_id", unique=True)
        # Các trường thường xuyên tìm kiếm
        self.collection.create_index("major")
        self.collection.create_index("fullName")

    def create(self, account_id, fullName, dob, gender, address, contactPhone, major, imageURL=None):
        """
        Tạo một hồ sơ sinh viên mới.
        Hàm này sẽ được gọi bởi Controller.
        """
        try:
            student_document = {
                # Lưu account_id dưới dạng ObjectId để tham chiếu
                "account_id": ObjectId(account_id),  
                "fullName": fullName,
                "dob": dob,  # Nên là đối tượng datetime
                "gender": gender,
                "address": address,
                "contactPhone": contactPhone,
                "major": major,
                "imageURL": imageURL,
                "createdAt": datetime.now(),
                "is_deleted": False,  # Dùng cho soft delete
                "fees": []  # Mảng rỗng để chứa các khoản phí (embedded)
            }
            
            result = self.collection.insert_one(student_document)
            return str(result.inserted_id)

        except Exception as e:
            print(f"Error creating student: {e}")
            return None

    def _format_student(self, student):
        """
        Hàm helper để chuyển đổi ObjectId sang string cho an toàn
        """
        if student:
            student["_id"] = str(student["_id"])
            if "account_id" in student:
                student["account_id"] = str(student["account_id"])
            # Bạn cũng có thể convert các ObjectId bên trong 'fees' nếu cần
        return student

    def get_by_id(self, student_id):
        """
        Lấy sinh viên bằng _id (dạng string)
        """
        try:
            query = {"_id": ObjectId(student_id), "is_deleted": False}
            student = self.collection.find_one(query)
            return self._format_student(student)
        except Exception:
            return None

    def get_by_account_id(self, account_id):
        """
        Lấy sinh viên bằng account_id (dạng string)
        """
        try:
            query = {"account_id": ObjectId(account_id), "is_deleted": False}
            student = self.collection.find_one(query)
            return self._format_student(student)
        except Exception:
            return None

    def get_all(self, major_filter=None):
        """
        Lấy tất cả sinh viên (chưa bị xóa)
        """
        query = {"is_deleted": False}
        if major_filter:
            query["major"] = major_filter

        students = self.collection.find(query)
        return [self._format_student(student) for student in students]

    def update_profile(self, student_id, update_data):
        """
        Cập nhật thông tin cơ bản cho sinh viên.
        'update_data' là một dict, ví dụ: {"address": "...", "contactPhone": "..."}
        """
        try:
            self.collection.update_one(
                {"_id": ObjectId(student_id), "is_deleted": False},
                {"$set": update_data}
            )
            return True
        except Exception as e:
            print(f"Error updating student profile: {e}")
            return False

    def soft_delete(self, student_id):
        """
        Thực hiện xóa mềm (soft delete)
        """
        return self.update_profile(student_id, {"is_deleted": True})

    # --- Quản lý Fees (Embedded Document) ---

    def add_fee(self, student_id, description, amount, dueDate, period):
        """
        Thêm một khoản phí mới vào mảng 'fees' của sinh viên
        """
        try:
            # Tự tạo ObjectId cho document nhúng để dễ dàng truy vấn sau này
            fee_id = ObjectId()
            new_fee = {
                "_id": fee_id,
                "feeID": str(fee_id), # Có thể dùng _id làm feeID
                "description": description,
                "amount": amount,
                "status": "pending",
                "dueDate": dueDate, # Nên là datetime
                "period": period,
                "createdAt": datetime.now(),
                "transactions": [] # Sẵn sàng để chứa transactions
            }

            self.collection.update_one(
                {"_id": ObjectId(student_id)},
                {"$push": {"fees": new_fee}}
            )
            return str(fee_id) # Trả về ID của khoản phí vừa tạo

        except Exception as e:
            print(f"Error adding fee: {e}")
            return None

    def update_fee_status(self, student_id, fee_id, new_status):
        """
        Cập nhật trạng thái của một khoản phí (ví dụ: 'pending' -> 'paid')
        """
        try:
            # Sử dụng positional operator '$' để cập nhật đúng document trong mảng
            result = self.collection.update_one(
                {"_id": ObjectId(student_id), "fees._id": ObjectId(fee_id)},
                {"$set": {"fees.$.status": new_status}}
            )
            return result.matched_count > 0
        except Exception as e:
            print(f"Error updating fee status: {e}")
            return False
    
    def add_transaction_to_fee(self, student_id, fee_id, transaction_data):
        """
        Thêm một giao dịch vào một khoản phí cụ thể
        'transaction_data' là một dict (amount, method, date...)
        """
        try:
            # Gán ID cho transaction
            transaction_data["_id"] = ObjectId()
            transaction_data["transactionID"] = str(transaction_data["_id"])
            transaction_data["date"] = transaction_data.get("date", datetime.now())

            result = self.collection.update_one(
                {"_id": ObjectId(student_id), "fees._id": ObjectId(fee_id)},
                {"$push": {"fees.$.transactions": transaction_data}}
            )
            return str(transaction_data["_id"]) if result.matched_count > 0 else None
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return None