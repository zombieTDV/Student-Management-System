from models.database import db
from bson.objectid import ObjectId

try:
    FEES_COLLECTION = db.get_db()["fees"]
except Exception as e:
    print(f"Lỗi khi kết nối collection 'fees': {e}")


class Fee:
    def __init__(
        self,
        description,
        amount,
        student_id,
        dueDate,
        period,
        status="pending",
        _id=None,
    ):
        """
        Khởi tạo một khoản Học phí.
        'student_id' là _id của Student nợ khoản phí này.
        """
        self._id = _id
        self.description = description
        self.amount = amount  # Nên dùng float hoặc Decimal
        self.student_id = student_id  # ObjectId của Student
        self.dueDate = dueDate  # Đối tượng datetime
        self.period = period  # Ví dụ: "Học kỳ 1 2025"
        self.status = status  # 'pending', 'paid', 'overdue'

    def save(self):
        """Lưu (hoặc cập nhật) khoản phí vào DB"""
        data = vars(self)

        if self._id:
            FEES_COLLECTION.update_one({"_id": self._id}, {"$set": data})
        else:
            data.pop("_id", None)
            result = FEES_COLLECTION.insert_one(data)
            self._id = result.inserted_id
        return self._id

    def markPaid(self):
        """Đánh dấu khoản phí này là 'paid' (từ UML)"""
        self.status = "paid"
        self.save()
        print(f"Học phí {self._id} đã được đánh dấu 'paid'.")

    @classmethod
    def find_by_id(cls, fee_id):
        """Tìm học phí bằng ID"""
        try:
            data = FEES_COLLECTION.find_one({"_id": ObjectId(fee_id)})
            return cls(**data) if data else None
        except Exception as e:
            print(f"Lỗi tìm học phí: {e}")
            return None

    @classmethod
    def find_by_student_id(cls, student_id):
        """
        Lấy tất cả học phí của một sinh viên.
        Đây là phương thức mà Student.viewFinancial() sẽ dùng.
        """
        # Đảm bảo student_id là ObjectId
        if not isinstance(student_id, ObjectId):
            student_id = ObjectId(student_id)

        cursor = FEES_COLLECTION.find({"student_id": student_id})
        return [cls(**data) for data in cursor]

    def __repr__(self):
        """Hiển thị dạng chuỗi (để debug)"""
        return f"<Fee {self.description} ({self.status}) for {self.student_id}>"
