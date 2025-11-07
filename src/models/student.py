# models/student.py
from models.account import Account
from models.database import db
from bson.objectid import ObjectId
import datetime

class Student(Account):
    
    def __init__(self, fullName, dob, gender, address, contact, major, 
                 imageURL=None, **kwargs):
        """
        Khởi tạo Student.
        **kwargs sẽ chứa các thuộc tính của Account (username, email, v.v.)
        """
        
        # --- SỬA Ở ĐÂY ---
        # Lấy 'role' ra khỏi kwargs (vì nó đã có từ DB khi tải)
        kwargs.pop('role', None)
        
        # Gọi __init__ của lớp cha (Account) với role='student'
        super().__init__(role='student', **kwargs)
        
        # Các thuộc tính riêng của Student
        self.fullName = fullName
        self.dob = dob
        self.gender = gender
        self.address = address
        self.contact = contact
        self.major = major
        self.imageURL = imageURL

    # Ghi đè phương thức save() để đảm bảo tất cả dữ liệu được lưu
    # (Thực ra lớp cha Account.save() đã xử lý việc này bằng vars(self))
    # Nhưng nếu bạn muốn logic lưu riêng biệt, hãy định nghĩa nó ở đây.
    # def save(self):
    #     # ...
    #     super().save()

    # --- Các phương thức từ UML (giờ là instance methods) ---

    def updateProfile(self, new_data):
        """
        Cập nhật thông tin hồ sơ của sinh viên.
        new_data là một dict chứa các trường cần cập nhật.
        """
        allowed_updates = ['fullName', 'dob', 'gender', 'address', 'contact', 'major', 'imageURL']
        update_fields = {}
        
        for key, value in new_data.items():
            if key in allowed_updates:
                setattr(self, key, value)  # Cập nhật trên đối tượng Python
                update_fields[key] = value
        
        if update_fields:
            # Gọi save() để lưu toàn bộ thay đổi vào DB
            self.save()
            print(f"Profile cho sinh viên {self.username} đã được cập nhật.")
            return True
        return False

    def viewFinancial(self):
        """
        Xem thông tin tài chính (Học phí và Giao dịch).
        """
        fees_collection = db.get_db()['fees']
        transactions_collection = db.get_db()['transactions']
        
        # Tìm tất cả học phí và giao dịch liên quan đến _id này
        fees = list(fees_collection.find({'student_id': self._id}))
        transactions = list(transactions_collection.find({'student_id': self._id}))
        
        return {'fees': fees, 'transactions': transactions}

    def changePassword(self, new_password):
        """
        Sinh viên tự đổi mật khẩu của mình.
        Phương thức này đến từ lớp cha Account.
        """
        print(f"Sinh viên {self.username} đang đổi mật khẩu...")
        return self.update_password(new_password)

    def viewNotification(self):
        """
        Xem thông báo (Announcements).
        """
        announcements_collection = db.get_db()['announcements']
        
        # Tìm tất cả thông báo, sắp xếp theo ngày tạo mới nhất
        notifications = list(announcements_collection.find().sort('createAt', -1))
        return notifications