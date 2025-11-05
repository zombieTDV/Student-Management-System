from models.account import Account # Import lớp Cha
from datetime import datetime
from bson import ObjectId

class Student(Account):
    def __init__(self, fullName, dob, gender, address, contactPhone, major, 
                 imageURL=None, fees=None, **kwargs):
        """
        Khởi tạo Student.
        **kwargs sẽ chứa các trường của Account (username, email...)
        """
        # Gán cứng role='student' và gọi hàm __init__ của Cha
        super().__init__(role="student", **kwargs)
        
        # Các thuộc tính riêng của Student
        self.fullName = fullName
        self.dob = dob
        self.gender = gender
        self.address = address
        self.contactPhone = contactPhone
        self.major = major
        self.imageURL = imageURL
        self.fees = fees or [] # Mảng nhúng (embedded)

    def to_doc(self):
        """
        Chuyển object Student thành 1 document để lưu vào DB
        """
        # Lấy tất cả thuộc tính của instance
        doc = self.__dict__ 
        # Xóa password hash nếu lỡ có
        doc.pop("password_hash", None) 
        return doc

    def save(self):
        """
        Lưu các thay đổi của object Student này vào CSDL
        (Dùng cho các hàm 'updateProfile' của Controller)
        """
        doc_data = self.to_doc()
        # Dùng 'self.collection' kế thừa từ Account
        self.collection.update_one(
            {"_id": self._id},
            {"$set": doc_data}
        )

    @classmethod
    def create_student(cls, username, email, password, accountID, 
                         fullName, dob, gender, address, contactPhone, major, imageURL=None):
        """
        Hàm Model để TẠO MỚI một student trong CSDL
        """
        password_hash = cls._hash_password(password)
        student_doc = {
            # Trường của Account
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": "student",
            "accountID": accountID,
            "created_at": datetime.now(),
            "last_login": None,
            # Trường của Student
            "fullName": fullName,
            "dob": dob,
            "gender": gender,
            "address": address,
            "contactPhone": contactPhone,
            "major": major,
            "imageURL": imageURL,
            "fees": []
        }
        try:
            # Dùng 'cls.collection' kế thừa từ Account
            result = cls.collection.insert_one(student_doc)
            student_doc["_id"] = result.inserted_id
            return Student(**student_doc) # Trả về 1 đối tượng Student
        except Exception as e:
            print(f"Error creating student: {e}")
            return None
