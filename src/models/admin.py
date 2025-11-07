# models/admin.py
from models.account import Account,hash_password, ACCOUNTS_COLLECTION
from models.student import Student
from models.database import db
from bson.objectid import ObjectId
import datetime


class Admin(Account):
    
    def __init__(self, **kwargs):
        """
        Khởi tạo Admin.
        """
        kwargs.pop('role', None)
        super().__init__(role='admin', **kwargs)

    # --- Các phương thức từ UML (giờ là instance methods) ---

    def createStudent(self, student_profile, account_profile):
            """
            Tạo một Sinh viên mới.
            'student_profile': dict (fullName, dob, v.v.)
            'account_profile': dict (username, password, email)
            """
            
            # Gộp cả hai dict lại
            full_profile = {**student_profile, **account_profile}
            
            try:
                # Kiểm tra username/email đã tồn tại chưa
                if Account.find_by_username(full_profile['username']):
                    raise ValueError("Username đã tồn tại.")

                # --- SỬA DÒNG NÀY ---
                # Thay vì self.get_collection(), dùng ACCOUNTS_COLLECTION
                if ACCOUNTS_COLLECTION.find_one({'email': full_profile['email']}):
                    raise ValueError("Email đã tồn tại.")
                # --- KẾT THÚC SỬA ---
                    
                # Tạo đối tượng Student
                # Mật khẩu sẽ được hash tự động bởi Account.__init__
                new_student = Student(**full_profile)
                
                # Lưu vào DB
                new_student.save()
                
                print(f"Admin {self.username} đã tạo sinh viên {new_student.username}.")
                return new_student
                
            except Exception as e:
                print(f"Lỗi khi tạo sinh viên: {e}")
                return None

    def editStudent(self, student_id, update_data):
        """
        Chỉnh sửa thông tin của một sinh viên.
        """
        student = Account.find_by_id(student_id)
        if not student or student.role != "student":
            print(f"Không tìm thấy sinh viên với ID: {student_id}")
            return False

        # Sử dụng phương thức của chính lớp Student
        success = student.updateProfile(update_data)
        return success

    def softDeleteStudent(self, student_id):
        """
        "Xóa mềm" một sinh viên (đánh dấu tài khoản là không hoạt động).
        Giả sử chúng ta thêm trường 'is_active'.
        """
        student = Account.find_by_id(student_id)
        if not student or student.role != "student":
            print(f"Không tìm thấy sinh viên với ID: {student_id}")
            return False

        # Thêm/cập nhật trường 'is_active'
        setattr(student, "is_active", False)
        student.save()

        print(f"Đã vô hiệu hóa tài khoản cho sinh viên: {student.username}")
        return True

    def postAnnouncement(self, title, content):
        """
        Đăng một thông báo mới.
        """
        announcements_collection = db.get_db()["announcements"]
        announcement_data = {
            "title": title,
            "content": content,
            "createBy": self._id,  # ID của admin đã đăng
            "createAt": datetime.datetime.utcnow(),
        }
        result = announcements_collection.insert_one(announcement_data)
        print(f"Admin {self.username} đã đăng thông báo '{title}'")
        return result.inserted_id

    def editPayment(self, fee_id, new_status, amount_paid=None):
        """
        Chỉnh sửa một khoản thanh toán (Fee).
        """
        fees_collection = db.get_db()["fees"]

        try:
            fee = fees_collection.find_one({"_id": ObjectId(fee_id)})
            if not fee:
                print(f"Không tìm thấy bản ghi học phí: {fee_id}")
                return False

            update_doc = {"status": new_status}

            # Nếu đánh dấu là 'paid', hãy tạo một Giao dịch (Transaction)
            if new_status == "paid" and amount_paid is not None:
                transactions_collection = db.get_db()["transactions"]
                transaction_data = {
                    "amount": amount_paid,
                    "status": "completed",
                    "method": "admin_entry",
                    "date": datetime.datetime.utcnow(),
                    "fee_id": ObjectId(fee_id),
                    "student_id": fee["student_id"],
                }
                transactions_collection.insert_one(transaction_data)
                print(f"Đã tạo giao dịch cho học phí {fee_id}")

            # Cập nhật trạng thái học phí
            fees_collection.update_one({"_id": ObjectId(fee_id)}, {"$set": update_doc})
            print(f"Admin {self.username} đã cập nhật học phí {fee_id}")
            return True

        except Exception as e:
            print(f"Lỗi khi chỉnh sửa thanh toán: {e}")
            return False
