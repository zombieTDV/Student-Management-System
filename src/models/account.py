# models/account.py
from models.database import db
from bson.objectid import ObjectId
import datetime
import hashlib
import os  # Cần thiết để tạo salt ngẫu nhiên

# Tải collection một lần
try:
    ACCOUNTS_COLLECTION = db.get_db()["accounts"]
except Exception as e:
    print(f"Lỗi khi kết nối tới collection 'accounts': {e}")
    exit(1)


def hash_password(password):
    """Băm mật khẩu an toàn với salt dùng hashlib.SHA256"""
    # Tạo một salt ngẫu nhiên
    salt = os.urandom(16).hex()

    # Băm mật khẩu với (salt + password)
    hashed_password = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    # Lưu salt và hash chung một chuỗi, phân cách bằng $
    # Định dạng này rất phổ biến và dễ dàng parse
    return f"{salt}${hashed_password}"


def check_password(password, stored_hash):
    """Kiểm tra mật khẩu có khớp với hash đã lưu không"""
    try:
        # Tách salt và hash đã lưu
        salt, hash_key = stored_hash.split('$')
        
        # Hash lại mật khẩu được cung cấp với salt đã lưu
        password_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
        
        # --- THAY ĐỔI Ở ĐÂY ---
        # Thay thế 'compare_digest' bằng so sánh == thông thường
        # vì phiên bản Python của bạn không hỗ trợ nó.
        return password_hash == hash_key
        # return hashlib.compare_digest(password_hash, hash_key) # Dòng cũ
        
    except Exception as e:
        # Lỗi (ví dụ: chuỗi hash không đúng định dạng, rỗng, v.v.)
        print(f"Lỗi khi kiểm tra mật khẩu: {e}")
        return False


class Account:
    """Lớp cơ sở cho tất cả các loại tài khoản (Admin, Student)"""

    def __init__(
        self, username, email, role, password=None, _id=None, createAt=None, **kwargs
    ):
        self._id = _id
        self.username = username
        self.email = email
        self.role = role

        # Gán các thuộc tính khác (nếu có, từ lớp con)
        # ví dụ: fullName, dob... sẽ được gán ở đây
        for key, value in kwargs.items():
            if key not in ("password_hash"):  # Tránh ghi đè hash
                setattr(self, key, value)

        # Xử lý mật khẩu
        if password:
            # Băm mật khẩu mới khi được cung cấp
            self.password_hash = hash_password(password)
        elif _id is None:
            # Nếu tạo mới mà không có pass, raise lỗi
            raise ValueError("Mật khẩu là bắt buộc khi tạo tài khoản mới.")
        else:
            # Khi tải từ DB, chúng ta không truyền 'password',
            # nhưng chúng ta cần lấy hash đã lưu
            if not hasattr(self, "password_hash"):
                account_data = ACCOUNTS_COLLECTION.find_one({"_id": self._id})
                # Gán trực tiếp hash đã lưu từ DB
                self.password_hash = account_data.get("password_hash")

        self.createAt = createAt or datetime.datetime.utcnow()

    def save(self):
        """Lưu (hoặc cập nhật) dữ liệu tài khoản vào collection 'accounts'"""

        # Chúng ta cần phải lấy *TẤT CẢ* dữ liệu của lớp con
        # sử dụng vars(self)
        account_data = vars(self).copy()

        # Xóa _id nếu nó là None (trường hợp tạo mới)
        if self._id is None:
            account_data.pop("_id", None)

        if self._id:
            # Cập nhật
            ACCOUNTS_COLLECTION.update_one({"_id": self._id}, {"$set": account_data})
        else:
            # Thêm mới
            # Đảm bảo không lưu password gốc (nếu còn tồn)
            account_data.pop("password", None)
            result = ACCOUNTS_COLLECTION.insert_one(account_data)
            self._id = result.inserted_id
        return self._id

    @classmethod
    def find_by_username(cls, username):
        """Tìm tài khoản bằng username."""
        account_data = ACCOUNTS_COLLECTION.find_one({"username": username})
        if account_data:
            return cls._instantiate_correct_class(account_data)
        return None

    @classmethod
    def find_by_id(cls, account_id):
        """Tìm tài khoản bằng ID."""
        try:
            account_data = ACCOUNTS_COLLECTION.find_one({"_id": ObjectId(account_id)})
            if account_data:
                return cls._instantiate_correct_class(account_data)
            return None
        except Exception as e:
            print(f"Lỗi khi tìm ID: {e}")
            return None

    @classmethod
    def authenticate(cls, username, password):
        """Xác thực người dùng và trả về đối tượng (Student hoặc Admin)"""
        account = cls.find_by_username(username)

        # `account.password_hash` sẽ chứa chuỗi "salt$hash"
        if account and check_password(password, account.password_hash):
            return account  # Đây sẽ là instance của Student hoặc Admin

        return None

    def update_password(self, new_password):
        """Cập nhật mật khẩu cho tài khoản (instance method)"""
        self.password_hash = hash_password(new_password)
        # Chỉ cập nhật trường password_hash trong DB
        ACCOUNTS_COLLECTION.update_one(
            {"_id": self._id}, {"$set": {"password_hash": self.password_hash}}
        )
        print(f"Đã cập nhật mật khẩu cho {self.username}")
        return True

    @staticmethod
    def _instantiate_correct_class(account_data):
        """
        Hàm helper quan trọng: Quyết định khởi tạo lớp Student hay Admin
        dựa trên trường 'role'.
        """
        role = account_data.get("role")

        # Chúng ta phải import ở đây để tránh lỗi 'circular import'
        from models.student import Student
        from models.admin import Admin

        # **kwargs sẽ truyền toàn bộ dict dữ liệu vào constructor
        # của Student hoặc Admin
        if role == "student":
            return Student(**account_data)
        elif role == "admin":
            return Admin(**account_data)
        else:
            # Trả về Account cơ sở nếu không rõ role
            return Account(**account_data)

    def __repr__(self):
        return f"<{self.role.capitalize()} {self.username} ({self._id})>"
