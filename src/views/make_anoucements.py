import customtkinter as ctk
from datetime import datetime

from controllers.notifications_controller import NotificationsController
from controllers.auth_controller import AuthController


class MakeAnnouncement:
    def __init__(
        self,
        parent,
        back_callback,
        notifications_controller: NotificationsController,
        auth_controller: AuthController,
    ):
        self.parent = parent
        self.back_callback = back_callback

        self.notifications_controller = notifications_controller
        self.auth_controller = auth_controller

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
        header_frame.pack(anchor="w", padx=60, pady=(40, 30))

        # Back arrow button
        back_arrow = ctk.CTkLabel(
            header_frame,
            text="🔙",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#FF7B7B",
            cursor="hand2",
        )
        back_arrow.pack(side="left", padx=(0, 20))
        if back_callback:
            back_arrow.bind("<Button-1>", lambda e: back_callback())

        # Header title
        header_label = ctk.CTkLabel(
            header_frame,
            text="Make\nAnnoucement",
            font=ctk.CTkFont(family="Arial", size=42, weight="bold"),
            text_color="#22C55E",
        )
        header_label.pack(side="left")

        # Content container with border
        content_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="black",
        )
        content_container.pack(fill="both", expand=True, padx=60, pady=(0, 30))

        # Title section
        title_section = ctk.CTkFrame(
            content_container, fg_color="#F5F5F5", corner_radius=0, height=80
        )
        title_section.pack(fill="x", padx=0, pady=0)
        title_section.pack_propagate(False)

        title_label = ctk.CTkLabel(
            title_section,
            text="TITLE",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color="black",
        )
        title_label.pack(expand=True)

        # Title border
        title_border = ctk.CTkFrame(content_container, fg_color="black", height=2)
        title_border.pack(fill="x", padx=0, pady=0)

        # Title input
        title_input_frame = ctk.CTkFrame(content_container, fg_color="white")
        title_input_frame.pack(fill="x", padx=20, pady=(15, 0))

        self.title_entry = ctk.CTkEntry(
            title_input_frame,
            font=ctk.CTkFont(family="Arial", size=16),
            placeholder_text="Enter announcement title...",
            height=40,
            border_width=0,
            fg_color="white",
        )
        self.title_entry.pack(fill="x", padx=10, pady=5)

        # Contents section label
        contents_label = ctk.CTkLabel(
            content_container,
            text="CONTENTS",
            font=ctk.CTkFont(family="Arial", size=18, slant="italic"),
            text_color="gray",
        )
        contents_label.pack(pady=(20, 10))

        # Contents input (multiline textbox)
        self.contents_text = ctk.CTkTextbox(
            content_container,
            font=ctk.CTkFont(family="Arial", size=14),
            fg_color="white",
            border_width=0,
            wrap="word",
        )
        self.contents_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Date label (bottom right)
        self.date_label = ctk.CTkLabel(
            content_container,
            text=f"date: {datetime.now().strftime('%m/%d/%Y')}",
            font=ctk.CTkFont(family="Arial", size=12),
            text_color="black",
        )
        self.date_label.pack(side="bottom", anchor="e", padx=30, pady=(0, 20))

        # Post button
        post_btn = ctk.CTkButton(
            main_frame,
            text="Post",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=220,
            height=70,
            corner_radius=20,
            command=self.post_announcement,
        )
        post_btn.pack(side="left", padx=(50, 150))

    def post_announcement(self):
        """Handle post announcement"""
        title = self.title_entry.get().strip()
        contents = self.contents_text.get("1.0", "end-1c").strip()
        date = datetime.now().strftime("%m/%d/%Y")

        # Validate
        if not title:
            self.show_error("Title is required!")
            return

        if not contents:
            self.show_error("Contents is required!")
            return

        # Create announcement data
        announcement = {"title": title, "content": contents, "date": f"date: {date}"}

        self.notifications_controller.admin_post_announcement(
            announcement["title"],
            announcement["content"],
            self.auth_controller.current_account._id,
        )

        print(f"Posting announcement: {announcement}")
        # TODO: Save to MongoDB via NotificationController

        # Show success and clear form
        self.show_success()
        self.clear_form()

    def show_error(self, message):
        """Show error dialog"""
        error_dialog = ctk.CTkToplevel(self.parent)
        error_dialog.title("Error")
        error_dialog.geometry("350x150")
        error_dialog.grab_set()

        ctk.CTkLabel(
            error_dialog,
            text=f"⚠️ {message}",
            font=ctk.CTkFont(size=16),
            text_color="#FF0000",
        ).pack(pady=30)
        ctk.CTkButton(
            error_dialog, text="OK", width=100, command=error_dialog.destroy
        ).pack(pady=10)

    def show_success(self):
        """Show success dialog"""
        success_dialog = ctk.CTkToplevel(self.parent)
        success_dialog.title("Success")
        success_dialog.geometry("350x150")
        success_dialog.grab_set()

        ctk.CTkLabel(
            success_dialog,
            text="✓ Announcement Posted!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#22C55E",
        ).pack(pady=30)
        ctk.CTkButton(
            success_dialog, text="OK", width=100, command=success_dialog.destroy
        ).pack(pady=10)

    def clear_form(self):
        """Clear the form"""
        self.title_entry.delete(0, "end")
        self.contents_text.delete("1.0", "end")
        self.date_label.configure(text=f"date: {datetime.now().strftime('%m/%d/%Y')}")


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Make Announcement")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    def go_back():
        print("Going back...")

    app = MakeAnnouncement(container, go_back)
    root.mainloop()
