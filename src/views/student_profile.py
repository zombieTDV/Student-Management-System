import customtkinter as ctk

from controllers.auth_controller import AuthController


class StudentProfile:
    """
    View Student Profile (Use Case 3)
    - Display full student information (read-only)
    - Accessed from "More information" link in StudentDashboard
    - Shows: StudentID, FullName, Avatar, DOB, Gender, Address, Phone, Email, Major
    """

    def __init__(
        self,
        parent,
        auth_controller: AuthController,
        back_callback,
        edit_callback,
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
        self.edit_callback = edit_callback

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
            text="STUDENT PROFILE",
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
        self.scrollable_frame.pack(fill="both", expand=True, padx=60, pady=(20, 30))

        # Profile content container
        content_container = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white",
        )
        content_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Avatar section
        avatar_section = ctk.CTkFrame(
            content_container,
            fg_color="white",
        )
        avatar_section.pack(pady=(0, 30))

        # Avatar frame with border
        avatar_frame = ctk.CTkFrame(
            avatar_section,
            fg_color="white",
            corner_radius=20,
            border_width=3,
            border_color="#22C55E",
            width=280,
            height=360,
        )
        avatar_frame.pack()
        avatar_frame.pack_propagate(False)

        # Avatar placeholder
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text="",
            fg_color="#F0F0F0",
            corner_radius=17,
        )
        avatar_label.pack(fill="both", expand=True, padx=3, pady=3)

        # Avatar text if no image
        if not self.student_data.get("avatar"):
            avatar_text = ctk.CTkLabel(
                avatar_label,
                text="📷\nNo Photo",
                font=ctk.CTkFont(family="Arial", size=24),
                text_color="#999999",
            )
            avatar_text.place(relx=0.5, rely=0.5, anchor="center")

        # Information fields section
        info_section = ctk.CTkFrame(
            content_container,
            fg_color="white",
        )
        info_section.pack(fill="both", expand=True, pady=(20, 0))

        # Define all fields with their labels and values
        fields = [
            ("Student ID", self.student_data.get("student_id", "N/A")),
            ("Full Name", self.student_data.get("full_name", "N/A")),
            ("Date of Birth", self.student_data.get("dob", "N/A")),
            ("Gender", self.student_data.get("gender", "N/A")),
            ("Address", self.student_data.get("address", "N/A")),
            ("Contact Number", self.student_data.get("contact", "N/A")),
            ("Email", self.student_data.get("email", "N/A")),
            ("Major", self.student_data.get("major", "N/A")),
            ("Enrollment Year", self.student_data.get("enrollment_year", "N/A")),
        ]

        # Create field displays
        for label, value in fields:
            self.create_info_field(info_section, label, value)

        # Buttons section
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(20, 40))

        # Edit Profile button
        edit_btn = ctk.CTkButton(
            buttons_frame,
            text="✏️ Edit Profile",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2",
            text_color="white",
            width=250,
            height=60,
            corner_radius=15,
            command=self.edit_profile,
        )
        edit_btn.pack(side="right")

    def create_info_field(self, parent, label_text, value_text):
        """Create a single information field display"""
        field_container = ctk.CTkFrame(
            parent,
            fg_color="white",
        )
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

        # Value display (looks like entry but read-only)
        value_frame = ctk.CTkFrame(
            field_container,
            fg_color="#F8F8F8",
            corner_radius=10,
            border_width=2,
            border_color="#E0E0E0",
            height=50,
        )
        value_frame.pack(side="left", fill="x", expand=True)

        value_label = ctk.CTkLabel(
            value_frame,
            text=value_text,
            font=ctk.CTkFont(family="Arial", size=15),
            text_color="#000000",
            anchor="w",
        )
        value_label.pack(fill="both", expand=True, padx=20, pady=12)

    def edit_profile(self):
        """Open edit profile page"""
        if self.edit_callback:
            self.edit_callback()
        else:
            print("Edit profile clicked - callback not set")


# # Example usage
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("1400x900")
#     root.title("Student Profile")

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
#         "enrollment_year": "2021",
#     }

#     def go_back():
#         print("Going back to dashboard...")

#     def edit_profile():
#         print("Opening edit profile page...")

#     app = StudentProfile(container, sample_student, go_back, edit_profile)
#     root.mainloop()
