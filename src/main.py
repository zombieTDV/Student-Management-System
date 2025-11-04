import customtkinter as ctk
from views.login import LoginNotificationApp
from views.forgot_password import ForgotPasswordApp
from views.notification_detail import NotificationDetailApp


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 1 Application")
        self.root.geometry("1400x800")

        # Container to hold different screens
        self.container = ctk.CTkFrame(root)
        self.container.pack(fill="both", expand=True)

        # Store current frame
        self.current_frame = None

        # Show login screen first
        self.show_login()

    def show_login(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Show login screen
        self.current_frame = LoginNotificationApp(
            self.container,
            self.show_forgot_password,
            self.show_notification_detail,  # Pass detail page callback
        )

    def show_forgot_password(self):
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Show forgot password screen
        self.current_frame = ForgotPasswordApp(self.container, self.show_login)

    def show_notification_detail(self, notification_data):
        """Show notification detail page"""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()

        # Show notification detail screen
        self.current_frame = NotificationDetailApp(
            self.container,
            self.show_login,  # Back button goes to login
            notification_data,
        )


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApp(root)
    root.mainloop()
