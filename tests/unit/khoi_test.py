import pytest
import os
import time
from datetime import datetime
from bson.objectid import ObjectId

# --- Import Controllers ---
from controllers.auth_controller import AuthController
from controllers.admin_controller import AdminController
from controllers.fee_controller import FeeController
from controllers.financial_controller import FinancialController
from controllers.notifications_controller import NotificationsController
from controllers.payment_controller import PaymentController
from controllers.student_controller import StudentController
from controllers.transaction_controller import TransactionController

class DummyStudent:
    """Một class giả để làm 'type' cho isinstance() hoạt động"""
    pass

# ==================================
# ========== HELPER MOCKS ==========
# ==================================

# ==================================
# ========== HELPER MOCKS ==========
# ==================================

VALID_STUDENT_ID = "60c72b9f9b1d8f001f8e4c6a"
VALID_ADMIN_ID = "60c72b9f9b1d8f001f8e4c6b"
VALID_FEE_ID = "60c72b9f9b1d8f001f8e4c6c"
VALID_TX_ID = "60c72b9f9b1d8f001f8e4c6d"

@pytest.fixture
def mock_student_obj(mocker):
    """Tạo một đối tượng Student giả."""
    # SỬA: Tạo instance từ class giả
    mock_student = DummyStudent()
    
    # Thêm các thuộc tính mock vào instance
    mock_student._id = ObjectId(VALID_STUDENT_ID)
    mock_student.username = "student_user"
    mock_student.email = "student@test.com"
    mock_student.role = "student"
    mock_student.fullName = "Mock Student"
    mock_student.dob = "01/01/2000"
    mock_student.major = "IT"
    mock_student.contact = "0900123456"
    mock_student.address = "123 Test Street"
    mock_student.gender = "Male"
    mock_student.imageURL = "http://example.com/img.png"
    mock_student.createAt = datetime(2025, 1, 1)

    mock_student.save = mocker.MagicMock(return_value=True)
    mock_student.delete = mocker.MagicMock(return_value=True)
    mock_student.updateProfile = mocker.MagicMock(return_value=True)
    mock_student.changePassword = mocker.MagicMock(return_value=True)
    
    return mock_student
    
@pytest.fixture
def mock_admin_obj(mocker):
    """Tạo một đối tượng Admin (Account) giả."""
    mock_admin = mocker.MagicMock() 
    mock_admin._id = ObjectId(VALID_ADMIN_ID)
    mock_admin.username = "admin_user"
    mock_admin.email = "admin@test.com"
    mock_admin.role = "admin"
    mock_admin.fullName = "Mock Admin"
    mock_admin.createAt = datetime(2025, 1, 1)
    
    mock_admin.save.return_value = True
    mock_admin.delete.return_value = True
    return mock_admin

@pytest.fixture
def mock_fee_obj(mocker):
    """Tạo một đối tượng Fee giả."""
    mock_fee = mocker.MagicMock() 
    mock_fee._id = ObjectId(VALID_FEE_ID)
    mock_fee.student_id = ObjectId(VALID_STUDENT_ID)
    mock_fee.amount = 100000
    mock_fee.status = "pending" # Thay vì "Unpaid"
    mock_fee.description = "Mock Fee"
    mock_fee.period = "Mock Period"

    mock_fee.save.return_value = True
    mock_fee.delete.return_value = True
    mock_fee.markPaid.return_value = True
    return mock_fee

@pytest.fixture
def mock_tx_obj(mocker):
    """Tạo một đối tượng Transaction giả."""
    mock_tx = mocker.MagicMock()
    mock_tx._id = ObjectId(VALID_TX_ID)
    mock_tx.fee_id = ObjectId(VALID_FEE_ID)
    mock_tx.student_id = ObjectId(VALID_STUDENT_ID)
    mock_tx.amount = 100000
    mock_tx.status = "completed"
    mock_tx.date = datetime(2025, 1, 1)
    
    mock_tx.save.return_value = True
    mock_tx.delete.return_value = True
    return mock_tx

@pytest.fixture
def mock_announcement_obj(mocker):
    """Tạo một đối tượng Announcement giả."""
    mock_ann = mocker.MagicMock() 
    mock_ann._id = ObjectId()
    mock_ann.title = "Test Title"
    mock_ann.content = "Test Content"
    mock_ann.status = "draft"
    
    mock_ann.save.return_value = True
    mock_ann.publish.return_value = True
    return mock_ann


# ======================================
# ========== CONTROLLER FIXTURES =========
# ======================================


@pytest.fixture
def auth_controller(mocker):
    """Mock các dependencies cho AuthController."""
    mock_account = mocker.patch('controllers.auth_controller.Account')
    
    mocker.patch('controllers.auth_controller.os.path.exists')
    mocker.patch('controllers.auth_controller.os.remove')
    mocker.patch('controllers.auth_controller.open', mocker.mock_open())
    mocker.patch('controllers.auth_controller.json.dump')
    mocker.patch('controllers.auth_controller.json.load')
    mocker.patch('controllers.auth_controller.time.time')

    mocker.patch.object(AuthController, '__init__', lambda self: None)
    
    controller = AuthController()
    controller.account_model = mocker.MagicMock() 
    controller.current_account = None
    controller.TOKEN_FILE = ".token.json" 
    
    return {"controller": controller, "MockAccount": mock_account}


@pytest.fixture
def admin_controller(mocker):
    """Mock các dependencies cho AdminController."""
    mock_account = mocker.patch('controllers.admin_controller.Account')
    mock_admin = mocker.patch('controllers.admin_controller.Admin', None) 
    # SỬA: Xóa patch cho ObjectId
    # mocker.patch('controllers.admin_controller.ObjectId')
    mocker.patch('models.database.db')
    
    return {
        "controller": AdminController(),
        "MockAccount": mock_account,
        "MockAdmin": mock_admin
    }


@pytest.fixture
def fee_controller(mocker):
    """Mock các dependencies cho FeeController."""
    mock_fee = mocker.patch('controllers.fee_controller.Fee')
    # SỬA: Xóa patch cho ObjectId
    # mocker.patch('controllers.fee_controller.ObjectId')
    mocker.patch('controllers.fee_controller.FEES_COLLECTION')
    return {"controller": FeeController(), "MockFee": mock_fee}


@pytest.fixture
def financial_controller(mocker):
    """Mock các dependencies cho FinancialController."""
    # Account được import BÊN TRONG HÀM -> patch đường dẫn GỐC
    mock_account = mocker.patch('models.account.Account')
    
    # SỬA: Fee và Transaction được import ở ĐẦU FILE -> patch đường dẫn LOCAL
    mock_fee = mocker.patch('controllers.financial_controller.Fee')
    mock_tx = mocker.patch('controllers.financial_controller.Transaction')
    
    return {
        "controller": FinancialController(),
        "MockAccount": mock_account,
        "MockFee": mock_fee,
        "MockTransaction": mock_tx
    }


@pytest.fixture
def payment_controller(mocker):
    """Mock các dependencies cho PaymentController."""
    # Account được import BÊN TRONG HÀM -> patch đường dẫn GỐC
    mock_account = mocker.patch('models.account.Account') 
    
    # SỬA: Fee và Transaction được import ở ĐẦU FILE -> patch đường dẫn LOCAL
    mock_fee = mocker.patch('controllers.payment_controller.Fee')
    mock_tx = mocker.patch('controllers.payment_controller.Transaction')
    
    mocker.patch('controllers.payment_controller.datetime')
    
    return {
        "controller": PaymentController(),
        "MockAccount": mock_account,
        "MockFee": mock_fee,
        "MockTransaction": mock_tx
    }


@pytest.fixture
def notifications_controller(mocker):
    """Mock các dependencies cho NotificationsController."""
    mock_announcement = mocker.patch('controllers.notifications_controller.Announcement')
    # SỬA: Xóa patch cho ObjectId
    # mocker.patch('controllers.notifications_controller.ObjectId')
    
    mocker.patch.object(NotificationsController, '__init__', lambda self: None)
    
    controller = NotificationsController()
    controller.announcement_model = mocker.MagicMock()
    
    return {"controller": controller, "MockAnnouncement": mock_announcement}


@pytest.fixture
def student_controller(mocker):
    """Mock các dependencies cho StudentController."""
    # SỬA: Patch 'Student' để nó trỏ vào class giả DummyStudent
    mock_student_class = mocker.patch(
        'controllers.student_controller.Student', 
        new=DummyStudent  # <--- TRỎ VÀO CLASS THẬT
    )
    
    mock_account = mocker.patch('controllers.student_controller.Account')
    
    return {
        "controller": StudentController(),
        "MockStudent": mock_student_class, # Đây là class DummyStudent
        "MockAccount": mock_account
    }


@pytest.fixture
def transaction_controller(mocker):
    """Mock các dependencies cho TransactionController."""
    mock_tx = mocker.patch('controllers.transaction_controller.Transaction')
    mock_collection = mocker.patch('controllers.transaction_controller.TRANSACTIONS_COLLECTION')
    # SỬA: Xóa patch cho ObjectId
    # mocker.patch('controllers.transaction_controller.ObjectId')
    
    return {
        "controller": TransactionController(),
        "MockTransaction": mock_tx,
        "MockCollection": mock_collection
    }


# ======================================
# ========== BỘ TEST SCRIPT ============
# ======================================

class TestAuthController:
    def test_login_success(self, auth_controller, mock_admin_obj, mocker):
        controller = auth_controller["controller"]
        
        controller.account_model.authenticate.return_value = mock_admin_obj
        mocker.patch.object(controller, '_save_token')

        result = controller.login("admin_user", "password123")

        assert result["success"] is True
        assert result["message"] == "Login successful"
        controller._save_token.assert_called_once_with(mock_admin_obj)

    def test_login_fail(self, auth_controller):
        controller = auth_controller["controller"]
        controller.account_model.authenticate.return_value = None
        result = controller.login("admin_user", "wrongpass")
        assert result["success"] is False

    def test_login_token_success(self, auth_controller, mock_student_obj, mocker):
        controller = auth_controller["controller"]
        MockAccount = auth_controller["MockAccount"]
        
        token_data = {"account_id": VALID_STUDENT_ID, "expiry": time.time() + 1000}
        mocker.patch.object(controller, '_load_token', return_value=token_data)
        MockAccount.find_by_id.return_value = mock_student_obj

        result = controller.login(None, None) 

        assert result["success"] is True
        assert result["auto_login"] is True
        MockAccount.find_by_id.assert_called_once_with(VALID_STUDENT_ID)

    def test_logout(self, auth_controller, mocker):
        controller = auth_controller["controller"]
        controller.current_account = mocker.MagicMock()
        os.path.exists.return_value = True

        controller.logout()

        assert controller.current_account is None
        os.remove.assert_called_once_with(controller.TOKEN_FILE)

class TestAdminController:
    def test_get_all_admins_success(self, admin_controller, mock_admin_obj):
        controller = admin_controller["controller"]
        MockAccount = admin_controller["MockAccount"]
        
        MockAccount.find_all_admins.return_value = [mock_admin_obj]
        
        result = controller.get_all_admins()
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["admins"][0]["username"] == "admin_user"

    def test_get_admin_by_id_not_found(self, admin_controller):
        controller = admin_controller["controller"]
        MockAccount = admin_controller["MockAccount"]
        
        MockAccount.find_by_id.return_value = None
        
        result = controller.get_admin_by_id(VALID_ADMIN_ID)
        
        assert result["success"] is False
        assert result["message"] == "Admin not found"
        
    def test_create_admin_username_exists(self, admin_controller, mock_admin_obj):
        controller = admin_controller["controller"]
        MockAccount = admin_controller["MockAccount"]

        MockAccount.find_by_username.return_value = mock_admin_obj
        
        profile = {"username": "admin_user", "password": "123"}
        result = controller.create_admin(profile)
        
        assert result["success"] is False
        assert result["message"] == "Username already exists"

    def test_delete_admin_success(self, admin_controller, mock_admin_obj):
        controller = admin_controller["controller"]
        MockAccount = admin_controller["MockAccount"]

        MockAccount.find_by_id.return_value = mock_admin_obj
        
        result = controller.delete_admin(VALID_ADMIN_ID)
        
        assert result["success"] is True
        mock_admin_obj.delete.assert_called_once()

class TestFeeController:
    def test_get_all_fees_success(self, fee_controller, mock_fee_obj):
        controller = fee_controller["controller"]
        MockFee = fee_controller["MockFee"]
        
        MockFee.find_all.return_value = [mock_fee_obj, mock_fee_obj]
        
        result = controller.get_all_fees()
        
        assert result["success"] is True
        assert len(result["fees"]) == 2

    def test_find_by_id_success(self, fee_controller, mock_fee_obj):
        controller = fee_controller["controller"]
        MockFee = fee_controller["MockFee"]
        
        MockFee.find_by_id.return_value = mock_fee_obj
        
        result = controller.find_by_id(VALID_FEE_ID)
        
        assert result == mock_fee_obj

    def test_create_fee(self, fee_controller, mocker):
        controller = fee_controller["controller"]
        MockFee = fee_controller["MockFee"]
        
        mock_fee_instance = mocker.MagicMock()
        MockFee.return_value = mock_fee_instance
        
        new_fee = controller.create_fee("Hoc phi", 50000, VALID_STUDENT_ID, "01/01/2026", "HK1")
        
        assert new_fee == mock_fee_instance
        MockFee.assert_called_once() 

    def test_mark_paid_success(self, fee_controller, mock_fee_obj, mocker):
        controller = fee_controller["controller"]
        
        mocker.patch.object(controller, 'find_by_id', return_value=mock_fee_obj)
        
        result = controller.mark_paid(VALID_FEE_ID)
        
        assert result["success"] is True
        assert mock_fee_obj.status == "Paid"
        mock_fee_obj.save.assert_called_once()

class TestFinancialController:
    def test_get_financial_summary_success(self, financial_controller, mock_student_obj, mock_fee_obj, mock_tx_obj):
        controller = financial_controller["controller"]
        MockAccount = financial_controller["MockAccount"]
        MockFee = financial_controller["MockFee"]
        MockTransaction = financial_controller["MockTransaction"]

        MockAccount.find_by_id.return_value = mock_student_obj
        MockFee.find_by_student_id.return_value = [mock_fee_obj]
        MockTransaction.find_by_student_id.return_value = [mock_tx_obj]
        
        result = controller.get_financial_summary(VALID_STUDENT_ID)
        
        # SỬA: Lỗi "assert False is True" đã được fix bằng cách xóa mock ObjectId
        assert result["success"] is True
        assert result["student_info"]["name"] == "Mock Student"
        assert len(result["financial_data"]) == 1
        assert result["financial_data"][0]["remain"] == "0"

    def test_get_financial_summary_student_not_found(self, financial_controller):
        controller = financial_controller["controller"]
        MockAccount = financial_controller["MockAccount"]
        
        MockAccount.find_by_id.return_value = None
        
        result = controller.get_financial_summary(VALID_STUDENT_ID)
        
        assert result["success"] is False
        assert result["message"] == "Student not found"

class TestNotificationsController:
    def test_admin_post_announcement_success(self, notifications_controller, mock_announcement_obj):
        controller = notifications_controller["controller"]
        MockAnnouncement = notifications_controller["MockAnnouncement"]
        
        MockAnnouncement.return_value = mock_announcement_obj
        
        result = controller.admin_post_announcement("Title", "Content", VALID_ADMIN_ID)
        
        assert result["success"] is True
        mock_announcement_obj.publish.assert_called_once()

    def test_admin_post_announcement_fail(self, notifications_controller):
        controller = notifications_controller["controller"]
        MockAnnouncement = notifications_controller["MockAnnouncement"]
        
        MockAnnouncement.side_effect = Exception("DB Error")
        
        result = controller.admin_post_announcement("Title", "Content", VALID_ADMIN_ID)
        
        assert result["success"] is False
        assert result["message"] == "Failed to post an announcement"

class TestPaymentController:
    def test_get_student_payment_data_success(self, payment_controller, mock_student_obj, mock_fee_obj, mocker):
        controller = payment_controller["controller"]
        MockAccount = payment_controller["MockAccount"]
        MockFee = payment_controller["MockFee"]
        
        mock_paid_fee = mocker.MagicMock()
        mock_paid_fee.status = "paid"
        
        MockAccount.find_by_id.return_value = mock_student_obj
        MockFee.find_by_student_id.return_value = [mock_fee_obj, mock_paid_fee]
        
        result = controller.get_student_payment_data(VALID_STUDENT_ID)
        
        # SỬA: Lỗi "assert False is True" đã được fix bằng cách xóa mock ObjectId
        assert result["success"] is True
        assert len(result["fees"]) == 1
        assert result["fees"][0]["id"] == str(VALID_FEE_ID)

    def test_process_payment_success(self, payment_controller, mock_fee_obj, mocker):
        controller = payment_controller["controller"]
        MockFee = payment_controller["MockFee"]
        MockTransaction = payment_controller["MockTransaction"]
        
        mock_tx_instance = mocker.MagicMock()
        
        MockFee.find_by_id.return_value = mock_fee_obj
        MockTransaction.return_value = mock_tx_instance
        
        result = controller.process_payment(VALID_STUDENT_ID, [VALID_FEE_ID])
        
        # SỬA: Lỗi "assert False is True" đã được fix bằng cách xóa mock ObjectId
        assert result["success"] is True
        assert result["total_paid"] == 100000
        mock_tx_instance.save.assert_called_once()
        mock_fee_obj.markPaid.assert_called_once()

class TestStudentController:
    def test_update_student_profile_success(self, student_controller, mock_student_obj):
        controller = student_controller["controller"]
        MockStudent = student_controller["MockStudent"]
        
        # SỬA: THÊM DÒNG NÀY
        mock_student_obj.__class__ = MockStudent
        
        data = {"contact": "0987654321", "dob": "10/10/2001"}
        
        result = controller.update_student_profile(mock_student_obj, data)
        
        assert result["success"] is True
        assert result["message"] == "Profile updated successfully"
        mock_student_obj.updateProfile.assert_called_with(data)

    def test_update_student_profile_invalid_phone(self, student_controller, mock_student_obj):
        controller = student_controller["controller"]
        MockStudent = student_controller["MockStudent"]
        mock_student_obj.__class__ = MockStudent
        
        data = {"contact": "12345"}
        
        result = controller.update_student_profile(mock_student_obj, data)
        
        assert result["success"] is False
        assert "Contact number must be 10 digits" in result["message"] 

    def test_register_student_by_admin_success(self, student_controller, mock_admin_obj, mock_student_obj, mocker): # Thêm 'mocker'
        controller = student_controller["controller"]
        MockAccount = student_controller["MockAccount"]
        
        MockAccount.find_by_username.return_value = None
    
        mocker.patch.object(DummyStudent, '__new__', return_value=mock_student_obj)
        
        result = controller.register_student_by_admin(mock_admin_obj, "new_student", "ValidPass123")
        
        assert result["success"] is True # Giờ sẽ pass
        mock_student_obj.save.assert_called_once()

    def test_register_student_username_exists(self, student_controller, mock_admin_obj, mock_student_obj):
        controller = student_controller["controller"]
        MockAccount = student_controller["MockAccount"]

        MockAccount.find_by_username.return_value = mock_student_obj
        
        result = controller.register_student_by_admin(mock_admin_obj, "student_user", "ValidPass123")
        
        assert result["success"] is False
        assert 'already exists' in result["message"]

    def test_get_all_students_success(self, student_controller, mock_student_obj):
        controller = student_controller["controller"]
        MockAccount = student_controller["MockAccount"]
        
        MockAccount.find_all_students.return_value = [mock_student_obj]
        
        result = controller.get_all_students()
        
        assert result["success"] is True
        assert result["count"] == 1

class TestTransactionController:
    def test_get_all_transactions_success(self, transaction_controller, mocker):
        controller = transaction_controller["controller"]
        MockCollection = transaction_controller["MockCollection"]
        
        mock_cursor_data = [
            {"_id": ObjectId(VALID_TX_ID), "amount": 100, "status": "completed"},
        ]
        MockCollection.find.return_value.sort.return_value = mock_cursor_data
        
        result = controller.get_all_transactions()
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["transactions"][0]["_id"] == VALID_TX_ID

    def test_get_transactions_by_student_success(self, transaction_controller, mock_tx_obj):
        controller = transaction_controller["controller"]
        MockTransaction = transaction_controller["MockTransaction"]

        MockTransaction.find_by_student_id.return_value = [mock_tx_obj]
        
        result = controller.get_transactions_by_student(VALID_STUDENT_ID)
        
        assert result["success"] is True
        assert result["count"] == 1
        assert result["transactions"][0]["_id"] == VALID_TX_ID

    def test_create_transaction_success(self, transaction_controller, mock_tx_obj):
        controller = transaction_controller["controller"]
        MockTransaction = transaction_controller["MockTransaction"]
        
        MockTransaction.return_value = mock_tx_obj
        
        result = controller.create_transaction(100, "cash", VALID_STUDENT_ID, VALID_FEE_ID)
        
        assert result["success"] is True
        assert result["transaction"]["_id"] == VALID_TX_ID
        mock_tx_obj.save.assert_called_once()

    def test_delete_transaction_success(self, transaction_controller, mock_tx_obj):
        controller = transaction_controller["controller"]
        MockTransaction = transaction_controller["MockTransaction"]
        
        MockTransaction.find_by_id.return_value = mock_tx_obj
        
        result = controller.delete_transaction(VALID_TX_ID)
        
        assert result["success"] is True
        mock_tx_obj.delete.assert_called_once()

    def test_delete_transaction_not_found(self, transaction_controller, mocker):
        controller = transaction_controller["controller"]
        MockTransaction = transaction_controller["MockTransaction"]
        MockCollection = transaction_controller["MockCollection"]
        
        MockTransaction.find_by_id.return_value = None
        
        mock_delete_result = mocker.MagicMock()
        mock_delete_result.deleted_count = 0
        MockCollection.delete_one.return_value = mock_delete_result
        
        result = controller.delete_transaction(VALID_TX_ID)
        
        assert result["success"] is False
        assert result["message"] == "Transaction not found"
