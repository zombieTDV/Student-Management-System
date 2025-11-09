from models.student import Student
from models.account import Account
import re
from datetime import datetime


class StudentController:
    """Controller for managing student operations"""

    @staticmethod
    def update_student_profile(student, updated_data):
        """
        Sinh viên dùng để cập nhật thông tin của sinh viên
        """
        try:
            # Validate that it's a student
            if not isinstance(student, Student):
                return {
                    'success': False,
                    'message': 'Invalid student object'
                }
            
            # Validate email if provided
            if 'email' in updated_data and updated_data['email']:
                email = updated_data['email'].strip()
                if not StudentController._validate_email(email):
                    return {
                        'success': False,
                        'message': 'Invalid email format'
                    }
                updated_data['email'] = email
            
            # Validate contact if provided
            if 'contact' in updated_data and updated_data['contact']:
                contact = updated_data['contact'].strip()
                if not StudentController._validate_phone(contact):
                    return {
                        'success': False,
                        'message': 'Contact number must be 10 digits starting with 0'
                    }
                updated_data['contact'] = contact
            
            # Validate date of birth if provided
            if 'dob' in updated_data and updated_data['dob']:
                dob = updated_data['dob'].strip()
                if not StudentController._validate_date(dob):
                    return {
                        'success': False,
                        'message': 'Date of Birth must be in DD/MM/YYYY format'
                    }
                updated_data['dob'] = dob
            
            # Clean up empty values
            cleaned_data = {
                key: value for key, value in updated_data.items()
                if value is not None and str(value).strip() != ''
            }
            
            if not cleaned_data:
                return {
                    'success': False,
                    'message': 'No valid fields to update'
                }
            
            # Call Student model's updateProfile method
            success = student.updateProfile(cleaned_data)
            
            if success:
                return {
                    'success': True,
                    'message': 'Profile updated successfully',
                    'updated_fields': list(cleaned_data.keys()),
                    'student_info': {
                        'fullName': student.fullName,
                        'imageURL': student.imageURL,
                        'dob': student.dob,
                        'gender': student.gender,
                        'address': student.address,
                        'contact': student.contact,
                        'email': student.email,
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'No changes were made'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            }

    @staticmethod
    def register_student_by_admin(admin, student_data):
        """
        Admin đăng ký tài khoản sinh viên mới, sử dụng username và account
        """
        try:
            # Xác định phải quyền của admin không
            if not hasattr(admin, 'role') or admin.role != 'admin':
                return {
                    'success': False,
                    'message': 'Unauthorized: Only admins can register students'
                }
            
            # Xác thực các field cần thiết
            username = student_data.get('username', '').strip()
            password = student_data.get('password', '').strip()
            
            if not username:
                return {'success': False, 'message': 'Username (Student ID) is required'}
            
            if not password:
                return {'success': False, 'message': 'Password is required'}
                        
            # Xác thực 
            username_validation = StudentController._validate_username(username)
            if not username_validation['valid']:
                return {
                    'success': False,
                    'message': username_validation['message']
                }
            
            # Validate password strength
            password_validation = StudentController._validate_password(password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'message': password_validation['message']
                }
            
            # Check if username already exists
            if Account.find_by_username(username):
                return {
                    'success': False,
                    'message': f'Student ID "{username}" already exists'
                }

            # Gọi hàm đăng ký tài khoản sinh viên vào Table Account
            success = Account.save(student_data)
            if success:
                return {
                    'success': True,
                    'message': f'Student "{username}" registered successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Cannot register this student account!'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error registering student: {str(e)}'
            }

    @staticmethod
    def admin_update_student_password(admin, student, new_password):
        """
        Admin cập nhật mật khẩu của sinh viên
        """
        try:
            # Xác thực phân quyền admin
            if not hasattr(admin, 'role') or admin.role != 'admin':
                return {
                    'success': False,
                    'message': 'Unauthorized: Only admins can change student passwords'
                }
            
            # Xác thực mật khẩu mới
            password_validation = StudentController._validate_password(new_password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'message': password_validation['message']
                }
            
            success = student.changePassword(new_password)
            
            if success:
                return {
                    'success': True,
                    'message': 'Password changed successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to change password'
                }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error changing password: {str(e)}'
            }



    # ========== Các phương thức Helper (dùng để xác thực thông tin có hợp lệ không) ==========
    
    @staticmethod
    def _validate_username(username):
        """Validate username format (StudentID = CitizenID)"""
        if len(username) < 3:
            return {
                'valid': False,
                'message': 'Student ID must be at least 3 characters'
            }
        
        if len(username) > 50:
            return {
                'valid': False,
                'message': 'Student ID must be less than 50 characters'
            }
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return {
                'valid': False,
                'message': 'Student ID can only contain letters, numbers, dots, hyphens, and underscores'
            }
        
        return {'valid': True, 'message': 'Valid Student ID'}
    
    @staticmethod
    def _validate_password(password):
        """Kiểm tra độ dài mật khẩu"""
        if len(password) < 8:
            return {
                'valid': False,
                'message': 'Password must be at least 8 characters'
            }
        
        if len(password) > 128:
            return {
                'valid': False,
                'message': 'Password must be less than 128 characters'
            }
        
        # Kiểm tra có ít nhất một chữ in hoa
        if not re.search(r'[A-Z]', password):
            return {
                'valid': False,
                'message': 'Password must contain at least one uppercase letter'
            }
        
        # Kiểm tra có ít nhất một chữ cái thường
        if not re.search(r'[a-z]', password):
            return {
                'valid': False,
                'message': 'Password must contain at least one lowercase letter'
            }
        
        # Kiểm tra có ít nhất một con số
        if not re.search(r'[0-9]', password):
            return {
                'valid': False,
                'message': 'Password must contain at least one number'
            }
        
        return {'valid': True, 'message': 'Valid password'}
        
    @staticmethod
    def _validate_phone(phone):
        """Xác thực đúng kiểu số điện thoại Việt Nam không (10 con số bắt đầu bằng số 0)"""
        pattern = r'^0[0-9]{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def _validate_date(date_str):
        """Định dạng format ngày kiểu DD/MM/YYYY"""
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except Exception:
            return False
