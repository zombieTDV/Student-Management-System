# main.py
import customtkinter as ctk
from controllers.auth_controller import AuthController

# from controllers.notification_controller import NotificationController
from views.login import LoginNotificationApp

# from views.forgot_password import ForgotPasswordApp
# from views.notification_detail import NotificationDetailApp
from models.database import db


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 1 Application")
        self.root.geometry("1400x800")

        # Initialize controllers
        self.auth_controller = AuthController()
        # self.notification_controller = NotificationController()

        # Container for views
        self.container = ctk.CTkFrame(root)
        self.container.pack(fill="both", expand=True)

        self.current_frame = None

        # Show login screen
        self.show_login()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_login(self):
        """Show login view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = LoginNotificationApp(
            self.container,
            self.handle_login,
            self.show_forgot_password,
            self.show_notification_detail,
            self.notification_controller,
        )

    def handle_login(self, username, password):
        """Handle login through controller"""
        result = self.auth_controller.login(username, password)
        return result

    # def show_forgot_password(self):
    #     """Show forgot password view"""
    #     for widget in self.container.winfo_children():
    #         widget.destroy()

    #     self.current_frame = ForgotPasswordApp(
    #         self.container,
    #         self.show_login,
    #         self.handle_password_recovery
    #     )

    def handle_password_recovery(self, email):
        """Handle password recovery through controller"""
        result = self.auth_controller.recover_password(email)
        return result

    # def show_notification_detail(self, notification_id):
    #     """Show notification detail view"""
    #     notification = self.notification_controller.\
    # get_notification_detail(notification_id)

    #     if notification:
    #         for widget in self.container.winfo_children():
    #             widget.destroy()

    #         self.current_frame = NotificationDetailApp(
    #             self.container,
    #             self.show_login,
    #             notification
    #         )

    def on_closing(self):
        """Handle application close"""
        db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApp(root)
    root.mainloop()
