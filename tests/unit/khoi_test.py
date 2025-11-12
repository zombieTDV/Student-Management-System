import pytest
from datetime import datetime
from bson.objectid import ObjectId

# --- Import tất cả Controller ---
from controllers.admin_controller import AdminController
from controllers.auth_controller import AuthController
from controllers.fee_controller import FeeController
from controllers.financial_controller import FinancialController
from controllers.notifications_controller import NotificationsController
from controllers.payment_controller import PaymentController
from controllers.student_controller import StudentController
from controllers.transaction_controller import TransactionController

# ========== CÁC HÀM HELPER TẠO DỮ LIỆU GIẢ (MOCK) ==========


def _create_mock_account(username, email, role, full_name="Mock User"):
    """Tạo một đối tượng Account (hoặc Student) giả."""
    mock_acc = MagicMock()
    mock_acc._id = ObjectId()
    mock_acc.username = username
    mock_acc.email = email
    mock_acc.role = role
    mock_acc.fullName = full_name
    mock_acc.dob = "01/01/2006"
    mock_acc.contact = "0900123456"
    mock_acc.address = "123 Vo Oanh Street"
    mock_acc.gender = "N/A"
    mock_acc.major = "IT Major"
    mock_acc.imageURL = "http://example.com/img.png"
    mock_acc.createAt = datetime(2025, 1, 1)
    mock_acc.createdAt = datetime(2025, 1, 1)

    # Giả lập các hàm của model
    mock_acc.save.return_value = True
    mock_acc.delete.return_value = True
    mock_acc.updateProfile.return_value = True
    mock_acc.changePassword.return_value = True
    mock_acc.markPaid.return_value = True
    return mock_acc


def _create_mock_fee(fee_id, student_id, amount, status="Unpaid", desc="Mock Fee"):
    """Tạo một đối tượng Fee giả."""
    mock_fee = MagicMock()
    mock_fee._id = ObjectId(fee_id)
    mock_fee.student_id = ObjectId(student_id)
    mock_fee.amount = amount
    mock_fee.status = status
    mock_fee.description = desc
    mock_fee.period = "Mock Period"

    mock_fee.save.return_value = True
    mock_fee.delete.return_value = True
    mock_fee.markPaid.return_value = True
    return mock_fee


def _create_mock_transaction(tx_id, fee_id, student_id, amount, status="completed"):
    """Tạo một đối tượng Transaction giả."""
    mock_tx = MagicMock()
    mock_tx._id = ObjectId(tx_id)
    mock_tx.fee_id = ObjectId(fee_id)
    mock_tx.student_id = ObjectId(student_id)
    mock_tx.amount = amount
    mock_tx.status = status
    mock_tx.date = datetime(2025, 11, 1)

    mock_tx.save.return_value = True
    mock_tx.delete.return_value = True
    return mock_tx


def _create_mock_announcement(title, content):
    """Tạo một đối tượng Announcement giả."""
    mock_ann = MagicMock()
    mock_ann._id = ObjectId()
    mock_ann.title = title
    mock_ann.content = content
    mock_ann.status = "draft"
    mock_ann.save.return_value = True
    mock_ann.publish.return_value = True
    return mock_ann


# ========== PYTEST FIXTURES (SETUP MOCKS) ==========
# Mỗi fixture sẽ mock các dependencies cho 1 controller


@pytest.fixture
def admin_controller(mocker):
    mocker.patch('controllers.admin_controller.Account')
    mocker.patch('controllers.admin_controller.Admin')
    mocker.patch('controllers.admin_controller.ObjectId')
    return AdminController()


@pytest.fixture
def auth_controller(mocker):
    mocker.patch('controllers.auth_controller.Account')
    mocker.patch('controllers.auth_controller.generate_random_password')
    mocker.patch('controllers.auth_controller.send_password_reset_email')

    controller = AuthController()
    controller.account_model = MagicMock()  # Mock instance trong __init__
    return controller


@pytest.fixture
def fee_controller(mocker):
    mocker.patch('controllers.fee_controller.Fee')
    mocker.patch('controllers.fee_controller.ObjectId')
    return FeeController()


@pytest.fixture
def financial_controller(mocker):
    # Cần patch 'Account' tại nơi nó được import (bên trong hàm)
    mocker.patch('controllers.financial_controller.Account')
    mocker.patch('controllers.financial_controller.Fee')
    mocker.patch('controllers.financial_controller.Transaction')
    mocker.patch('controllers.financial_controller.ObjectId')
    return FinancialController()


@pytest.fixture
def notifications_controller(mocker):
    mocker.patch('controllers.notifications_controller.Announcement')
    mocker.patch('controllers.notifications_controller.ObjectId')

    controller = NotificationsController()
    # Mock instance model trong __init__
    controller.announcement_model = MagicMock()
    return controller


@pytest.fixture
def payment_controller(mocker):
    mocker.patch('controllers.payment_controller.Account')
    mocker.patch('controllers.payment_controller.Fee')
    mocker.patch('controllers.payment_controller.Transaction')
    mocker.patch('controllers.payment_controller.ObjectId')
    return PaymentController()


@pytest.fixture
def student_controller(mocker):
    mocker.patch('controllers.student_controller.Student')
    mocker.patch('controllers.student_controller.Account')
    mocker.patch('controllers.student_controller.ObjectId')
    return StudentController()


@pytest.fixture
def transaction_controller(mocker):
    mocker.patch('controllers.transaction_controller.Transaction')
    mocker.patch('controllers.transaction_controller.ObjectId')
    # Mock collection
    mocker.patch('controllers.transaction_controller.TRANSACTIONS_COLLECTION')
    return TransactionController()


# ========== BỘ TEST CHO CÁC CONTROLLER ==========


class TestAdminController:
    def test_get_all_admins_success(self, admin_controller, mocker):
        mock_admins_list = [
            _create_mock_account("admin1", "a1@test.com", "admin"),
            _create_mock_account("admin2", "a2@test.com", "admin"),
        ]
        admin_controller.Account.find_all_admins.return_value = mock_admins_list

        result = admin_controller.get_all_admins()

        assert result["success"] is True
        assert result["count"] == 2
        assert result["admins"][0]["username"] == "admin1"

    def test_get_admin_by_id_not_found(self, admin_controller):
        admin_controller.Account.find_by_id.return_value = None
        result = admin_controller.get_admin_by_id("some_id")
        assert result["success"] is False
        assert result["message"] == "Admin not found"

    def test_search_admins_found(self, admin_controller, mocker):
        mock_all_admins_result = {
            "success": True,
            "admins": [
                {
                    "username": "Admin-Chris",
                    "email": "c@test.com",
                    "fullName": "Chris Evans",
                },
                {
                    "username": "User-Steve",
                    "email": "s@test.com",
                    "fullName": "Steve Rogers",
                },
            ],
            "count": 2,
        }
        mocker.patch.object(
            admin_controller, 'get_all_admins', return_value=mock_all_admins_result
        )

        result = admin_controller.search_admins("Steve")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["admins"][0]["username"] == "User-Steve"

    def test_create_admin_username_exists(self, admin_controller):
        admin_controller.Account.find_by_username.return_value = MagicMock()
        profile = {"username": "existing_user", "password": "123"}

        result = admin_controller.create_admin(profile)

        assert result["success"] is False
        assert result["message"] == "Username already exists"

    def test_delete_admin_success(self, admin_controller):
        mock_admin = _create_mock_account("admin", "a@a.com", "admin")
        admin_controller.Account.find_by_id.return_value = mock_admin

        result = admin_controller.delete_admin("some_id")

        assert result["success"] is True
        mock_admin.delete.assert_called_once()

    def test_validate_username_valid(self):
        assert AdminController._validate_username("valid_user")["valid"] is True

    def test_validate_username_invalid(self):
        assert AdminController._validate_username("a!")["valid"] is False


class TestAuthController:
    def test_login_success(self, auth_controller):
        mock_user = _create_mock_account("user", "u@u.com", "admin")
        auth_controller.account_model.authenticate.return_value = mock_user

        result = auth_controller.login("user", "password")

        assert result["success"] is True
        assert result["user"] == mock_user
        assert auth_controller.is_authenticated() is True

    def test_login_fail(self, auth_controller):
        auth_controller.account_model.authenticate.return_value = None
        result = auth_controller.login("user", "wrong_pass")
        assert result["success"] is False
        assert auth_controller.is_authenticated() is False

    def test_recover_password_email_not_found(self, auth_controller):
        auth_controller.Account.find_by_email.return_value = None
        result = auth_controller.recover_password("not@found.com")
        assert result["success"] is False
        assert result["message"] == "Email not found in system"


class TestFeeController:
    def test_get_all_fees_success(self, fee_controller):
        mock_list = [MagicMock(), MagicMock()]
        fee_controller.Fee.find_all.return_value = mock_list
        result = fee_controller.get_all_fees()
        assert result["success"] is True
        assert result["fees"] == mock_list

    def test_update_fee_not_found(self, fee_controller):
        fee_controller.Fee.find_by_id.return_value = None
        # Giả lập hàm find_by_id của CHÍNH controller (vì nó gọi self.find_by_id)
        mocker.patch.object(fee_controller, 'find_by_id', return_value=None)

        result = fee_controller.update_fee("not_found_id", amount=100)
        assert result["success"] is False
        assert result["message"] == "Fee not found"

    def test_mark_paid_success(self, fee_controller, mocker):
        mock_fee = _create_mock_fee("fee1", "student1", 100)
        mocker.patch.object(fee_controller, 'find_by_id', return_value=mock_fee)

        result = fee_controller.mark_paid("fee1")

        assert result["success"] is True
        assert mock_fee.status == "Paid"
        mock_fee.save.assert_called_once()


class TestFinancialController:
    def test_get_financial_summary_success(self, financial_controller):
        mock_student = _create_mock_account("student", "s@s.com", "student")
        mock_fee = _create_mock_fee("fee1", "student_id", 1000, desc="Hoc phi")
        mock_tx = _create_mock_transaction("tx1", "fee1", "student_id", 400)

        financial_controller.Account.find_by_id.return_value = mock_student
        financial_controller.Fee.find_by_student_id.return_value = [mock_fee]
        financial_controller.Transaction.find_by_student_id.return_value = [mock_tx]

        result = financial_controller.get_financial_summary("student_id")

        assert result["success"] is True
        assert result["student_info"]["name"] == mock_student.fullName
        assert len(result["financial_data"]) == 1
        assert result["financial_data"][0]["name"] == "Hoc phi - Mock Period"
        assert result["financial_data"][0]["fee"] == "1.000"
        assert result["financial_data"][0]["remain"] == "600"  # 1000 - 400

    def test_get_financial_summary_student_not_found(self, financial_controller):
        financial_controller.Account.find_by_id.return_value = None
        result = financial_controller.get_financial_summary("student_id")
        assert result["success"] is False
        assert result["message"] == "Student not found"

    def test_format_currency(self):
        assert FinancialController._format_currency(1234567) == "1.234.567"
        assert FinancialController._format_currency(0) == "0"


class TestNotificationsController:
    def test_admin_post_announcement_success(self, notifications_controller, mocker):
        mock_ann_instance = _create_mock_announcement("Test", "Content")
        # Mock hàm constructor của Announcement
        notifications_controller.Announcement.return_value = mock_ann_instance

        result = notifications_controller.admin_post_announcement("T", "C", "admin_id")

        assert result["success"] is True
        assert result["message"] == "Posted an announcement successfully"
        mock_ann_instance.publish.assert_called_once()

    def test_student_view_all_notifications(self, notifications_controller):
        mock_list = [MagicMock(), MagicMock()]
        notifications_controller.announcement_model.find_all.return_value = mock_list

        result = notifications_controller.student_view_all_notifications()

        assert result == mock_list


class TestPaymentController:
    def test_get_student_payment_data_filters_paid(self, payment_controller):
        mock_student = _create_mock_account("student", "s@s.com", "student")
        mock_fees = [
            _create_mock_fee("f1", "sid", 100, status="pending"),
            _create_mock_fee("f2", "sid", 200, status="overdue"),
            _create_mock_fee("f3", "sid", 300, status="paid"),
        ]
        payment_controller.Account.find_by_id.return_value = mock_student
        payment_controller.Fee.find_by_student_id.return_value = mock_fees

        result = payment_controller.get_student_payment_data("sid")

        assert result["success"] is True
        assert len(result["fees"]) == 2  # Chỉ lấy "pending" và "overdue"
        assert result["fees"][0]["raw_amount"] == 100
        assert result["fees"][1]["raw_amount"] == 200

    def test_process_payment_success(self, payment_controller, mocker):
        mock_fee = _create_mock_fee("f1", "sid", 150, status="pending")
        payment_controller.Fee.find_by_id.return_value = mock_fee

        mock_tx_instance = MagicMock()
        payment_controller.Transaction.return_value = mock_tx_instance

        result = payment_controller.process_payment("sid", ["f1"])

        assert result["success"] is True
        assert result["message"] == "Successfully paid 1 fee(s)"
        assert result["total_paid"] == 150

        # Kiểm tra Fee được markPaid và Transaction được save
        mock_fee.markPaid.assert_called_once()
        mock_tx_instance.save.assert_called_once()

    def test_process_payment_no_fees_selected(self, payment_controller):
        result = payment_controller.process_payment("sid", [])
        assert result["success"] is False
        assert result["message"] == "No fees selected"


class TestStudentController:
    def test_update_student_profile_success(self, student_controller):
        mock_student = _create_mock_account("student", "s@s.com", "student")
        # Phải pass một instance của Student
        student_controller.Student.return_value = mock_student

        data = {"contact": "0987654321", "dob": "10/10/2001"}

        # Giả lập student là một instance của Student
        # Đây là một cách check `isinstance` đơn giản
        mock_student.__class__ = student_controller.Student

        result = student_controller.update_student_profile(mock_student, data)

        assert result["success"] is True
        assert result["message"] == "Profile updated successfully"
        mock_student.updateProfile.assert_called_with(data)

    def test_update_student_profile_invalid_phone(self, student_controller):
        mock_student = MagicMock()
        mock_student.__class__ = student_controller.Student
        data = {"contact": "12345"}  # Invalid

        result = student_controller.update_student_profile(mock_student, data)

        assert result["success"] is False
        assert "Contact number must be 10 digits" in result["message"]

    def test_validate_phone_valid(self):
        assert StudentController._validate_phone("0123456789") is True

    def test_validate_phone_invalid(self):
        assert (
            StudentController._validate_phone("1234567890") is False
        )  # Phải bắt đầu bằng 0
        assert StudentController._validate_phone("0123456") is False  # Không đủ 10 số

    def test_get_all_students_success(self, student_controller):
        mock_list = [
            _create_mock_account("s1", "s1@s.com", "student"),
            _create_mock_account("s2", "s2@s.com", "student"),
        ]
        student_controller.Account.find_all_students.return_value = mock_list

        result = student_controller.get_all_students()

        assert result["success"] is True
        assert result["count"] == 2
        assert result["students"][0]["username"] == "s1"


class TestTransactionController:
    def test_get_all_transactions_success(self, transaction_controller):
        mock_cursor = [
            {"_id": ObjectId(), "amount": 100, "status": "completed"},
            {"_id": ObjectId(), "amount": 200, "status": "pending"},
        ]
        # Giả lập chuỗi lời gọi find().sort()
        transaction_controller.TRANSACTIONS_COLLECTION.find.return_value.sort.return_value = (
            mock_cursor
        )

        result = transaction_controller.get_all_transactions()

        assert result["success"] is True
        assert result["count"] == 2
        assert result["transactions"][0]["amount"] == 100

    def test_get_transactions_by_student_success(self, transaction_controller):
        mock_tx_list = [_create_mock_transaction("tx1", "f1", "s1", 100)]
        transaction_controller.Transaction.find_by_student_id.return_value = (
            mock_tx_list
        )

        result = transaction_controller.get_transactions_by_student("s1")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["transactions"][0]["amount"] == 100

    def test_create_transaction_success(self, transaction_controller):
        mock_tx_instance = MagicMock()
        transaction_controller.Transaction.return_value = mock_tx_instance

        result = transaction_controller.create_transaction(100, "cash", "s1", "f1")

        assert result["success"] is True
        transaction_controller.Transaction.assert_called_once()
        mock_tx_instance.save.assert_called_once()
