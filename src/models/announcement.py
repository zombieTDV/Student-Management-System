from models.database import db
from bson.objectid import ObjectId
import datetime

# Lấy collection một lần để tái sử dụng
try:
    ANNOUNCEMENTS_COLLECTION = db.get_db()['announcements']
except Exception as e:
    print(f"Lỗi khi kết nối collection 'announcements': {e}")

class Announcement:
    
    def __init__(self, title, content, createBy, createAt=None, _id=None, status='published'):
        """
        Khởi tạo một Thông báo.
        'createBy' là _id của Admin tạo ra nó.
        """
        self._id = _id
        self.title = title
        self.content = content
        self.createBy = createBy  # Đây là ObjectId của Admin
        self.createAt = createAt or datetime.datetime.utcnow()
        self.status = status  # Trạng thái: 'published' (đã đăng), 'draft' (nháp), 'archived' (lưu trữ)

    def save(self):
        """Lưu (hoặc cập nhật) thông báo vào DB"""
        data = vars(self)
        
        if self._id:
            # Cập nhật
            ANNOUNCEMENTS_COLLECTION.update_one({'_id': self._id}, {'$set': data})
        else:
            # Thêm mới
            data.pop('_id', None) # Xóa _id None để MongoDB tự tạo
            result = ANNOUNCEMENTS_COLLECTION.insert_one(data)
            self._id = result.inserted_id
        return self._id

    def delete(self):
        """Xóa thông báo này khỏi DB"""
        if self._id:
            ANNOUNCEMENTS_COLLECTION.delete_one({'_id': self._id})
            print(f"Thông báo {self._id} đã bị xóa.")

    def edit(self, new_data):
        """
        Chỉnh sửa title hoặc content.
        new_data là dict: {'title': '...', 'content': '...'}
        """
        if 'title' in new_data:
            self.title = new_data['title']
        if 'content' in new_data:
            self.content = new_data['content']
        self.save() # Lưu thay đổi

    def publish(self):
        """Đặt trạng thái là 'published' (từ UML)"""
        self.status = 'published'
        self.save()

    def store(self):
        """Đặt trạng thái là 'archived' (từ 'store' trong UML)"""
        self.status = 'archived'
        self.save()
    
    @classmethod
    def find_by_id(cls, ann_id):
        """Tìm thông báo bằng ID"""
        try:
            data = ANNOUNCEMENTS_COLLECTION.find_one({'_id': ObjectId(ann_id)})
            return cls(**data) if data else None
        except Exception as e:
            print(f"Lỗi tìm thông báo: {e}")
            return None

    @classmethod
    def find_all(cls, status='published'):
        """
        Lấy tất cả thông báo (mặc định là đã publish).
        Đây là phương thức mà Student.viewNotification() sẽ dùng.
        """
        cursor = ANNOUNCEMENTS_COLLECTION.find({'status': status}).sort('createAt', -1)
        # Trả về một danh sách các đối tượng Announcement
        return [cls(**data) for data in cursor]

    def __repr__(self):
        """Hiển thị dạng chuỗi (để debug)"""
        return f"<Announcement '{self.title}' by {self.createBy}>"