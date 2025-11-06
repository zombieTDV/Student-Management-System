import customtkinter as ctk


class ForgotPasswordApp:
    def __init__(self, parent, back_callback=None, email_sent_callback=None):
        self.parent = parent
        self.back_callback = back_callback
        self.email_sent_callback = email_sent_callback

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
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Group 1 title
        group_title = ctk.CTkLabel(
            main_frame,
            text="GROUP 1",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        group_title.pack(pady=(50, 20))

        # Password Recovery title
        recovery_title = ctk.CTkLabel(
            main_frame,
            text="Password Recovery",
            font=ctk.CTkFont(family="Arial", size=42, weight="bold"),
            text_color="#EF4444",
        )
        recovery_title.pack(pady=(0, 80))

        # Email input
        self.email_entry = ctk.CTkEntry(
            main_frame,
            font=ctk.CTkFont(family="Arial", size=18),
            placeholder_text="Your Account Emails",
            placeholder_text_color="#9CA3AF",
            height=70,
            corner_radius=20,
            border_width=3,
            border_color="black",
            fg_color="white",
        )
        self.email_entry.pack(padx=80, pady=30, fill="x")

        # Continue button
        continue_btn = ctk.CTkButton(
            main_frame,
            text="Continute",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            fg_color="#00D600",
            hover_color="#00B000",
            text_color="white",
            height=70,
            corner_radius=20,
            border_width=3,
            border_color="black",
            command=self.recover_password,
        )
        continue_btn.pack(padx=80, pady=40, fill="x")

        if back_callback:
            back_btn = ctk.CTkButton(
                main_frame,
                text="Back to Login",
                font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
                fg_color="#FF0000",
                hover_color="#DD1919",
                text_color="white",
                height=70,
                corner_radius=20,
                border_width=3,
                border_color="black",
                command=self.back_callback,
            )
            back_btn.pack(pady=10)

    def recover_password(self):
        email = self.email_entry.get()
        print(f"Password recovery requested for: {email}")
        self.email_sent_callback()
        # Add your password recovery logic here
