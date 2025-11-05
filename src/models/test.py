import datetime
from models.account import Account
from models.admin import Admin
from models.student import Student
from models.database import db # Import đối tượng db

def run_tests():
    print("--- [BẮT ĐẦU TEST] ---")
    
    # Lấy collection 'users' và xóa sạch để test lại từ đầu
    # BẠN CÓ THỂ BỎ QUA DÒNG NÀY NẾU MUỐN GIỮ LẠI DỮ LIỆU CŨ
    print("\n[Bước 0: Dọn dẹp CSDL...]")
    user_collection = db.get_db()["users"]
    user_collection.delete_many({})
    print("Đã xóa hết user cũ.")

    # -------------------------------------------------
    # TEST 1: TẠO MỚI (CREATE)
    # -------------------------------------------------
    print("\n[Bước 1: Test tạo Admin...]")
    admin = Admin.create_admin(
        username="admin01",
        email="admin@test.com",
        password="admin123",
        accountID="AD001"
    )
    if admin:
        print(f"✅ Tạo Admin thành công: {admin.username} (Role: {admin.role})")
    else:
        print("❌ Tạo Admin thất bại!")

    print("\n[Bước 2: Test tạo Student...]")
    student = Student.create_student(
        username="sv001",
        email="sv@test.com",
        password="sv123",
        accountID="SV001",
        fullName="Nguyễn Văn A",
        dob=datetime.datetime(2003, 5, 15),
        gender="Nam",
        address="123 ABC, Q1, TPHCM",
        contactPhone="0909123456",
        major="Công nghệ thông tin"
    )
    if student:
        print(f"✅ Tạo Student thành công: {student.fullName} (Role: {student.role})")
    else:
        print("❌ Tạo Student thất bại!")

    # -------------------------------------------------
    # TEST 2: ĐĂNG NHẬP VÀ TRUY VẤN (READ)
    # -------------------------------------------------
    print("\n[Bước 3: Test Đăng nhập (Authenticate)...]")
    
    print("  -> Thử đăng nhập Student (đúng pass):")
    user_sv = Account.authenticate("sv001", "sv123")
    if user_sv:
        # Check xem nó có phải là 1 object Student không
        print(f"✅ Đăng nhập thành công! User: {user_sv.username}, Role: {user_sv.role}")
        print(f"   Tên đầy đủ: {user_sv.fullName}") # Chỉ Student mới có
    else:
        print("❌ Đăng nhập thất bại!")

    print("  -> Thử đăng nhập Admin (sai pass):")
    user_admin_fail = Account.authenticate("admin01", "saipass")
    if not user_admin_fail:
        print("✅ Thất bại như mong đợi.")
    else:
        print("❌ Lỗi logic! Đăng nhập vẫn thành công dù sai pass.")

    # -------------------------------------------------
    # TEST 3: CẬP NHẬT (UPDATE)
    # -------------------------------------------------
    print("\n[Bước 4: Test Cập nhật (Update)...]")
    
    # 1. Tìm lại student
    sv_to_update = Account.find_by_username("sv001")
    
    if sv_to_update:
        print(f"  -> Tên gốc: {sv_to_update.fullName}")
        
        # 2. Thay đổi dữ liệu
        sv_to_update.fullName = "Trần Thị B"
        sv_to_update.address = "456 XYZ, Q.Thủ Đức"
        
        # 3. Gọi .save()
        sv_to_update.save()
        print("  -> Đã gọi hàm save()")

        # 4. Kiểm tra lại bằng cách tìm lại từ CSDL
        sv_check = Account.find_by_username("sv001")
        if sv_check.fullName == "Trần Thị B":
            print(f"✅ Cập nhật thành công! Tên mới: {sv_check.fullName}")
        else:
            print("❌ Cập nhật thất bại!")

    # -------------------------------------------------
    # TEST 4: NHÚNG (EMBEDDED)
    # -------------------------------------------------
    print("\n[Bước 5: Test thêm dữ liệu nhúng (Add Fee)...]")
    
    if sv_to_update:
        print(f"  -> Số lượng phí ban đầu: {len(sv_to_update.fees)}")
        
        fee_data_1 = {
            "description": "Học phí HK1",
            "amount": 5000000,
            "status": "pending",
            "dueDate": datetime.datetime.now()
        }
        sv_to_update.add_fee(fee_data_1)
        print("  -> Đã thêm 1 khoản phí.")
        
        # Kiểm tra lại
        sv_check_2 = Account.find_by_username("sv001")
        if len(sv_check_2.fees) == 1 and sv_check_2.fees[0]["amount"] == 5000000:
            print(f"✅ Thêm phí thành công! Số phí hiện tại: {len(sv_check_2.fees)}")
            print(f"   Mô tả phí: {sv_check_2.fees[0]['description']}")
        else:
            print("❌ Thêm phí thất bại!")

    print("\n--- [TEST HOÀN TẤT] ---")

# --- Chạy hàm test ---
if __name__ == "__main__":
    run_tests()