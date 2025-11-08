import customtkinter as ctk


class AdminDashboard:
    def __init__(
        self,
        parent,
        back_callback,
        student_management_callback,
        make_announcement_callback,
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.student_management_callback = student_management_callback
        self.make_announcement_callback = make_announcement_callback

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

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
        header_frame.pack(fill="x", padx=40, pady=(40, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Administration",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        title_label.pack(side="left")

        # Make Announcement button (top right)
        announcement_btn = ctk.CTkButton(
            header_frame,
            text="Make\nAnnouncement",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#FF6B6B",
            hover_color="#FF5252",
            text_color="white",
            width=200,
            height=80,
            corner_radius=15,
            command=self.make_announcement_callback,
        )
        announcement_btn.pack(side="right")

        # Main content area
        content_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
        content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Left side - Menu sections
        left_frame = ctk.CTkFrame(
            content_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="#B0B0B0",
        )
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        # ACCOUNT AND AUTHENTICATION section
        self.create_section_header(left_frame, "ACCOUNT AND AUTHENTICATION")
        self.create_menu_item(left_frame, "Admin", self.manage_admin)
        self.create_menu_item(left_frame, "Students", self.manage_students)

        # FEE AND TRANSACTION section
        self.create_section_header(left_frame, "FEE AND TRANSACTION")
        self.create_menu_item(left_frame, "Fee", self.manage_fee)
        self.create_menu_item(left_frame, "Transaction", self.manage_transaction)

        # NOTIFICATION section
        self.create_section_header(left_frame, "NOTIFICATION")

        # Notification content area (expandable)
        notif_content = ctk.CTkFrame(left_frame, fg_color="white", height=100)
        notif_content.pack(fill="both", expand=True, padx=2, pady=(0, 2))

        # Right side - Back to Login button
        right_frame = ctk.CTkFrame(content_frame, fg_color="white")
        right_frame.pack(side="right", fill="y")

        # Spacer to push button to bottom
        spacer = ctk.CTkFrame(right_frame, fg_color="white")
        spacer.pack(fill="both", expand=True)

        # Back to Login button
        if back_callback:
            back_btn = ctk.CTkButton(
                right_frame,
                text="Back to Login",
                font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
                fg_color="#FF0000",
                hover_color="#CC0000",
                text_color="white",
                width=250,
                height=80,
                corner_radius=15,
                command=self.back_callback,
            )
            back_btn.pack(pady=(0, 20))

    def create_section_header(self, parent, text):
        """Create a section header with blue background"""
        header_frame = ctk.CTkFrame(
            parent, fg_color="#ADD8E6", corner_radius=0, height=60
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        header_label = ctk.CTkLabel(
            header_frame,
            text=text,
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="black",
        )
        header_label.pack(expand=True)

        # Add bottom border
        border = ctk.CTkFrame(parent, fg_color="#B0B0B0", height=2)
        border.pack(fill="x", padx=0, pady=0)

    def create_menu_item(self, parent, text, command):
        """Create a clickable menu item"""
        item_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=0, height=60)
        item_frame.pack(fill="x", padx=0, pady=0)
        item_frame.pack_propagate(False)

        # Make it hoverable
        item_frame.bind("<Enter>", lambda e: item_frame.configure(fg_color="#F0F0F0"))
        item_frame.bind("<Leave>", lambda e: item_frame.configure(fg_color="white"))
        item_frame.bind("<Button-1>", lambda e: command())

        item_label = ctk.CTkLabel(
            item_frame,
            text=text,
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="#0000FF",
            cursor="hand2",
        )
        item_label.pack(side="left", padx=20, pady=15)
        item_label.bind("<Button-1>", lambda e: command())

        # Add bottom border
        border = ctk.CTkFrame(parent, fg_color="#B0B0B0", height=2)
        border.pack(fill="x", padx=0, pady=0)

    def manage_admin(self):
        """Handle admin management"""
        print("Admin management clicked")

    def manage_students(self):
        """Handle student management"""
        self.student_management_callback()

    def manage_fee(self):
        """Handle fee management"""
        print("Fee management clicked")

    def manage_transaction(self):
        """Handle transaction management"""
        print("Transaction management clicked")


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Admin Dashboard")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    def back_to_login():
        print("Back to login clicked")

    app = AdminDashboard(container, back_to_login)
    root.mainloop()
