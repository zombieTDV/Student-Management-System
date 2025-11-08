import customtkinter as ctk

from controllers.notifications_controller import NotificationsController


class StudentDashboardViewNotification:
    def __init__(
        self,
        parent,
        back_callback,
        detail_callback,
        notification_controller: NotificationsController,
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.detail_callback = detail_callback
        self.notification_controller = notification_controller

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
        header_frame.pack(fill="x", padx=60, pady=(40, 30))

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
            text="NOTIFICATIONS",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        header_label.pack(side="left")

        # Scrollable frame for notifications
        self.scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=0,
            scrollbar_button_color="#22C55E",
            scrollbar_button_hover_color="#16A34A",
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=60, pady=(0, 40))

        # Load notifications
        self.load_notifications()

    def load_notifications(self):
        """Load notifications from controller or sample data"""
        if self.notification_controller:
            notifications = (
                self.notification_controller.student_view_all_notifications()
            )
        else:
            # Sample data if no controller
            print("Can not fetch any annoucement datas")

        # Create notification items
        for notif in notifications:
            self.create_notification_item(notif)

    def create_notification_item(self, notification):
        """Create a single notification item"""
        notif_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color="black",
        )
        notif_frame.pack(fill="x", padx=20, pady=15)

        # Make it clickable
        notif_frame.configure(cursor="hand2")
        notif_frame.bind(
            "<Enter>", lambda e: notif_frame.configure(border_color="#22C55E")
        )
        notif_frame.bind(
            "<Leave>", lambda e: notif_frame.configure(border_color="black")
        )
        notif_frame.bind("<Button-1>", lambda e, n=notification: self.open_detail(n))

        # Content container
        content_frame = ctk.CTkFrame(notif_frame, fg_color="white")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        content_frame.bind("<Button-1>", lambda e, n=notification: self.open_detail(n))

        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=f"News: {notification.title}",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color="#22C55E",
            anchor="w",
            cursor="hand2",
        )
        title_label.pack(anchor="w", pady=(0, 5))
        title_label.bind("<Button-1>", lambda e, n=notification: self.open_detail(n))

        # Date
        date_label = ctk.CTkLabel(
            content_frame,
            text=notification.createAt,
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="black",
            anchor="w",
            cursor="hand2",
        )
        date_label.pack(anchor="w")
        date_label.bind("<Button-1>", lambda e, n=notification: self.open_detail(n))

    def open_detail(self, notification_data):
        """Open notification detail page"""
        self.detail_callback(notification_data)


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    root.title("Notifications")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    def go_back():
        print("Going back...")

    def show_detail(notification_id):
        print(f"Show detail for notification: {notification_id}")

    app = StudentDashboardViewNotification(container, go_back, show_detail)
    root.mainloop()
