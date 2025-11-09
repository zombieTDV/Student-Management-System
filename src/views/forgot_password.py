import customtkinter as ctk
from controllers.auth_controller import AuthController


class ForgotPasswordApp:
    def __init__(self, parent, back_callback, auth_controller: AuthController):
        self.parent = parent
        self.back_callback = back_callback
        self.auth_controller = auth_controller

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
            text="Continue",
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
        """Handle password recovery using auth_controller"""
        email = self.email_entry.get().strip()

        # Validate email input
        if not email:
            self.show_message("Error", "Please enter your email", error=True)
            return

        # Call auth_controller to handle recovery
        result = self.auth_controller.recover_password(email)

        if result["success"]:
            # Success - show message and go back to login
            self.show_message(
                "Success",
                result["message"],
                callback=self.back_callback,  # Go back after OK
            )
        else:
            # Error - show error message
            self.show_message("Error", result["message"], error=True)

    def show_message(self, title, message, error=False, callback=None):
        """Show message dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.grab_set()

        # Icon and color
        icon = "✗" if error else "✓"
        color = "#FF0000" if error else "#22C55E"

        ctk.CTkLabel(
            dialog,
            text=f"{icon} {message}",
            font=ctk.CTkFont(size=16),
            text_color=color,
            wraplength=350,
        ).pack(pady=40)

        ctk.CTkButton(
            dialog,
            text="OK",
            width=120,
            height=40,
            command=lambda: [dialog.destroy(), callback() if callback else None],
        ).pack(pady=10)
