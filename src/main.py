# main.py
import customtkinter as ctk
from controllers.auth_controller import AuthController
from controllers.notifications_controller import NotificationsController
from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController

from views.forgot_password import ForgotPasswordApp
from views.notification_detail import NotificationDetailApp
from views.login import LoginNotificationApp

from views.student.student_dashboard import StudentDashboard
from views.student.student_profile import StudentProfile
from views.student.update_student_profile import UpdateStudentProfile
from views.student.student_dashboard_view_notifications import (
    StudentDashboardViewNotification,
)
from views.student.financial_summary import FinancialSummaryApp
from views.student.payment import PaymentApp

from views.admin.admin_dashboard import AdminDashboard
from views.admin.student_management import StudentManagement
from views.admin.make_anoucements import MakeAnnouncement
from views.admin.fee_management import FeeManagement


from models.database import db


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 1 Application")
        self.root.geometry("1400x800")

        # Initialize controllers
        self.auth_controller = AuthController()
        self.notifications_controller = NotificationsController()
        self.student_controller = StudentController()
        self.fee_controller = FeeController()

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
            self.show_forgot_password,
            self.show_notification_detail_onLogin,
            self.show_student_dashboard,
            self.handle_login,
            self.show_admin_dashboard,
            notifications_controller=self.notifications_controller,
        )

    def handle_login(self, username, password):
        """Handle login through controller"""
        result = self.auth_controller.login(username, password)
        return result

    def show_forgot_password(self):
        """Show forgot password view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = ForgotPasswordApp(
            self.container,
            back_callback=self.show_login,
            # self.handle_password_recovery
            # email_sent_callback=self.show_email_sent,
            auth_controller=self.auth_controller,
        )

    def handle_password_recovery(self, email):
        """Handle password recovery through controller"""
        result = self.auth_controller.recover_password(email)
        return result

    def show_notification_detail_onLogin(self, notification_data):
        """Show notification detail view"""
        if notification_data:
            for widget in self.container.winfo_children():
                widget.destroy()

            self.current_frame = NotificationDetailApp(
                self.container, self.show_login, notification_data
            )

    # =======================================================
    def show_admin_dashboard(self):
        """Show admin dashboard view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = AdminDashboard(
            self.container,
            self.show_login,
            self.show_student_management,
            self.show_make_announcement,
            fee_management_callback=self.show_fee_management,
            transaction_callback=None,
        )

    def show_student_management(self):
        """Show student management view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = StudentManagement(
            self.container,
            back_callback=self.show_admin_dashboard,
            student_controller=self.student_controller,
            auth_controller=self.auth_controller,
        )

    def show_fee_management(self):
        """Show student management view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = FeeManagement(
            self.container,
            back_callback=self.show_admin_dashboard,
            student_controller=self.student_controller,
            auth_controller=self.auth_controller,
            fee_controller=self.fee_controller,
        )

    def show_make_announcement(self):
        """Show make announcement view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = MakeAnnouncement(
            self.container,
            self.show_admin_dashboard,
            self.notifications_controller,
            self.auth_controller,
        )

    # =============================================
    def show_student_dashboard(self):
        """Show student dashboard view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = StudentDashboard(
            self.container,
            auth_controller=self.auth_controller,
            student_dashboard_view_notifications_callback=self.show_student_dashboard_view_notifications,
            show_financial_summary_callback=self.show_financial_summary,
            show_payment_callback=self.show_payment,
            show_more_info_callback=self.show_student_profile,
            show_update_info_callback=self.show_update_student_profile_on_studentDashboard,
        )

    def show_notification_detail_onDashBoard(self, notification_data):
        """Show notification detail view"""
        if notification_data:
            for widget in self.container.winfo_children():
                widget.destroy()

            self.current_frame = NotificationDetailApp(
                self.container,
                self.show_student_dashboard_view_notifications,
                notification_data,
            )

    def show_student_profile(self):
        """Show student profile via more-information"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = StudentProfile(
            self.container,
            auth_controller=self.auth_controller,
            back_callback=self.show_student_dashboard,
            edit_callback=self.show_update_student_profile_on_moreInfo,
        )

    def show_update_student_profile_on_moreInfo(self):
        """Show update student profile via more-information"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = UpdateStudentProfile(
            self.container,
            back_callback=self.show_student_profile,
            auth_controller=self.auth_controller,
            student_controller=self.student_controller,
        )

    def show_update_student_profile_on_studentDashboard(self):  # BUGS
        """Show update student profile via student dashboard"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = UpdateStudentProfile(
            self.container,
            back_callback=self.show_student_dashboard,
            auth_controller=self.auth_controller,
            student_controller=self.student_controller,
        )

    def show_student_dashboard_view_notifications(self):
        """Show the option of view notification for student dashboard"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = StudentDashboardViewNotification(
            self.container,
            self.show_student_dashboard,
            self.show_notification_detail_onDashBoard,
            self.notifications_controller,
        )

    def show_financial_summary(self):
        """Show student dashboard's financial summary view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = FinancialSummaryApp(
            self.container, self.show_student_dashboard
        )

    def show_payment(self):
        """Show student payment view"""
        for widget in self.container.winfo_children():
            widget.destroy()

        self.current_frame = PaymentApp(
            self.container, self.show_student_dashboard, None, None
        )

    # ======================================================
    def on_closing(self):
        """Handle application close"""
        db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApp(root)
    root.mainloop()
