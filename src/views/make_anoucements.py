import customtkinter as ctk
from datetime import datetime

from controllers.notifications_controller import NotificationsController
from controllers.auth_controller import AuthController


class MakeAnnouncement:
    def __init__(
        self,
        parent,
        back_callback,
        notifications_controller: "NotificationsController",
        auth_controller: "AuthController",
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.notifications_controller = notifications_controller
        self.auth_controller = auth_controller

        # Set theme (consistent with other views)
        ctk.set_appearance_mode("light")

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

        # Back arrow button (style from financial_summary_treeview.py)
        back_arrow = ctk.CTkLabel(
            header_frame,
            text="🔙",
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#AA00FF",  # Purple from mockup
            cursor="hand2",
        )
        back_arrow.pack(side="left", padx=(0, 30))
        if back_callback:
            back_arrow.bind("<Button-1>", lambda e: back_callback())

        # Title (with line break as in mockup)
        title_label = ctk.CTkLabel(
            header_frame,
            text="Make\nAnnoucement",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
            justify="left",
        )
        title_label.pack(side="left")

        # --- Content Container ---
        content_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="black",
        )
        content_container.pack(fill="both", expand=True, padx=40, pady=10)

        # 1. Title Entry
        self.title_entry = ctk.CTkEntry(
            content_container,
            placeholder_text="TITLE",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            border_width=0,
            fg_color="transparent",
            justify="center",  # <-- Add this to center the text
        )
        self.title_entry.pack(fill="x", padx=20, pady=(20, 10), ipady=10)

        # Separator line
        separator = ctk.CTkFrame(content_container, fg_color="#B0B0B0", height=2)
        separator.pack(fill="x", padx=20)

        # 2. Date Label (at the bottom)
        bottom_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom", padx=20, pady=10)

        today_str = datetime.now().strftime("date: %d/%m/%Y")
        date_label = ctk.CTkLabel(
            bottom_frame,
            text=today_str,
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="gray",
        )
        date_label.pack(side="right")

        # 3. Contents Textbox (fills remaining space)
        self.contents_textbox = ctk.CTkTextbox(
            content_container,
            font=ctk.CTkFont(family="Arial", size=16),
            border_width=0,
            fg_color="transparent",
            wrap="word",  # Wrap text
        )
        self.contents_textbox.pack(fill="both", expand=True, padx=20, pady=(10, 0))
        # Add "CONTENTS" placeholder
        self.contents_textbox.insert("1.0", "CONTENTS")
        self.contents_textbox.configure(text_color="gray")
        # Bind focus events to manage placeholder
        self.contents_textbox.bind("<FocusIn>", self._clear_placeholder)
        self.contents_textbox.bind("<FocusOut>", self._add_placeholder)

        # --- Footer (Post Button) ---
        footer_frame = ctk.CTkFrame(main_frame, fg_color="white")
        footer_frame.pack(fill="x", padx=40, pady=(20, 40))

        post_button = ctk.CTkButton(
            footer_frame,
            text="Post",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="white",
            width=180,  # Wider button
            height=60,  # Taller button
            corner_radius=15,
            command=self.post_announcement,
        )
        post_button.pack(side="left")  # Aligned left as in mockup

    def _clear_placeholder(self, event):
        """Remove placeholder text on focus"""
        if self.contents_textbox.get("1.0", "end-1c") == "CONTENTS":
            self.contents_textbox.delete("1.0", "end")
            self.contents_textbox.configure(text_color="black")

    def _add_placeholder(self, event):
        """Add placeholder text if empty"""
        if not self.contents_textbox.get("1.0", "end-1c"):
            self.contents_textbox.insert("1.0", "CONTENTS")
            self.contents_textbox.configure(text_color="gray")

    def post_announcement(self):
        """Core mechanism: Get data and call controller"""
        title = self.title_entry.get()
        content = self.contents_textbox.get("1.0", "end-1c")

        # Validation
        if not title or not content or content == "CONTENTS":
            self.show_error_popup("Title and Content are required.")
            return

        try:
            # Get author info from auth_controller
            # This is an assumption; change as needed
            author = self.auth_controller.current_account
            author_id = author._id
            # author_name = author.username

            # Call the notifications_controller
            # This is an assumption; change as needed
            success = self.notifications_controller.admin_post_announcement(
                title, content, author_id
            )

            if success:
                self.show_success_popup("Announcement posted successfully!")
                # Optionally clear the fields
                self.title_entry.delete(0, "end")
                self.contents_textbox.delete("1.0", "end")
                self._add_placeholder(None)
            else:
                self.show_error_popup("Failed to post announcement.")

        except Exception as e:
            self.show_error_popup(f"An error occurred: {e}")

    def show_success_popup(self, message):
        """Shows a success message popup (modal)"""
        success_dialog = ctk.CTkToplevel(self.parent)
        success_dialog.title("Success")
        success_dialog.geometry("400x200")
        success_dialog.grab_set()  # Make modal
        success_dialog.attributes("-topmost", True)

        ctk.CTkLabel(
            success_dialog,
            text="✓ " + message,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#22C55E",
            wraplength=360,
        ).pack(pady=40, padx=20)

        ctk.CTkButton(
            success_dialog,
            text="OK",
            width=120,
            height=40,
            command=success_dialog.destroy,
        ).pack(pady=(0, 20))

    def show_error_popup(self, message):
        """Shows an error message popup (modal)"""
        error_dialog = ctk.CTkToplevel(self.parent)
        error_dialog.title("Error")
        error_dialog.geometry("400x200")
        error_dialog.grab_set()
        error_dialog.attributes("-topmost", True)

        ctk.CTkLabel(
            error_dialog,
            text="⚠️ " + message,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#EF4444",  # Red
            wraplength=360,
        ).pack(pady=40, padx=20)

        ctk.CTkButton(
            error_dialog,
            text="OK",
            width=120,
            height=40,
            command=error_dialog.destroy,
        ).pack(pady=(0, 20))


# # Example usage (if you want to run this file directly)
# if __name__ == "__main__":
#     # --- Dummy Controller Classes for Testing ---
#     class DummyNotificationsController:
#         def create_announcement(self, author_id, author_name, title, content):
#             print("--- New Announcement ---")
#             print(f"From: {author_name} ({author_id})")
#             print(f"Title: {title}")
#             print(f"Content: {content}")
#             print("-------------------------")
#             # _return False # Use this to test the error case
#             return True

#     class DummyAuthController:
#         def get_current_user(self):
#             return {"id": "admin123", "name": "Dr. Admin"}

#     # --- Main App Setup ---

#     root = ctk.CTk()
#     root.geometry("1400x800")
#     root.title("Make Announcement Test")

#     def go_back_test():
#         print("Back button clicked!")

#     # Create dummy controllers
#     notif_controller = DummyNotificationsController()
#     auth_controller = DummyAuthController()

#     # Create the app
#     app = MakeAnnouncement(root, go_back_test, notif_controller, auth_controller)

#     root.mainloop()
