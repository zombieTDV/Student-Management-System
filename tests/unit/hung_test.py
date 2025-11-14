import pytest

# Giả sử module chứa class Account được đặt ở models.account
import models.account as account_module
from models.account import hash_password, check_password, safe_compare, Account


class FakeInsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class FakeCollection:
    """Fake collection để dùng trong unit tests — không kết nối DB thật."""

    def __init__(self):
        self.storage = {}
        self._next_id = 1
        self.last_update = None
        self.last_inserted = None

    def find_one(self, query):
        # Hỗ trợ tìm theo username, email, _id (ObjectId-like or raw)
        if "_id" in query:
            _id = query["_id"]
            return self.storage.get(_id)
        if "username" in query:
            for v in self.storage.values():
                if v.get("username") == query["username"]:
                    return v
        if "email" in query:
            for v in self.storage.values():
                if v.get("email") == query["email"]:
                    return v
        return None

    def insert_one(self, doc):
        new_id = f"fakeid{self._next_id}"
        self._next_id += 1
        doc_copy = doc.copy()
        doc_copy["_id"] = new_id
        self.storage[new_id] = doc_copy
        self.last_inserted = doc_copy
        return FakeInsertResult(inserted_id=new_id)

    def update_one(self, query, update):
        _id = query.get("_id")
        if _id in self.storage:
            # giả lập $set
            set_obj = update.get("$set", {})
            self.storage[_id].update(set_obj)
            self.last_update = (_id, set_obj)

            class R:
                modified_count = 1

            return R()

        class R2:
            modified_count = 0

        return R2()

    def delete_one(self, query):
        _id = query.get("_id")
        if _id in self.storage:
            del self.storage[_id]
            return FakeDeleteResult(deleted_count=1)
        return FakeDeleteResult(deleted_count=0)

    def count_documents(self, query):
        role = query.get("role")
        return sum(1 for v in self.storage.values() if v.get("role") == role)

    def find(self, query):
        role = query.get("role")
        return [v for v in self.storage.values() if v.get("role") == role]


def test_sample():
    pass


def test_hash_password_format_and_lengths():
    hashed = hash_password("mysecret")
    assert isinstance(hashed, str)
    assert "$" in hashed
    salt, h = hashed.split("$")
    # os.urandom(16).hex() -> 32 hex chars ; sha256 hex -> 64 chars
    assert len(salt) == 32
    assert len(h) == 64


def test_check_password_correct_and_incorrect():
    pwd = "S3cr3t!"
    stored = hash_password(pwd)
    assert check_password(pwd, stored) is True
    assert check_password("wrong", stored) is False
    # malformed stored_hash should not raise, chỉ return False
    assert check_password(pwd, "badformat") is False


def test_safe_compare_behavior():
    assert safe_compare("abc", "abc") is True
    assert safe_compare("abc", "ab") is False
    assert safe_compare("", "") is True
    # non-string inputs -> False
    assert safe_compare(None, "a") is False
    assert safe_compare("a", None) is False


def test_account_init_requires_password_for_new_accounts():
    # Khi _id là None, nếu không có password -> ValueError
    with pytest.raises(ValueError):
        Account(username="u", email="e", role="student")


def test_account_save_insert_and_update_and_delete(monkeypatch):
    fake = FakeCollection()
    # thay thế collection trong module
    monkeypatch.setattr(account_module, "ACCOUNTS_COLLECTION", fake)

    # Tạo tài khoản mới (cần password) -> sẽ insert
    a = Account(username="u1", email="u1@example.com", role="student", password="pw1")
    assert a._id is None  # trước khi save chưa có id
    new_id = a.save()
    assert new_id is not None
    assert a._id == new_id
    # dữ liệu được lưu vào fake storage
    stored = fake.find_one({"_id": new_id})
    assert stored is not None
    assert stored["username"] == "u1"

    # Thử update (khi có _id), thay đổi email rồi save -> gọi update_one
    a.email = "new@example.com"
    returned = a.save()
    assert returned == a._id
    assert fake.last_update is not None
    updated_id, set_obj = fake.last_update
    assert updated_id == a._id
    assert set_obj.get("email") == "new@example.com"

    # Test delete thành công
    assert a.delete() is True
    # delete lần nữa trả về False
    assert a.delete() is False


#  ========================================================================================================================


import pytest
from unittest.mock import MagicMock
from bson import ObjectId
from models.account import Account
from models.student import Student
from models.announcement import Announcement
from models.fee import Fee
from models.transaction import Transaction
from models.admin import Admin


def test_admin_init_sets_role_admin():
    admin = Admin(username="admin", email="a@a.com", password="123")
    assert admin.role == "admin"
    assert admin.username == "admin"


def test_create_student_duplicate_username(monkeypatch):
    admin = Admin(username="admin3", email="a@a.com", password="123")

    monkeypatch.setattr(Account, "find_by_username", lambda u: True)

    result = admin.createStudent(
        student_profile={"fullname": "Hưng"},
        account_profile={"username": "student1", "email": "s1@mail.com"},
    )

    assert result is None  # vì lỗi trùng username


def test_soft_delete_student_not_found(monkeypatch):
    admin = Admin(username="admin3", email="a@a.com", password="123")

    monkeypatch.setattr(Account, "find_by_id", lambda sid: None)

    result = admin.softDeleteStudent(ObjectId())
    assert result is False


def test_hard_delete_student_not_found(monkeypatch):
    admin = Admin(username="admin3", email="a@a.com", password="123")

    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 0
    monkeypatch.setattr(
        "models.admin.ACCOUNTS_COLLECTION.delete_one", lambda q: mock_delete_result
    )

    result = admin.hardDeleteStudent(ObjectId())
    assert result is False


def test_post_announcement(monkeypatch):
    admin = Admin(username="admin3", email="a@a.com", password="123")

    fake_announcement = Announcement(title="Hello", content="World", createBy="123")

    monkeypatch.setattr("models.admin.Announcement", lambda **kwargs: fake_announcement)
    fake_announcement.save = lambda: None

    result = admin.postAnnouncement("Hello", "World")

    assert result.title == "Hello"
    assert result.content == "World"


#  ========================================================================================================================

import pytest
from unittest.mock import MagicMock
from bson import ObjectId
from datetime import datetime, UTC
from models.announcement import Announcement


# ✅ Test khởi tạo Announcement cơ bản
def test_announcement_init_defaults():
    ann = Announcement(title="Test", content="Hello", createBy="admin123")
    assert ann.title == "Test"
    assert ann.status == "published"
    assert isinstance(ann.createAt, datetime)


# ✅ Test phương thức edit thay đổi nội dung mà không gọi DB thật
def test_edit_updates_fields(monkeypatch):
    ann = Announcement(title="Old", content="Old content", createBy="admin123")
    monkeypatch.setattr(ann, "save", lambda: None)  # chặn không gọi DB

    ann.edit({"title": "New", "content": "New content"})

    assert ann.title == "New"
    assert ann.content == "New content"


# ✅ Test publish() đổi trạng thái thành 'published'
def test_publish_sets_status(monkeypatch):
    ann = Announcement(
        title="Draft", content="...", createBy="admin123", status="draft"
    )
    monkeypatch.setattr(ann, "save", lambda: None)

    ann.publish()
    assert ann.status == "published"


# ✅ Test store() đổi trạng thái thành 'archived'
def test_store_sets_status(monkeypatch):
    ann = Announcement(title="Old", content="...", createBy="admin123")
    monkeypatch.setattr(ann, "save", lambda: None)

    ann.store()
    assert ann.status == "archived"


# ✅ Test find_by_id trả về đối tượng hợp lệ (mock DB)
def test_find_by_id_returns_announcement(monkeypatch):
    fake_data = {
        "_id": ObjectId(),
        "title": "Mock Title",
        "content": "Mock Content",
        "createBy": "admin123",
        "createAt": datetime.now(UTC),
        "status": "published",
    }

    # Mock ANNOUNCEMENTS_COLLECTION.find_one
    monkeypatch.setattr(
        "models.announcement.ANNOUNCEMENTS_COLLECTION.find_one",
        lambda query: fake_data,
    )

    ann = Announcement.find_by_id(ObjectId())
    assert isinstance(ann, Announcement)
    assert ann.title == "Mock Title"


# ✅ Test find_by_id trả về None khi không có dữ liệu
def test_find_by_id_returns_none(monkeypatch):
    monkeypatch.setattr(
        "models.announcement.ANNOUNCEMENTS_COLLECTION.find_one",
        lambda query: None,
    )

    ann = Announcement.find_by_id(ObjectId())
    assert ann is None


#  ========================================================================================================================


import pytest
from unittest.mock import patch, MagicMock
from models.database import Database


def test_singleton_instance():
    """Kiểm tra chỉ có 1 instance (Singleton)"""
    db1 = Database()
    db2 = Database()
    assert db1 is db2, "Database không tuân theo Singleton pattern"


def test_get_db_calls_connect_if_none(monkeypatch):
    """Kiểm tra get_db() sẽ tự gọi connect() nếu chưa có _db"""
    db = Database()
    db._db = None
    called = {}

    def fake_connect():
        called["connect"] = True
        db._db = "fake_db"

    monkeypatch.setattr(db, "connect", fake_connect)

    result = db.get_db()
    assert called.get("connect", False)
    assert result == "fake_db"


def test_close_connection(monkeypatch):
    """Kiểm tra close() đóng kết nối"""
    db = Database()
    mock_client = MagicMock()
    db._client = mock_client

    db.close()
    mock_client.close.assert_called_once()


#  ========================================================================================================================

import pytest
from unittest.mock import MagicMock, patch
from bson.objectid import ObjectId
from models.fee import Fee


def test_fee_initialization():
    """Kiểm tra khởi tạo Fee"""
    fee = Fee("Học phí HK1", 1000000, ObjectId(), "2025-06-01", "HK1 2025")
    assert fee.description == "Học phí HK1"
    assert fee.amount == 1000000
    assert fee.status == "pending"
    assert fee.period == "HK1 2025"


@patch("models.fee.FEES_COLLECTION")
def test_save_insert(mock_collection):
    """Kiểm tra save() khi tạo mới (insert_one)"""
    mock_insert = MagicMock()
    mock_insert.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_insert

    fee = Fee("Test", 200, ObjectId(), "2025-06-01", "HK2 2025")
    result_id = fee.save()

    mock_collection.insert_one.assert_called_once()
    assert result_id == mock_insert.inserted_id


@patch("models.fee.FEES_COLLECTION")
def test_save_update(mock_collection):
    """Kiểm tra save() khi có _id (update_one)"""
    fee_id = ObjectId()
    fee = Fee("Update test", 300, ObjectId(), "2025-06-01", "HK3 2025", _id=fee_id)

    fee.save()
    mock_collection.update_one.assert_called_once_with(
        {"_id": fee_id}, {"$set": vars(fee)}
    )


@patch("models.fee.FEES_COLLECTION")
def test_find_all(mock_collection):
    """Kiểm tra find_all()"""
    mock_collection.find.return_value = [
        {
            "_id": ObjectId(),
            "description": "Test",
            "amount": 100,
            "student_id": ObjectId(),
            "dueDate": "2025-06-01",
            "period": "HK1 2025",
            "status": "pending",
        }
    ]
    fees = Fee.find_all()
    assert len(fees) == 1
    assert isinstance(fees[0], Fee)
    assert fees[0].description == "Test"


@patch("models.fee.FEES_COLLECTION")
def test_delete_success(mock_collection):
    """Kiểm tra delete() khi có _id"""
    fee = Fee("Del test", 100, ObjectId(), "2025-06-01", "HK4 2025", _id=ObjectId())
    result = fee.delete()
    mock_collection.delete_one.assert_called_once()
    assert result is True


def test_delete_no_id():
    """Kiểm tra delete() khi chưa có _id"""
    fee = Fee("Del test", 100, ObjectId(), "2025-06-01", "HK4 2025")
    result = fee.delete()
    assert result is False


@patch("models.fee.FEES_COLLECTION")
def test_markPaid(mock_collection):
    """Kiểm tra markPaid() thay đổi status và gọi save()"""
    fee = Fee("Paid test", 150, ObjectId(), "2025-06-01", "HK5 2025")
    fee.save = MagicMock()
    fee.markPaid()
    assert fee.status == "paid"
    fee.save.assert_called_once()


@patch("models.fee.FEES_COLLECTION")
def test_find_by_id_found(mock_collection):
    """Kiểm tra find_by_id() khi tìm thấy"""
    fake_data = {
        "_id": ObjectId(),
        "description": "Test",
        "amount": 100,
        "student_id": ObjectId(),
        "dueDate": "2025-06-01",
        "period": "HK1 2025",
        "status": "pending",
    }
    mock_collection.find_one.return_value = fake_data

    fee = Fee.find_by_id(fake_data["_id"])
    assert isinstance(fee, Fee)
    assert fee.description == "Test"


@patch("models.fee.FEES_COLLECTION")
def test_find_by_id_not_found(mock_collection):
    """Kiểm tra find_by_id() khi không tìm thấy"""
    mock_collection.find_one.return_value = None
    result = Fee.find_by_id(ObjectId())
    assert result is None
