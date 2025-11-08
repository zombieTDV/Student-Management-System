import customtkinter as ctk


class NotificationDetailApp:
    def __init__(self, parent, back_callback, notification_data):
        self.parent = parent
        self.back_callback = back_callback
        self.notification_data = notification_data

        # Set theme and color
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Main container with rounded background
        main_frame = ctk.CTkFrame(
            parent, fg_color="white", corner_radius=50, border_width=0
        )
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Inner content frame with border
        content_frame = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=20,
            border_width=2,
            border_color="black",
        )
        content_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Title section (top bar with border)
        title_section = ctk.CTkFrame(
            content_frame,
            fg_color="#F5F5F5",
            corner_radius=0,
            border_width=0,
            height=100,
        )
        title_section.pack(fill="x", padx=0, pady=0)
        title_section.pack_propagate(False)

        # Add bottom border to title section
        title_border = ctk.CTkFrame(content_frame, fg_color="black", height=2)
        title_border.pack(fill="x", padx=0, pady=0)

        # Title text
        title_label = ctk.CTkLabel(
            title_section,
            text=notification_data.title,
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            text_color="black",
        )
        title_label.pack(expand=True)

        # Content section (scrollable)
        content_scroll = ctk.CTkScrollableFrame(
            content_frame, fg_color="white", corner_radius=0
        )
        content_scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Content text (italic)
        content_label = ctk.CTkLabel(
            content_scroll,
            text=notification_data.content,
            font=ctk.CTkFont(family="Arial", size=18, slant="italic"),
            text_color="black",
            justify="left",
            wraplength=1200,
        )
        content_label.pack(fill="both", expand=True, pady=20)

        # Date label (bottom right)
        date_label = ctk.CTkLabel(
            content_frame,
            text=notification_data.createAt,
            font=ctk.CTkFont(family="Arial", size=14),
            text_color="black",
        )
        date_label.pack(side="bottom", anchor="e", padx=30, pady=20)

        # Back button
        back_btn = ctk.CTkButton(
            main_frame,
            text="← Back",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="white",
            height=40,
            width=120,
            corner_radius=10,
            command=self.back_callback,
        )
        back_btn.place(x=40, y=40)


# Example standalone usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")

    sample_notification = {
        "title": "System Update Available",
        "content": "A new system update is now available for download.\
            This update includes important security patches,\
                performance improvements, and new features.\
                Please make sure to save your work before proceeding with the update.\
                    The installation process may take 15-20 minutes \
                        and will require a system restart.",
        "date": "date: 11/04/2025",
    }

    def dummy_back():
        print("Back clicked")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    app = NotificationDetailApp(container, dummy_back, sample_notification)
    root.mainloop()
