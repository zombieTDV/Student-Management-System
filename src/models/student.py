from models.account import Account
from models.announcement import Announcement
from models.fee import Fee
from models.transaction import Transaction


class Student(Account):
    def __init__(
        self, fullName, dob, gender, address, contact, major, imageURL=None, **kwargs
    ):
        """
        Khởi tạo Student.
        """
        kwargs.pop("role", None)
        super().__init__(role="student", **kwargs)

        self.fullName = fullName
        self.dob = dob
        self.gender = gender
        self.address = address
        self.contact = contact
        self.major = major
        self.imageURL = imageURL

    # --- Các phương thức từ UML ---

    def updateProfile(self, new_data):
        """
        Cập nhật thông tin hồ sơ của sinh viên.
        """
        allowed_updates = [
            "fullName",
            "dob",
            "gender",
            "address",
            "contact",
            "major",
            "imageURL",
        ]
        update_fields = {}

        for key, value in new_data.items():
            if key in allowed_updates:
                setattr(self, key, value)
                update_fields[key] = value

        if update_fields:
            self.save()
            print(f"Profile cho sinh viên {self.username} đã được cập nhật.")
            return True
        return False

    def viewFinancial(self):
        """
        NÂNG CẤP: Xem thông tin tài chính (Học phí và Giao dịch).
        Trả về các đối tượng Model.
        """
        # Sử dụng các phương thức của lớp Fee và Transaction
        fees = Fee.find_by_student_id(self._id)
        transactions = Transaction.find_by_student_id(self._id)

        return {"fees": fees, "transactions": transactions}

    def changePassword(self, new_password):
        """
        Sinh viên tự đổi mật khẩu của mình.
        """
        print(f"Sinh viên {self.username} đang đổi mật khẩu...")
        return self.update_password(new_password)

    def viewNotification(self):
        """
        NÂNG CẤP: Xem thông báo (Announcements).
        Trả về danh sách các đối tượng Announcement.
        """
        # Sử dụng phương thức của lớp Announcement
        notifications = Announcement.find_all(status="published")
        return notifications


s = Student(
    "TDV",
    "21/01",
    "male",
    "HCM",
    "0101",
    "CS",
    None,
    username="sv",
    email="SV@",
    password="sv123",
)
s.save()
