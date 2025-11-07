import customtkinter as ctk


class EmailSent:
    def __init__(self, parent, back_callback=None):
        self.parent = parent
        self.back_callback = back_callback

        # Set theme and color
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Main container with white background
        main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="white",
            corner_radius=50,
            border_width=3,
            border_color="black",
        )
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Group 1 title
        group_title = ctk.CTkLabel(
            main_frame,
            text="GROUP 1",
            font=ctk.CTkFont(family="Arial", size=56, weight="bold"),
            text_color="#22C55E",
        )
        group_title.pack(pady=(80, 30))

        # Password Recovery title
        recovery_title = ctk.CTkLabel(
            main_frame,
            text="Password Recovery",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#EF4444",
        )
        recovery_title.pack(pady=(0, 100))

        # Email sent message
        email_sent_label = ctk.CTkLabel(
            main_frame,
            text="Email sent!",
            font=ctk.CTkFont(family="Arial", size=52, weight="bold"),
            text_color="black",
        )
        email_sent_label.pack(pady=(80, 120))

        # Back to Login button
        back_btn = ctk.CTkButton(
            main_frame,
            text="Back to Login",
            font=ctk.CTkFont(family="Arial", size=32, weight="bold"),
            fg_color="#FF0000",
            hover_color="#DD0000",
            text_color="white",
            height=90,
            corner_radius=20,
            border_width=0,
            command=self.go_back,
        )
        back_btn.pack(padx=120, pady=(0, 80), fill="x")

    def go_back(self):
        """Handle back to login"""
        if self.back_callback:
            self.back_callback()
        else:
            print("Back to login clicked")


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("900x700")
    root.title("Password Recovery Success")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    def back_to_login():
        print("Going back to login...")

    app = EmailSent(container, back_to_login)
    root.mainloop()
