import customtkinter as ctk

from PIL import Image
import os


from controllers.auth_controller import AuthController


class StudentDashboard:
    def __init__(
        self,
        parent,
        auth_controller: AuthController,
        student_dashboard_view_notifications_callback=None,
        show_financial_summary_callback=None,
        show_payment_callback=None,
        show_update_info_callback=None,
        show_more_info_callback=None,
    ):
        self.parent = parent
        self.student_data = {
            "student_id": auth_controller.current_account._id,
            "full_name": auth_controller.current_account.fullName,
            "gender": auth_controller.current_account.gender,
            "dob": auth_controller.current_account.dob,
            "enrollment_year": auth_controller.current_account.createAt,
            "major": auth_controller.current_account.major,
            "avatar": auth_controller.current_account.imageURL,
        }

        self.student_dashboard_view_notifications_callback = (
            student_dashboard_view_notifications_callback
        )
        self.show_financial_summary_callback = show_financial_summary_callback
        self.show_payment_callback = show_payment_callback

        self.show_more_info_callback = show_more_info_callback
        self.show_update_info_callback = show_update_info_callback

        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Main container
        main_frame = ctk.CTkFrame(parent, fg_color="#E8E8E8", corner_radius=50)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Student Info Section
        info_section = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=30,
            border_width=2,
            border_color="#D0D0D0",
        )
        info_section.pack(fill="x", padx=40, pady=(40, 20))

        # Title with border
        title_frame = ctk.CTkFrame(
            info_section, fg_color="white", corner_radius=0, height=60
        )
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            title_frame,
            text="Student's Info",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="#22C55E",
        )
        title_label.pack(side="left", padx=30, pady=15)

        # Separator line
        separator = ctk.CTkFrame(info_section, fg_color="#D0D0D0", height=2)
        separator.pack(fill="x", padx=0, pady=0)

        # Content area
        content_frame = ctk.CTkFrame(info_section, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Left side - Avatar
        left_frame = ctk.CTkFrame(content_frame, fg_color="white")
        left_frame.pack(side="left", padx=(0, 30))

        # Avatar placeholder
        avatar_frame = ctk.CTkFrame(
            left_frame,
            fg_color="white",
            # corner_radius=20,
            border_width=3,
            border_color="#22C55E",
            width=250,
            height=320,
        )
        avatar_frame.pack()
        avatar_frame.pack_propagate(False)

        avatar_label = ctk.CTkLabel(avatar_frame, text="", fg_color="#F0F0F0")
        avatar_label.pack(fill="both", expand=True, padx=3, pady=3)

        # Load student's avatar if available
        avatar_path = self.student_data.get("avatar")
        if avatar_path and os.path.exists(avatar_path):
            try:
                img = Image.open(avatar_path).convert("RGBA")
                img = img.resize((250, 320), Image.Resampling.LANCZOS)
                self.avatar_ctk_img = ctk.CTkImage(
                    light_image=img, dark_image=img, size=(250, 320)
                )
                avatar_label.configure(image=self.avatar_ctk_img, text="")
            except Exception as e:
                print("Failed to load avatar:", e)
        else:
            avatar_label.configure(
                text="No Avatar", font=ctk.CTkFont(size=14, slant="italic")
            )

        # Right side - Info fields
        right_frame = ctk.CTkFrame(content_frame, fg_color="white")
        right_frame.pack(side="left", fill="both", expand=True)

        # Create grid for fields
        fields = [
            (
                "Student's ID",
                self.student_data["student_id"],
                "Gender",
                self.student_data["gender"],
            ),
            (
                "Full Name",
                self.student_data["full_name"],
                "Enrollment year",
                self.student_data["enrollment_year"],
            ),
            (
                "Date of birth",
                self.student_data["dob"],
                "Major",
                self.student_data["major"],
            ),
        ]

        for i, (label1, value1, label2, value2) in enumerate(fields):
            row_frame = ctk.CTkFrame(right_frame, fg_color="white")
            row_frame.pack(fill="x", pady=10)

            # Left column
            left_col = ctk.CTkFrame(row_frame, fg_color="white")
            left_col.pack(side="left", fill="x", expand=True, padx=(0, 15))

            field1 = ctk.CTkEntry(
                left_col,
                placeholder_text=label1,
                font=ctk.CTkFont(family="Arial", size=14),
                height=50,
                corner_radius=10,
                border_width=2,
                border_color="black",
                fg_color="white",
            )
            field1.pack(fill="x")
            field1.insert(0, value1)
            field1.configure(state="readonly")

            # Right column
            right_col = ctk.CTkFrame(row_frame, fg_color="white")
            right_col.pack(side="left", fill="x", expand=True)

            field2 = ctk.CTkEntry(
                right_col,
                placeholder_text=label2,
                font=ctk.CTkFont(family="Arial", size=14),
                height=50,
                corner_radius=10,
                border_width=2,
                border_color="black",
                fg_color="white",
            )
            field2.pack(fill="x")
            field2.insert(0, value2)
            field2.configure(state="readonly")

        # More information link
        more_info = ctk.CTkLabel(
            info_section,
            text="More information",
            font=ctk.CTkFont(family="Arial", size=14, slant="italic", underline=True),
            text_color="#0066CC",
            cursor="hand2",
        )
        more_info.pack(anchor="e", padx=40, pady=(0, 20))
        more_info.bind("<Button-1>", lambda e: self.show_more_info_callback())

        # Action buttons section
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="#E8E8E8")
        buttons_frame.pack(fill="x", padx=40, pady=(20, 40))

        # Button definitions
        buttons = [
            {
                "text": "Update Info",
                "icon": "ℹ️",
                "color": "#2196F3",
                "command": self.show_update_info_callback,
            },
            {
                "text": "View Notifications",
                "icon": "🔔",
                "color": "#8BC34A",
                "command": self.student_dashboard_view_notifications_callback,
            },
            {
                "text": "Financial\nSummary",
                "icon": "📚",
                "color": "#FF4081",
                "command": self.show_financial_summary_callback,
            },
            {
                "text": "Payment",
                "icon": "💳",
                "color": "#4CAF50",
                "command": self.show_payment_callback,
            },
        ]

        for btn_data in buttons:
            btn_container = ctk.CTkFrame(
                buttons_frame,
                fg_color="white",
                corner_radius=20,
                border_width=2,
                border_color="black",
            )
            btn_container.pack(side="left", fill="both", expand=True, padx=10)

            # Icon
            icon_label = ctk.CTkLabel(
                btn_container, text=btn_data["icon"], font=ctk.CTkFont(size=30)
            )
            icon_label.pack(pady=(30, 10))

            # Button
            btn = ctk.CTkButton(
                btn_container,
                text=btn_data["text"],
                font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
                fg_color=btn_data["color"],
                hover_color=self.darken_color(btn_data["color"]),
                text_color="white",
                height=40,
                corner_radius=10,
                command=btn_data["command"],
            )
            btn.pack(padx=20, pady=(0, 30), fill="x")

    def darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        darker = tuple(int(c * 0.8) for c in rgb)
        return "#%02x%02x%02x" % darker


# # Example usage
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("1400x800")
#     root.title("Student Dashboard")

#     container = ctk.CTkFrame(root)
#     container.pack(fill="both", expand=True)

#     sample_student = {
#         "student_id": "2021001",
#         "full_name": "John Doe",
#         "gender": "Male",
#         "dob": "01/15/2000",
#         "enrollment_year": "2021",
#         "major": "Computer Science",
#     }

#     app = StudentDashboard(container, sample_student)
#     root.mainloop()
