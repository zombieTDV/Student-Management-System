import customtkinter as ctk
from tkinter import ttk


class FinancialSummaryApp:
    def __init__(self, parent, back_callback=None, financial_data=None):
        self.parent = parent
        self.back_callback = back_callback
        self.financial_data = financial_data or []

        # Define column widths and weights for layout
        # These weights will be used by the Treeview AND the Total row
        self.column_config = {
            "Index": {"width": 100, "minwidth": 80, "weight": 1, "anchor": "center"},
            "Name": {
                "width": 400,
                "minwidth": 200,
                "weight": 3,
                "anchor": "w",
            },  # Name is better left-aligned
            "Fee": {"width": 200, "minwidth": 150, "weight": 2, "anchor": "center"},
            "Remain": {"width": 200, "minwidth": 150, "weight": 2, "anchor": "center"},
        }
        # --- IF YOU WANT TO CENTER THE "Name" COLUMN ---
        # Uncomment the line below:
        # self.column_config["Name"]["anchor"] = "center"
        # ---

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
            text="Financial Summary",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        title_label.pack(side="left")

        # Table container
        table_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="#B0B0B0",
        )
        table_container.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        # --- Treeview Implementation (from your example) ---

        # Create Treeview Style
        style = ttk.Style()
        style.theme_use("default")

        # Configure Treeview colors and fonts
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=35,  # Increased row height
            fieldbackground="white",
            font=("Arial", 14),  # Increased font size
        )
        style.configure(
            "Treeview.Heading",
            background="#ADD8E6",  # Match original header color
            foreground="black",
            font=("Arial", 16, "bold"),  # Increased font size
            padding=(0, 5),
        )
        style.map("Treeview", background=[("selected", "#22C55E")])  # Green selection
        style.layout(
            "Treeview", [("Treeview.treearea", {"sticky": "nswe"})]
        )  # Fix for theme bug

        # Create frame for treeview and scrollbar
        tree_frame = ctk.CTkFrame(table_container, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Scrollbar
        # scrollbar = ttk.Scrollbar(tree_frame) # Replaced this line
        # --- NEW CTK SCROLLBAR ---
        scrollbar = ctk.CTkScrollbar(
            tree_frame, button_color="#22C55E", button_hover_color="#16A34A"
        )
        # --- END NEW SCROLLBAR ---
        scrollbar.pack(side="right", fill="y")

        # Define columns
        columns = tuple(self.column_config.keys())

        # Create Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=10,  # Will be overridden by pack(expand=True)
        )

        # Configure scrollbar
        # scrollbar.config(command=self.tree.yview) # Changed to .configure
        scrollbar.configure(command=self.tree.yview)

        # Define headings and column properties
        for col_name, config in self.column_config.items():
            self.tree.heading(col_name, text=col_name)
            self.tree.column(
                col_name,
                width=config["width"],
                minwidth=config["minwidth"],
                anchor=config["anchor"],  # This is the key to alignment!
            )

        self.tree.pack(fill="both", expand=True)

        # Load sample data
        self.load_financial_data()

        # --- End of Treeview ---

        # Calculate totals
        total_fee = sum(
            [self.parse_number(item["fee"]) for item in self.financial_data]
        )
        total_remain = sum(
            [self.parse_number(item["remain"]) for item in self.financial_data]
        )

        # Total separator line
        total_line = ctk.CTkFrame(table_container, fg_color="#B0B0B0", height=3)
        total_line.pack(fill="x", padx=0, pady=0)

        # --- Total Row (Using Grid for Alignment) ---
        total_row = ctk.CTkFrame(
            table_container, fg_color="#FFE6E6", corner_radius=0, height=70
        )
        total_row.pack(fill="x", padx=0, pady=0)
        total_row.pack_propagate(False)

        # Configure total_row grid with the SAME weights as the columns
        total_row.grid_columnconfigure(0, weight=self.column_config["Index"]["weight"])
        total_row.grid_columnconfigure(1, weight=self.column_config["Name"]["weight"])
        total_row.grid_columnconfigure(2, weight=self.column_config["Fee"]["weight"])
        total_row.grid_columnconfigure(3, weight=self.column_config["Remain"]["weight"])
        total_row.grid_rowconfigure(0, weight=1)

        # Total label (spans first two columns)
        total_label_frame = ctk.CTkFrame(total_row, fg_color="transparent")
        # Place in grid, sticky="w" to align left
        total_label_frame.grid(row=0, column=0, columnspan=2, sticky="w", padx=20)

        total_label = ctk.CTkLabel(
            total_label_frame,
            text="Total",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color="#EF4444",
        )
        total_label.pack(side="left", pady=20)

        # Total fee (in column 2)
        total_fee_frame = ctk.CTkFrame(total_row, fg_color="transparent")
        total_fee_frame.grid(row=0, column=2, sticky="nsew", padx=5)  # Fills the cell

        total_fee_label = ctk.CTkLabel(
            total_fee_frame,
            text=self.format_number(total_fee),
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#EF4444",
        )
        total_fee_label.pack(expand=True)  # pack(expand=True) centers it in the frame

        # Total remain (in column 3)
        total_remain_frame = ctk.CTkFrame(total_row, fg_color="transparent")
        total_remain_frame.grid(
            row=0, column=3, sticky="nsew", padx=5
        )  # Fills the cell

        total_remain_label = ctk.CTkLabel(
            total_remain_frame,
            text=self.format_number(total_remain),
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#EF4444",
        )
        total_remain_label.pack(expand=True)  # pack(expand=True) centers it

    def load_financial_data(self):
        """Load financial data into the treeview"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sample data if none provided
        if not self.financial_data:
            self.financial_data = [
                {
                    "index": "1",
                    "name": "Software Engineer",
                    "fee": "3.000.000",
                    "remain": "3.000.000",
                },
                {"index": "2", "name": "Fitness", "fee": "2.000.000", "remain": "0"},
            ]

        # Add data rows
        for row_data in self.financial_data:
            values = (
                row_data["index"],
                row_data["name"],
                row_data["fee"],
                row_data["remain"],
            )
            self.tree.insert("", "end", values=values)

    def parse_number(self, num_str):
        """Parse number string like '3.000.000' to integer"""
        try:
            # Added str() cast for safety
            return int(str(num_str).replace(".", ""))
        except (ValueError, TypeError) as e:  # <-- Now catches specific errors
            # Re-raise as a general Exception with more info
            raise Exception(f"Error parsing number '{num_str}': {e}")

    def format_number(self, num):
        """Format number to string like '3.000.000'"""
        return f"{num: , }".replace(",", ".")


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Financial Summary")

    # Sample data
    financial_data = [
        {
            "index": "1",
            "name": "Software Engineer",
            "fee": "3.000.000",
            "remain": "3.000.000",
        },
        {"index": "2", "name": "Fitness", "fee": "2.000.000", "remain": "0"},
        {"index": "3", "name": "Groceries", "fee": "1.500.000", "remain": "500.000"},
        {"index": "4", "name": "Utilities", "fee": "800.000", "remain": "800.000"},
        {
            "index": "5",
            "name": "Transportation",
            "fee": "1.200.000",
            "remain": "1.200.000",
        },
        {"index": "6", "name": "Dining Out", "fee": "1.000.000", "remain": "100.000"},
        {"index": "7", "name": "Shopping", "fee": "2.500.000", "remain": "1.200.000"},
        {"index": "8", "name": "Rent", "fee": "5.000.000", "remain": "5.000.000"},
        {"index": "9", "name": "Subscriptions", "fee": "300.000", "remain": "300.000"},
        {"index": "10", "name": "Travel", "fee": "4.000.000", "remain": "0"},
    ]

    def go_back():
        print("Back button clicked")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    app = FinancialSummaryApp(container, go_back, financial_data)
    root.mainloop()
