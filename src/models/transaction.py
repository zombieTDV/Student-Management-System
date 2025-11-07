from models.database import db
from bson.objectid import ObjectId
import datetime

try:
    TRANSACTIONS_COLLECTION = db.get_db()['transactions']
except Exception as e:
    print(f"Lỗi khi kết nối collection 'transactions': {e}")

class Transaction:
    
    def __init__(self, amount, method, student_id, fee_id, 
                 status='completed', date=None, _id=None):
        """
        Khởi tạo Giao dịch.
        'student_id' là _id của Student thực hiện.
        'fee_id' là _id của Fee mà giao dịch này trả cho.
        """
        self._id = _id
        self.amount = amount
        self.method = method  # Ví dụ: 'admin_entry', 'bank_transfer', 'momo'
        self.student_id = student_id  # ObjectId
        self.fee_id = fee_id  # ObjectId
        self.status = status  # 'completed', 'pending', 'failed'
        self.date = date or datetime.datetime.utcnow()

    def save(self):
        """Lưu (hoặc cập nhật) giao dịch vào DB"""
        data = vars(self)
        
        if self._id:
            TRANSACTIONS_COLLECTION.update_one({'_id': self._id}, {'$set': data})
        else:
            data.pop('_id', None)
            result = TRANSACTIONS_COLLECTION.insert_one(data)
            self._id = result.inserted_id
        return self._id
    
    @classmethod
    def find_by_id(cls, trans_id):
        """Tìm giao dịch bằng ID"""
        try:
            data = TRANSACTIONS_COLLECTION.find_one({'_id': ObjectId(trans_id)})
            return cls(**data) if data else None
        except Exception as e:
            print(f"Lỗi tìm giao dịch: {e}")
            return None
    
    @classmethod
    def find_by_student_id(cls, student_id):
        """
        Lấy tất cả giao dịch của một sinh viên.
        Student.viewFinancial() sẽ dùng phương thức này.
        """
        # Đảm bảo student_id là ObjectId
        if not isinstance(student_id, ObjectId):
            student_id = ObjectId(student_id)
            
        cursor = TRANSACTIONS_COLLECTION.find({'student_id': student_id})
        return [cls(**data) for data in cursor]
    
    @classmethod
    def find_by_fee_id(cls, fee_id):
        """Lấy các giao dịch liên quan đến một khoản phí"""
        if not isinstance(fee_id, ObjectId):
            fee_id = ObjectId(fee_id)
            
        cursor = TRANSACTIONS_COLLECTION.find({'fee_id': fee_id})
        return [cls(**data) for data in cursor]

    def __repr__(self):
        """Hiển thị dạng chuỗi (để debug)"""
        return f"<Transaction {self.amount} ({self.method}) for {self.student_id}>"