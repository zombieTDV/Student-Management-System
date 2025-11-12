# tests/test_account.py
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


def test_authenticate_returns_account_on_correct_password(monkeypatch):
    fake = FakeCollection()
    monkeypatch.setattr(account_module, "ACCOUNTS_COLLECTION", fake)

    pwd = "mypw"
    # đặt role là 'unknown' để tránh import Student/Admin trong _instantiate_correct_class
    # authenticate sử dụng find_by_username -> find_one trả về bản ghi -> _instantiate_correct_class -> Account
    obj = Account.authenticate("authuser", pwd)
    assert obj is not None
    assert isinstance(obj, Account)
    assert obj.username == "authuser"

    # sai password -> None
    assert Account.authenticate("authuser", "bad") is None
