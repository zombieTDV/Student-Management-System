# test.py
import datetime
from database import db
from account import Account # Import lớp cha
# Các lớp con sẽ được import động bên trong Account
# nhưng chúng ta có thể import chúng ở đây để tạo mới
from admin import Admin
from student import Student

# Lấy các collection để dọn dẹp
db_conn = db.get_db()
accounts_coll = db_conn['accounts']
announcements_coll = db_conn['announcements']
fees_coll = db_conn['fees']
transactions_coll = db_conn['transactions']

def cleanup(admin_username, student_username):
    print("\n--- 🧹 Bắt đầu dọn dẹp ---")
    try:
        admin = accounts_coll.find_one({'username': admin_username})
        if admin:
            announcements_coll.delete_many({'createBy': admin['_id']})
            print(f"Đã xóa announcements của {admin_username}")
            
        student = accounts_coll.find_one({'username': student_username})
        if student:
            fees_coll.delete_many({'student_id': student['_id']})
            transactions_coll.delete_many({'student_id': student['_id']})
            print(f"Đã xóa financial của {student_username}")

        # Xóa cả hai tài khoản
        accounts_coll.delete_many({
            'username': {'$in': [admin_username, student_username]}
        })
        print(f"Đã xóa tài khoản: {admin_username}, {student_username}")
        
        print("--- ✅ Dọn dẹp hoàn tất ---")
    except Exception as e:
        print(f"Lỗi khi dọn dẹp: {e}")

def run_tests():
    print("--- 🚀 Bắt đầu Test Run (Mô hình Kế thừa) ---")
    
    ts = datetime.datetime.now().timestamp()
    ADMIN_USER = f"test_admin_{ts}"
    ADMIN_PASS = "admin_pass_123"
    
    STUDENT_USER = f"test_student_{ts}"
    STUDENT_PASS = "student_pass_123"
    
    test_admin_obj = None
    test_student_obj = None

    try:
        # === 1. Tạo Admin Account ===
        print(f"\n--- 1. Tạo Admin '{ADMIN_USER}' ---")
        admin_data = {
            'username': ADMIN_USER,
            'password': ADMIN_PASS,
            'email': f"{ADMIN_USER}@test.com"
        }
        test_admin_obj = Admin(**admin_data)
        test_admin_obj.save()
        print(f"✅ Đã tạo Admin (ID: {test_admin_obj._id})")

        # === 2. Đăng nhập với tư cách Admin ===
        print(f"\n--- 2. Test: Admin.authenticate() ---")
        authed_admin = Account.authenticate(ADMIN_USER, ADMIN_PASS)
        assert authed_admin is not None
        assert authed_admin.role == 'admin'
        assert isinstance(authed_admin, Admin)
        print(f"✅ Xác thực Admin '{authed_admin.username}' thành công.")

        # === 3. Admin tạo Student ===
        print(f"\n--- 3. Test: Admin.createStudent() ---")
        student_profile = {
            'fullName': 'Nguyễn Văn Test Kế Thừa',
            'dob': datetime.datetime(2002, 5, 15),
            'gender': 'Male',
            'address': '789 Đường Kế Thừa',
            'contact': '090111222',
            'major': 'Khoa học Kế thừa'
        }
        student_account = {
            'username': STUDENT_USER,
            'password': STUDENT_PASS,
            'email': f'{STUDENT_USER}@test.com'
        }
        
        # Sử dụng đối tượng admin đã xác thực để tạo
        test_student_obj = authed_admin.createStudent(student_profile, student_account)
        assert test_student_obj is not None
        assert test_student_obj.role == 'student'
        print(f"✅ Admin đã tạo Student '{test_student_obj.username}'")

        # === 4. Đăng nhập với tư cách Student ===
        print(f"\n--- 4. Test: Student.authenticate() ---")
        authed_student = Account.authenticate(STUDENT_USER, STUDENT_PASS)
        assert authed_student is not None
        assert authed_student.fullName == 'Nguyễn Văn Test Kế Thừa'
        assert isinstance(authed_student, Student)
        print(f"✅ Xác thực Student '{authed_student.username}' thành công.")

        # === 5. Student tự cập nhật hồ sơ ===
        print(f"\n--- 5. Test: Student.updateProfile() ---")
        authed_student.updateProfile({'address': 'Địa chỉ mới 123'})
        
        # Tải lại từ DB để chắc chắn
        reloaded_student = Account.find_by_id(authed_student._id)
        assert reloaded_student.address == 'Địa chỉ mới 123'
        print("✅ Student.updateProfile() thành công.")

        # === 6. Student đổi mật khẩu ===
        print(f"\n--- 6. Test: Student.changePassword() ---")
        NEW_PASS = "new_pass_456"
        authed_student.changePassword(NEW_PASS)
        
        # Thử đăng nhập lại bằng pass mới
        authed_student_newpass = Account.authenticate(STUDENT_USER, NEW_PASS)
        assert authed_student_newpass is not None
        
        # Thử đăng nhập bằng pass cũ (phải thất bại)
        authed_student_oldpass = Account.authenticate(STUDENT_USER, STUDENT_PASS)
        assert authed_student_oldpass is None
        print("✅ Student.changePassword() thành công (pass mới OK, pass cũ FAILED).")

        # === 7. Admin đăng thông báo ===
        print(f"\n--- 7. Test: Admin.postAnnouncement() & Student.viewNotification() ---")
        authed_admin.postAnnouncement("Test thông báo", "Nội dung...")
        
        notifications = authed_student.viewNotification()
        assert len(notifications) > 0
        assert notifications[0]['title'] == 'Test thông báo'
        print("✅ Đăng và xem thông báo thành công.")
        
    except Exception as e:
        print(f"\n❌❌❌ TEST THẤT BẠI: {e} ❌❌❌")
        import traceback
        traceback.print_exc()
        
    finally:
        # Luôn chạy dọn dẹp
        cleanup(ADMIN_USER, STUDENT_USER)
        # Đóng kết nối DB
        db.close()

# Chạy test
if __name__ == "__main__":
    run_tests()