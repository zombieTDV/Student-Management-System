import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from datetime import datetime

from controllers.auth_controller import AuthController


class UpdateStudentProfile:
    """
    Use Case 4: Update Student Profile
    - Cho phép sinh viên cập nhật thông tin cá nhân
    - Validate dữ liệu trước khi submit
    - Upload avatar
    - Một số field không được phép sửa (StudentID, FullName)
    """

    def __init__(
        self,
        parent,
        auth_controller: AuthController,
        back_callback,
        update_callback=None,  # Callback để gọi controller
    ):
        self.parent = parent
        self.auth_controller = auth_controller

        self.student_data = {
            "student_id": auth_controller.current_account._id,
            "full_name": auth_controller.current_account.fullName,
            "gender": auth_controller.current_account.gender,
            "dob": auth_controller.current_account.dob,
            "enrollment_year": auth_controller.current_account.createAt,
            "major": auth_controller.current_account.major,
            "avatar": auth_controller.current_account.imageURL,
            "address": auth_controller.current_account.address,
            "email": auth_controller.current_account.email,
            "contact": auth_controller.current_account.contact,
        }

        self.back_callback = back_callback
        self.update_callback = update_callback
        self.avatar_path = None  # Store new avatar path

        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Main container with rounded border
        main_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=50,
            border_width=3,
            border_color="black",
        )
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header with back arrow
        header_frame = ctk.CTkFrame(main_frame, fg_color="white")
        header_frame.pack(fill="x", padx=60, pady=(40, 20))

        # Back arrow button
        back_arrow = ctk.CTkLabel(
            header_frame,
            text="🔙",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#FF7B7B",
            cursor="hand2",
        )
        back_arrow.pack(side="left", padx=(0, 30))
        if back_callback:
            back_arrow.bind("<Button-1>", lambda e: back_callback())

        # Header title
        header_label = ctk.CTkLabel(
            header_frame,
            text="Update Info",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        header_label.pack(side="left")

        # Scrollable content area
        self.scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=0,
            scrollbar_button_color="#22C55E",
            scrollbar_button_hover_color="#16A34A",
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=60, pady=(20, 20))

        # Content container
        content_container = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white",
        )
        content_container.pack(fill="both", expand=True, padx=20, pady=20)

        # === Avatar Section ===
        avatar_section = ctk.CTkFrame(content_container, fg_color="white")
        avatar_section.pack(pady=(0, 30))

        # Avatar frame with border
        self.avatar_frame = ctk.CTkFrame(
            avatar_section,
            fg_color="white",
            corner_radius=20,
            border_width=3,
            border_color="#22C55E",
            width=280,
            height=360,
        )
        self.avatar_frame.pack()
        self.avatar_frame.pack_propagate(False)

        # Avatar display label
        self.avatar_label = ctk.CTkLabel(
            self.avatar_frame,
            text="",
            fg_color="#F0F0F0",
            corner_radius=17,
        )
        self.avatar_label.pack(fill="both", expand=True, padx=3, pady=3)

        # Avatar placeholder text
        if not self.student_data.get("avatar"):
            self.avatar_placeholder = ctk.CTkLabel(
                self.avatar_label,
                text="📷\nNo Photo",
                font=ctk.CTkFont(family="Arial", size=24),
                text_color="#999999",
            )
            self.avatar_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # Upload button below avatar
        upload_btn = ctk.CTkButton(
            avatar_section,
            text="📁 Upload New Image",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2",
            text_color="white",
            height=45,
            corner_radius=10,
            command=self.upload_avatar,
        )
        upload_btn.pack(pady=(15, 0))

        # === Information Fields ===
        fields_section = ctk.CTkFrame(content_container, fg_color="white")
        fields_section.pack(fill="both", expand=True, pady=(20, 0))

        # Fixed fields (read-only)
        self.create_readonly_field(
            fields_section, "Student ID", self.student_data.get("student_id", "")
        )
        # self.create_readonly_field(
        #     fields_section, "Full Name", self.student_data.get("full_name", "")
        # )

        # Editable fields
        self.entries = {}

        # Date of Birth
        self.entries["full_name"] = self.create_editable_field(
            fields_section,
            "full_name*",
            self.student_data.get("full_name", ""),
            placeholder="Nguyen Van A",
        )

        # Date of Birth
        self.entries["dob"] = self.create_editable_field(
            fields_section,
            "Date of Birth *",
            self.student_data.get("dob", ""),
            placeholder="DD/MM/YYYY",
        )

        # Gender (Dropdown)
        self.entries["gender"] = self.create_dropdown_field(
            fields_section,
            "Gender *",
            ["Male", "Female", "Other"],
            self.student_data.get("gender", "Male"),
        )

        # Address
        self.entries["address"] = self.create_editable_field(
            fields_section,
            "Address",
            self.student_data.get("address", ""),
            placeholder="Enter your address",
        )

        # Contact Number
        self.entries["contact"] = self.create_editable_field(
            fields_section,
            "Contact Number",
            self.student_data.get("contact", ""),
            placeholder="09xxxxxxxx",
        )

        # Email
        self.entries["email"] = self.create_editable_field(
            fields_section,
            "Email *",
            self.student_data.get("email", ""),
            placeholder="your.email@example.com",
        )

        # Major (Dropdown)
        majors = [
            "Computer Science",
            "Business Administration",
            "Engineering",
            "Mathematics",
            "Physics",
        ]
        self.entries["major"] = self.create_dropdown_field(
            fields_section, "Major *", majors, self.student_data.get("major", majors[0])
        )

        # Required field note
        note_label = ctk.CTkLabel(
            fields_section,
            text="* Required fields",
            font=ctk.CTkFont(family="Arial", size=12, slant="italic"),
            text_color="#666666",
        )
        note_label.pack(anchor="w", padx=20, pady=(10, 0))

        # === Buttons Section ===
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(20, 40))

        # Update button
        update_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ Update",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="white",
            width=200,
            height=60,
            corner_radius=15,
            command=self.submit_update,
        )
        update_btn.pack(side="right", padx=(10, 0))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✕ Cancel",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#FF5252",
            hover_color="#FF1744",
            text_color="white",
            width=200,
            height=60,
            corner_radius=15,
            command=self.back_callback if back_callback else None,
        )
        cancel_btn.pack(side="right")

    def create_readonly_field(self, parent, label_text, value_text):
        """Create a read-only field (for StudentID)"""
        field_container = ctk.CTkFrame(parent, fg_color="white")
        field_container.pack(fill="x", pady=12, padx=20)

        # Label
        label = ctk.CTkLabel(
            field_container,
            text=label_text + ":",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#333333",
            anchor="w",
            width=180,
        )
        label.pack(side="left", padx=(0, 20))

        # Read-only display
        value_frame = ctk.CTkFrame(
            field_container,
            fg_color="#E8E8E8",
            corner_radius=10,
            border_width=2,
            border_color="#CCCCCC",
            height=50,
        )
        value_frame.pack(side="left", fill="x", expand=True)

        value_label = ctk.CTkLabel(
            value_frame,
            text=value_text,
            font=ctk.CTkFont(family="Arial", size=15),
            text_color="#666666",
            anchor="w",
        )
        value_label.pack(fill="both", expand=True, padx=20, pady=12)

    def create_editable_field(self, parent, label_text, initial_value, placeholder=""):
        """Create an editable text field"""
        field_container = ctk.CTkFrame(parent, fg_color="white")
        field_container.pack(fill="x", pady=12, padx=20)

        # Label
        label = ctk.CTkLabel(
            field_container,
            text=label_text + ":",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#333333",
            anchor="w",
            width=180,
        )
        label.pack(side="left", padx=(0, 20))

        # Entry field
        entry = ctk.CTkEntry(
            field_container,
            font=ctk.CTkFont(family="Arial", size=15),
            placeholder_text=placeholder,
            height=50,
            corner_radius=10,
            border_width=2,
            border_color="#AAAAAA",
            fg_color="white",
        )
        entry.pack(side="left", fill="x", expand=True)
        entry.insert(0, initial_value)

        return entry

    def create_dropdown_field(self, parent, label_text, options, initial_value):
        """Create a dropdown field"""
        field_container = ctk.CTkFrame(parent, fg_color="white")
        field_container.pack(fill="x", pady=12, padx=20)

        # Label
        label = ctk.CTkLabel(
            field_container,
            text=label_text + ":",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#333333",
            anchor="w",
            width=180,
        )
        label.pack(side="left", padx=(0, 20))

        # Dropdown
        dropdown = ctk.CTkOptionMenu(
            field_container,
            values=options,
            font=ctk.CTkFont(family="Arial", size=15),
            height=50,
            corner_radius=10,
            button_color="#22C55E",
            button_hover_color="#16A34A",
            fg_color="white",
            dropdown_fg_color="white",
        )
        dropdown.pack(side="left", fill="x", expand=True)
        dropdown.set(initial_value)

        return dropdown

    def upload_avatar(self):
        """Handle avatar upload"""
        file_path = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            try:
                # Load and display image
                image = Image.open(file_path)
                # Resize to fit frame
                image = image.resize((274, 354), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                # Update avatar label
                self.avatar_label.configure(image=photo, text="")
                self.avatar_label.image = photo  # Keep reference

                # Hide placeholder if exists
                if hasattr(self, "avatar_placeholder"):
                    self.avatar_placeholder.place_forget()

                # Store path
                self.avatar_path = file_path
                print(f"Avatar uploaded: {file_path}")

            except Exception as e:
                self.show_error_popup(f"Failed to load image: {str(e)}")

    def validate_data(self):
        """Validate all input data"""
        errors = []

        # Date of Birth validation
        dob = self.entries["dob"].get().strip()
        if dob:
            if not self._validate_date(dob):
                errors.append("Date of Birth must be in DD/MM/YYYY format")

        # Contact validation
        contact = self.entries["contact"].get().strip()
        if contact:
            if not self._validate_phone(contact):
                errors.append("Contact Number must be 10 digits starting with 0")

        # Email validation
        email = self.entries["email"].get().strip()
        if not email:
            errors.append("Email is required")
        elif not self._validate_email(email):
            errors.append("Email format is invalid")

        return errors

    def _validate_date(self, date_str):
        """Validate date format DD/MM/YYYY"""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except Exception:
            return False

    def _validate_phone(self, phone):
        """Validate Vietnamese phone number"""
        import re

        pattern = r"^0[0-9]{9}$"
        return re.match(pattern, phone) is not None

    def _validate_email(self, email):
        """Validate email format"""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def submit_update(self):
        """Submit profile update"""
        # Validate data
        errors = self.validate_data()

        if errors:
            self.show_error_popup("\n".join(errors))
            return

        # Collect updated data
        updated_data = {
            "full_name": self.entries["full_name"].get().strip(),
            "dob": self.entries["dob"].get().strip(),
            "gender": self.entries["gender"].get(),
            "address": self.entries["address"].get().strip(),
            "contact": self.entries["contact"].get().strip(),
            "email": self.entries["email"].get().strip(),
            "major": self.entries["major"].get(),
        }

        # Add avatar if uploaded
        if self.avatar_path:
            updated_data["imageURL"] = self.avatar_path

        # Call update callback (controller)
        if self.update_callback:
            result = self.update_callback(updated_data)
            if result.get("success"):
                self.show_success_popup("Profile updated successfully!")
            else:
                self.show_error_popup(result.get("message", "Update failed"))
        else:
            print("Updated data:", updated_data)
            self.show_success_popup("Profile updated successfully!")

    def show_success_popup(self, message):
        """Show success message"""
        success_dialog = ctk.CTkToplevel(self.parent)
        success_dialog.title("Success")
        success_dialog.geometry("400x200")
        success_dialog.grab_set()
        success_dialog.attributes("-topmost", True)

        ctk.CTkLabel(
            success_dialog,
            text="✓ " + message,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#22C55E",
            wraplength=360,
        ).pack(pady=40, padx=20)

        ctk.CTkButton(
            success_dialog,
            text="OK",
            width=120,
            height=40,
            command=lambda: [success_dialog.destroy(), self.back_callback()],
        ).pack(pady=(0, 20))

    def show_error_popup(self, message):
        """Show error message"""
        error_dialog = ctk.CTkToplevel(self.parent)
        error_dialog.title("Error")
        error_dialog.geometry("400x250")
        error_dialog.grab_set()
        error_dialog.attributes("-topmost", True)

        ctk.CTkLabel(
            error_dialog,
            text="⚠️ Validation Error",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#EF4444",
        ).pack(pady=20, padx=20)

        ctk.CTkLabel(
            error_dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color="#333333",
            wraplength=360,
            justify="left",
        ).pack(pady=10, padx=20)

        ctk.CTkButton(
            error_dialog, text="OK", width=120, height=40, command=error_dialog.destroy
        ).pack(pady=20)


# # Example usage
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("1400x900")
#     root.title("Update Student Profile")

#     container = ctk.CTkFrame(root)
#     container.pack(fill="both", expand=True)

#     sample_student = {
#         "student_id": "2021001",
#         "full_name": "Nguyễn Văn An",
#         "avatar": None,
#         "dob": "15/01/2000",
#         "gender": "Male",
#         "address": "123 Nguyễn Huệ, Quận 1, TP.HCM",
#         "contact": "0901234567",
#         "email": "nguyen.van.an@student.edu.vn",
#         "major": "Computer Science",
#     }

#     def go_back():
#         print("Going back...")

#     def handle_update(data):
#         print("Update data:", data)
#         return {"success": True, "message": "Profile updated"}

#     app = UpdateStudentProfile(container, sample_student, go_back, handle_update)
#     root.mainloop()
