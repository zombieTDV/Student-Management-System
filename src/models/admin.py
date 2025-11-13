from models.account import Account, ACCOUNTS_COLLECTION
from models.student import Student
from models.database import db
from bson.objectid import ObjectId
from models.announcement import Announcement
from models.fee import Fee
from models.transaction import Transaction

FEES_COLLECTION = db.get_db()["fees"]
TRANSACTIONS_COLLECTION = db.get_db()["transactions"]


class Admin(Account):
    def __init__(self, **kwargs):
        """
        Khởi tạo Admin.
        """
        kwargs.pop("role", None)
        super().__init__(role="admin", **kwargs)

    def createStudent(self, student_profile, account_profile):
        """
        Tạo một Sinh viên mới.
        """
        full_profile = {**student_profile, **account_profile}

        try:
            if Account.find_by_username(full_profile["username"]):
                raise ValueError("Username đã tồn tại.")
            if ACCOUNTS_COLLECTION.find_one({"email": full_profile["email"]}):
                raise ValueError("Email đã tồn tại.")

            new_student = Student(**full_profile)
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
        return student.updateProfile(update_data)

    def softDeleteStudent(self, student_id):
        """
        "Xóa mềm" một sinh viên (đánh dấu tài khoản là không hoạt động).
        """
        student = Account.find_by_id(student_id)
        if not student or student.role != "student":
            print(f"Không tìm thấy sinh viên với ID: {student_id}")
            return False

        setattr(student, "is_active", False)
        student.save()

        print(f"Đã vô hiệu hóa tài khoản cho sinh viên: {student.username}")
        return True

    def hardDeleteStudent(self, student_id):
        """
        XÓA VĨNH VIỄN (Hard Delete) một sinh viên và TẤT CẢ dữ liệu liên quan.
        Hành động này không thể hoàn tác.
        """
        print(
            f"\n--- CẢNH BÁO: Admin {self.username} đang xóa vĩnh viễn SV {student_id} ---"
        )

        try:
            # 1. Biến student_id thành ObjectId nếu cần
            if not isinstance(student_id, ObjectId):
                student_id = ObjectId(student_id)

            # 2. Xóa tài khoản sinh viên khỏi 'accounts'
            delete_result = ACCOUNTS_COLLECTION.delete_one(
                {"_id": student_id, "role": "student"}
            )

            if delete_result.deleted_count == 0:
                print(f"Không tìm thấy sinh viên (ID: {student_id}) để xóa.")
                return False

            # 3. Xóa dữ liệu liên quan (Cascading Delete)
            fees_result = FEES_COLLECTION.delete_many({"student_id": student_id})
            trans_result = TRANSACTIONS_COLLECTION.delete_many(
                {"student_id": student_id}
            )

            print(f"✅ Đã xóa vĩnh viễn sinh viên: {student_id}")
            print(f"- Đã xóa tài khoản: {delete_result.deleted_count}")
            print(f"- Đã xóa học phí: {fees_result.deleted_count}")
            print(f"- Đã xóa giao dịch: {trans_result.deleted_count}")
            return True

        except Exception as e:
            print(f"Lỗi khi xóa vĩnh viễn: {e}")
            return False

    def postAnnouncement(self, title, content):
        """
        NÂNG CẤP: Đăng một thông báo mới.
        """
        # Sử dụng lớp Announcement
        announcement = Announcement(
            title=title, content=content, createBy=self._id  # ID của admin này
        )
        announcement.save()
        print(f"Admin {self.username} đã đăng thông báo '{title}'")
        return announcement  # Trả về đối tượng vừa tạo

    def createFee(self, student_id, description, amount, dueDate, period):
        """
        THÊM MỚI: Tạo một khoản phí mới cho sinh viên.
        """
        # Đảm bảo student_id là ObjectId
        if not isinstance(student_id, ObjectId):
            student_id = ObjectId(student_id)

        fee = Fee(
            description=description,
            amount=amount,
            student_id=student_id,
            dueDate=dueDate,
            period=period,
        )
        fee.save()
        print(
            f"Admin {self.username} đã tạo học phí '{description}' cho SV {student_id}"
        )
        return fee

    def editPayment(self, fee_id, new_status, amount_paid=None):
        """
        NÂNG CẤP: Chỉnh sửa một khoản thanh toán (Fee).
        Sử dụng các lớp Fee và Transaction.
        """
        fee = Fee.find_by_id(fee_id)
        if not fee:
            print(f"Không tìm thấy bản ghi học phí: {fee_id}")
            return False

        try:
            if new_status == "paid":
                if amount_paid is None:
                    amount_paid = fee.amount  # Mặc định trả đủ

                # 1. Đánh dấu học phí đã trả
                fee.markPaid()  # Hàm này tự .save()

                # 2. Tạo giao dịch tương ứng
                transaction = Transaction(
                    amount=amount_paid,
                    method="admin_entry",
                    student_id=fee.student_id,
                    fee_id=fee._id,
                    status="completed",
                )
                transaction.save()
                print(f"Đã tạo giao dịch cho học phí {fee_id}")
            else:
                # Chỉ cập nhật trạng thái (ví dụ: 'overdue')
                fee.status = new_status
                fee.save()

            print(f"Admin {self.username} đã cập nhật học phí {fee_id}")
            return True

        except Exception as e:
            print(f"Lỗi khi chỉnh sửa thanh toán: {e}")
            return False


# a = Admin(username = "admin", email = "", password = "admin123")

# a.save()
