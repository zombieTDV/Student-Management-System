import customtkinter as ctk


class StudentDashboardViewNotification:
    def __init__(
        self,
        parent,
        back_callback=None,
        detail_callback=None,
        notification_controller=None,
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
            notifications = self.notification_controller.get_all_notifications()
        else:
            # Sample data if no controller
            notifications = [
                {
                    "_id": "1",
                    "title": "Welcome to the System",
                    "date": "date: 11/07/2025",
                    "content": "Welcome to our student management system. \
                        Please update your profile information.",
                },
                {
                    "_id": "2",
                    "title": "Midterm Exam Schedule Released",
                    "date": "date: 11/06/2025",
                    "content": "The midterm examination schedule has been posted. \
                        Please check your student portal.",
                },
                {
                    "_id": "3",
                    "title": "Fee Payment Reminder",
                    "date": "date: 11/05/2025",
                    "content": "This is a reminder that tuition fees are due \
                        by the end of this month.",
                },
                {
                    "_id": "4",
                    "title": "Campus Event: Tech Conference",
                    "date": "date: 11/04/2025",
                    "content": "Join us for an exciting tech \
                        conference featuring industry leaders next week.",
                },
                {
                    "_id": "5",
                    "title": "Library Hours Extended",
                    "date": "date: 11/03/2025",
                    "content": "The library will now be open until 10 PM \
                        on weekdays during exam season.",
                },
                {
                    "_id": "6",
                    "title": "Career Fair Announcement",
                    "date": "date: 11/02/2025",
                    "content": "Annual career fair will be held next month.\
                        Register early to meet top employers.",
                },
            ]

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
            text=f"News: {notification.get('title', '...')}",
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
            text=notification.get("date", "date: xx/xx/xxxx"),
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="black",
            anchor="w",
            cursor="hand2",
        )
        date_label.pack(anchor="w")
        date_label.bind("<Button-1>", lambda e, n=notification: self.open_detail(n))

    def open_detail(self, notification):
        """Open notification detail page"""
        if self.detail_callback:
            # Pass notification ID or full data
            notification_id = notification.get("_id")
            if notification_id:
                self.detail_callback(notification_id)
            else:
                # If no ID, pass the full notification data
                self.detail_callback(notification)
        else:
            print(f"Clicked notification: {notification.get('title')}")


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
