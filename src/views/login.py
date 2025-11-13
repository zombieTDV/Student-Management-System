import customtkinter as ctk

from controllers.notifications_controller import NotificationsController


class LoginNotificationApp:
    def __init__(
        self,
        parent,
        forgot_password_callback,
        detail_callback,
        student_dashboard_callback,
        handle_login_callback,
        admin_dashboard_callback,
        notifications_controller: NotificationsController,
    ):
        self.parent = parent
        self.forgot_password_callback = forgot_password_callback
        self.detail_callback = detail_callback  # Store detail page callback
        self.student_dashboard_callback = student_dashboard_callback
        self.handle_login_callback = handle_login_callback
        self.admin_dashboard_callback = admin_dashboard_callback

        self.notifications_controller = notifications_controller

        # Set theme and color
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Main container with green background
        main_frame = ctk.CTkFrame(parent, fg_color="#4ADE80", corner_radius=0)
        main_frame.pack(expand=True, fill="both")

        # Left side - Notifications with Scrollbar
        notif_frame = ctk.CTkFrame(
            main_frame, fg_color="white", corner_radius=30, border_width=0
        )
        notif_frame.place(relx=0.05, rely=0.12, relwidth=0.45, relheight=0.70)

        # Notifications title
        notif_title = ctk.CTkLabel(
            notif_frame,
            text="NOTIFICATIONS",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#22C55E",
        )
        notif_title.pack(pady=(30, 20))

        # Create scrollable frame for notifications
        self.scrollable_frame = ctk.CTkScrollableFrame(
            notif_frame,
            fg_color="white",
            corner_radius=0,
            scrollbar_button_color="#22C55E",
            scrollbar_button_hover_color="#16A34A",
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        # Sample notifications data (you can load this from database/API)
        self.notifications = (
            self.notifications_controller.student_view_all_notifications()
        )

        # Load notifications
        self.load_notifications()

        # Right side - Login
        login_frame = ctk.CTkFrame(
            main_frame, fg_color="white", corner_radius=30, border_width=0
        )
        login_frame.place(relx=0.53, rely=0.12, relwidth=0.30, relheight=0.70)

        # Group 1 title
        group_title = ctk.CTkLabel(
            login_frame,
            text="GROUP 1",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="#22C55E",
        )
        group_title.pack(pady=(40, 10))

        # Login title
        login_title = ctk.CTkLabel(
            login_frame,
            text="LOGIN",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#EF4444",
        )
        login_title.pack(pady=(0, 40))

        # Login Account input
        self.account_entry = ctk.CTkEntry(
            login_frame,
            font=ctk.CTkFont(family="Arial", size=16),
            placeholder_text="Login Account",
            height=50,
            corner_radius=10,
            border_width=2,
            border_color="gray",
        )
        self.account_entry.pack(padx=40, pady=15, fill="x")

        # Password input
        self.password_entry = ctk.CTkEntry(
            login_frame,
            font=ctk.CTkFont(family="Arial", size=16),
            placeholder_text="Password",
            show="●",
            height=50,
            corner_radius=10,
            border_width=2,
            border_color="gray",
        )
        self.password_entry.pack(padx=40, pady=15, fill="x")

        # Continue button
        continue_btn = ctk.CTkButton(
            login_frame,
            text="Continue",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="white",
            height=50,
            corner_radius=10,
            command=self.login,
        )
        continue_btn.pack(padx=40, pady=30, fill="x")

        # Forgot password link
        forgot_label = ctk.CTkLabel(
            login_frame,
            text="Forgot password?",
            font=ctk.CTkFont(family="Arial", size=14, underline=True),
            text_color="#EF4444",
            cursor="hand2",
        )
        forgot_label.pack(pady=10)
        forgot_label.bind("<Button-1>", lambda e: self.forgot_password())

    def load_notifications(self):
        """Load notifications into scrollable frame"""
        for notif in self.notifications:
            notif_item = ctk.CTkFrame(
                self.scrollable_frame,
                fg_color="white",
                corner_radius=15,
                border_width=2,
                border_color="black",
            )
            notif_item.pack(padx=20, pady=10, fill="x")

            # Make the frame clickable
            notif_item.configure(cursor="hand2")
            notif_item.bind("<Button-1>", lambda e, n=notif: self.open_detail(n))

            title_label = ctk.CTkLabel(
                notif_item,
                text=notif.title,
                font=ctk.CTkFont(family="Arial", size=14, weight="bold"),
                text_color="#22C55E",
                anchor="w",
                cursor="hand2",
            )
            title_label.pack(padx=15, pady=(15, 5), anchor="w", fill="x")
            title_label.bind("<Button-1>", lambda e, n=notif: self.open_detail(n))

            date_label = ctk.CTkLabel(
                notif_item,
                text=notif.createAt,
                font=ctk.CTkFont(family="Arial", size=12),
                text_color="black",
                anchor="w",
                cursor="hand2",
            )
            date_label.pack(padx=15, pady=(0, 15), anchor="w", fill="x")
            date_label.bind("<Button-1>", lambda e, n=notif: self.open_detail(n))

    def open_detail(self, notification_data):
        """Open notification detail page"""
        self.detail_callback(notification_data)

    def add_notification(self, title, date):
        """Dynamically add a new notification"""
        self.notifications.insert(0, {"title": title, "date": date})

        # Clear and reload all notifications
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.load_notifications()

    def login(self):
        account = self.account_entry.get()
        password = self.password_entry.get()

        login_result = self.handle_login_callback(account, password)
        if login_result["success"] is True:
            if login_result["user"].role == "student":
                self.student_dashboard_callback()
            elif login_result["user"].role == "admin":
                self.admin_dashboard_callback()
        else:
            # Show popup for invalid credentials
            self.show_error_popup("Invalid username or password")

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

    def forgot_password(self):
        self.forgot_password_callback()


# # Example: Add a new notification after 3 seconds
# def add_new_notification():
#     app.add_notification("New Notification!", "date: 11/04/2025")

# root.after(3000, add_new_notification)  # Add notification after 3 seconds
