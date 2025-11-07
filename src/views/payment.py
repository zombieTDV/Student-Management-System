import customtkinter as ctk
import tkinter as tk  # Import tkinter for BooleanVar


class PaymentApp:
    def __init__(self, parent, back_callback=None, student_data=None, fee_data=None):
        self.parent = parent
        self.back_callback = back_callback
        self.student_data = student_data or {}
        # This is the original list of all available fees
        self.fee_data = fee_data or []

        # This dict will hold all fee item widgets and their tick status
        self.fee_items = {}
        self.total_fee = 0

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

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=0)
        header_frame.pack(fill="x", padx=40, pady=(40, 20))

        # Back button on the left (using same style as FinancialSummaryApp)
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

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Payment",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        title_label.pack(side="left", padx=20)

        # You can add the icon here if you have it as an image file
        # For example, using a simple label as placeholder:
        icon_label = ctk.CTkLabel(
            header_frame,
            text="💳",  # Placeholder emoji for card icon
            font=ctk.CTkFont(size=40),
            text_color="#22C55E",
        )
        icon_label.pack(side="left", padx=10)

        # --- Student Details ---
        details_frame = ctk.CTkFrame(main_frame, fg_color="#F3F4F6", corner_radius=10)
        details_frame.pack(fill="x", padx=40, pady=10)

        student_info = f"""
Student ID:     {self.student_data.get('id', '...')}
Full name:      {self.student_data.get('name', '...')}
Date of birth:  {self.student_data.get('dob', '...')}
Major:          {self.student_data.get('major', '...')}
        """

        details_label = ctk.CTkLabel(
            details_frame,
            text=student_info,
            font=ctk.CTkFont(family="Arial", size=18),
            text_color="black",
            justify="left",
            anchor="w",
        )
        details_label.pack(anchor="w", padx=20, pady=15)

        # --- Fee List Container ---
        fee_list_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="#B0B0B0",
        )
        fee_list_container.pack(fill="both", expand=True, padx=40, pady=20)

        # Title for fee list
        list_title_label = ctk.CTkLabel(
            fee_list_container,
            text="Lists of fees (select to pay)",  # Updated title
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="black",
        )
        list_title_label.pack(anchor="w", padx=20, pady=(10, 5))

        # Scrollable frame for fee items
        self.scroll_frame = ctk.CTkScrollableFrame(
            fee_list_container,
            fg_color="white",
            corner_radius=0,
            scrollbar_button_color="#22C55E",
            scrollbar_button_hover_color="#16A34A",
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        # Add fee items
        for item in self.fee_data:
            self.add_fee_item(item)

        # --- Total and Pay Button ---
        footer_frame = ctk.CTkFrame(main_frame, fg_color="white")
        footer_frame.pack(fill="x", padx=40, pady=(0, 40))

        self.total_label = ctk.CTkLabel(
            footer_frame,
            text="Total: 0",  # Initial text
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color="#EF4444",
        )
        self.total_label.pack(side="left", padx=20, pady=10)

        pay_button = ctk.CTkButton(
            footer_frame,
            text="Pay",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="white",
            width=150,
            height=50,
            corner_radius=10,
            command=self.pay_action,
        )
        pay_button.pack(side="right", padx=20, pady=10)

        # Initial calculation
        self.update_total()

    def add_fee_item(self, item_data):
        """Adds a new fee item row to the scrollable frame with a checkbox"""
        item_id = item_data.get("id", f"item_{len(self.fee_items)}")
        name = item_data.get("name", "Unknown Fee")
        fee_str = item_data.get("fee", "0")

        item_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=5)

        # Variable to hold the checkbox state (default to True/ticked)
        checkbox_var = tk.BooleanVar(value=True)

        item_label_text = f"{name}: {self.format_number(self.parse_number(fee_str))}"

        # Create Checkbox instead of Label and Button
        checkbox = ctk.CTkCheckBox(
            item_frame,
            text=item_label_text,
            variable=checkbox_var,
            font=ctk.CTkFont(family="Arial", size=16),
            text_color="black",
            command=self.update_total,  # Update total whenever ticked/unticked
        )
        checkbox.pack(side="left", fill="x", expand=True, padx=10)

        # Store the frame, data, and checkbox variable
        self.fee_items[item_id] = {
            "frame": item_frame,
            "data": item_data,
            "var": checkbox_var,
        }

    # This function is no longer needed
    # def remove_fee_item(self, item_id):
    #     ...

    def update_total(self):
        """Recalculates and updates the total fee label based on ticked items"""
        total = 0
        # Iterate over all stored fee items
        for item_id, item in self.fee_items.items():
            # Check if the item's checkbox variable is ticked (True)
            if item["var"].get():
                # If ticked, add its fee to the total
                total += self.parse_number(item["data"].get("fee", "0"))

        self.total_fee = total
        self.total_label.configure(text=f"Total: {self.format_number(self.total_fee)}")

    def pay_action(self):
        """Action to perform when 'Pay' is clicked"""
        print(f"Attempting to pay: {self.format_number(self.total_fee)}")

        # Log which items are being paid for
        paid_items = []
        for item_id, item in self.fee_items.items():
            if item["var"].get():
                paid_items.append(item["data"].get("name", "Unknown"))

        print(f"Paying for: {', '.join(paid_items)}")

        # Show success message
        success_dialog = ctk.CTkToplevel(self.parent)
        success_dialog.title("Payment Success")
        success_dialog.geometry("400x200")
        success_dialog.grab_set()  # Make modal

        ctk.CTkLabel(
            success_dialog,
            text="✓ Payment Successful!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#22C55E",
        ).pack(pady=30)

        ctk.CTkLabel(
            success_dialog,
            text=f"Amount Paid: {self.format_number(self.total_fee)}",
            font=ctk.CTkFont(size=16),
        ).pack(pady=10)

        ctk.CTkButton(
            success_dialog,
            text="OK",
            width=120,
            height=40,
            command=success_dialog.destroy,
        ).pack(pady=20)

    def parse_number(self, num_str):
        """Parse number string like '3.000.000' to integer"""
        try:
            # Added str() cast for safety
            return int(str(num_str).replace(".", ""))
        except (ValueError, TypeError):  # <-- This is the specific change
            # Catch specific errors and return 0 as requested
            return 0

    def format_number(self, num):
        return f"{num:,}".replace(",", ".")


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Payment Screen")

    # Sample data
    sample_student = {
        "id": "2021001",
        "name": "John Doe",
        "dob": "01/15/2000",
        "major": "Computer Science",
    }

    sample_fees = [
        {"id": "fee1", "name": "Software Engineer", "fee": "3.000.000"},
        {"id": "fee2", "name": "Fitness", "fee": "2.000.000"},
        {"id": "fee3", "name": "Library Fine", "fee": "50.000"},
    ]

    def go_back():
        print("Back button clicked")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    # Use the class name from your provided code
    app = PaymentApp(container, go_back, sample_student, sample_fees)
    root.mainloop()
