import customtkinter as ctk
from tkinter import ttk
from bson.objectid import ObjectId
from models.fee import Fee  # Your Fee model
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController
from datetime import datetime


class FeeManagement:
    def __init__(
        self,
        parent,
        back_callback,
        student_controller: StudentController,
        auth_controller: AuthController,
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.student_controller = student_controller
        self.auth_controller = auth_controller

        # Theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        main_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=50,
            border_width=3,
            border_color="black",
        )
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="white")
        header_frame.pack(anchor="w", padx=60, pady=(40, 30))

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

        header_label = ctk.CTkLabel(
            header_frame,
            text="Fees",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#22C55E",
        )
        header_label.pack(side="left")

        # Table container
        table_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="black",
        )
        table_container.pack(fill="both", expand=True, padx=60, pady=(0, 30))

        tree_frame = ctk.CTkFrame(table_container, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = (
            "FeeID",
            "Description",
            "Amount",
            "StudentID",
            "DueDate",
            "Period",
            "Status",
        )
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12,
        )
        scrollbar.config(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=100, anchor="w")
        self.tree.pack(fill="both", expand=True)

        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(20, 40))

        add_btn = ctk.CTkButton(
            buttons_frame,
            text="Add Fee",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=220,
            height=80,
            corner_radius=15,
            command=self.add_fee_dialog,
        )
        add_btn.pack(side="left", padx=(0, 20))

        mark_paid_btn = ctk.CTkButton(
            buttons_frame,
            text="Mark Paid",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#FF7B7B",
            hover_color="#FF6B6B",
            text_color="white",
            width=220,
            height=80,
            corner_radius=15,
            command=self.mark_fee_paid,
        )
        mark_paid_btn.pack(side="left", padx=(0, 20))

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Save Changes",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#22C55E",
            hover_color="#1e9c4e",
            text_color="white",
            width=220,
            height=80,
            corner_radius=15,
            command=self.save_changes,
        )
        save_btn.pack(side="left")

        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_fees()

    def load_fees(self):
        """Load all fees from database"""
        self.tree.delete(*self.tree.get_children())
        fees = Fee.FEES_COLLECTION.find()
        for fee_data in fees:
            fee = Fee(**fee_data)
            self.tree.insert(
                "",
                "end",
                values=(
                    str(fee._id),
                    fee.description,
                    fee.amount,
                    str(fee.student_id),
                    fee.dueDate.strftime("%Y-%m-%d")
                    if hasattr(fee.dueDate, "strftime")
                    else fee.dueDate,
                    fee.period,
                    fee.status,
                ),
            )

    def on_double_click(self, event):
        """Edit fee on double-click"""
        item = self.tree.selection()
        if item:
            values = self.tree.item(item[0])["values"]
            self.open_edit_fee_dialog(item[0], values)

    def open_edit_fee_dialog(self, tree_item, fee_values):
        """Popup to edit fee details"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Fee")
        dialog.geometry("500x400")
        dialog.grab_set()

        fields = ["Description", "Amount", "StudentID", "DueDate", "Period", "Status"]
        entries = {}

        for i, (field, value) in enumerate(zip(fields, fee_values[1:])):
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=5)
            ctk.CTkLabel(frame, text=field + ":", width=100, anchor="w").pack(
                side="left"
            )
            entry = ctk.CTkEntry(frame, width=300)
            entry.insert(0, str(value))
            entry.pack(side="left", padx=10)
            entries[field] = entry

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            width=120,
            command=lambda: self.save_fee_edit(
                dialog, tree_item, entries, fee_values[0]
            ),
        ).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, command=dialog.destroy).pack(
            side="left", padx=10
        )

    def save_fee_edit(self, dialog, tree_item, entries, fee_id):
        fee = Fee.find_by_id(fee_id)
        if not fee:
            self.show_error_dialog("Fee not found!")
            return
        try:
            fee.description = entries["Description"].get().strip()
            fee.amount = float(entries["Amount"].get().strip())
            fee.student_id = ObjectId(entries["StudentID"].get().strip())
            fee.dueDate = datetime.strptime(
                entries["DueDate"].get().strip(), "%Y-%m-%d"
            )
            fee.period = entries["Period"].get().strip()
            fee.status = entries["Status"].get().strip()
            fee.save()

            self.load_fees()
            dialog.destroy()
            self.show_success_dialog("Fee updated successfully!")
        except Exception as e:
            self.show_error_dialog(str(e))

    def add_fee_dialog(self):
        """Popup to add a new fee"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Fee")
        dialog.geometry("500x400")
        dialog.grab_set()

        fields = ["Description", "Amount", "StudentID", "DueDate", "Period"]
        entries = {}

        for field in fields:
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=5)
            ctk.CTkLabel(frame, text=field + ":", width=100, anchor="w").pack(
                side="left"
            )
            entry = ctk.CTkEntry(frame, width=300)
            entry.pack(side="left", padx=10)
            entries[field] = entry

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(
            btn_frame,
            text="Add Fee",
            width=120,
            command=lambda: self.add_fee(dialog, entries),
        ).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, command=dialog.destroy).pack(
            side="left", padx=10
        )

    def add_fee(self, dialog, entries):
        try:
            fee = Fee(
                description=entries["Description"].get().strip(),
                amount=float(entries["Amount"].get().strip()),
                student_id=ObjectId(entries["StudentID"].get().strip()),
                dueDate=datetime.strptime(entries["DueDate"].get().strip(), "%Y-%m-%d"),
                period=entries["Period"].get().strip(),
            )
            fee.save()
            self.load_fees()
            dialog.destroy()
            self.show_success_dialog("Fee added successfully!")
        except Exception as e:
            self.show_error_dialog(str(e))

    def mark_fee_paid(self):
        item = self.tree.selection()
        if not item:
            self.show_error_dialog("Select a fee to mark as paid!")
            return
        fee_id = self.tree.item(item[0])["values"][0]
        fee = Fee.find_by_id(fee_id)
        if fee:
            fee.markPaid()
            self.load_fees()
            self.show_success_dialog("Fee marked as paid!")

    def save_changes(self):
        """Reload fees to ensure latest data saved"""
        self.load_fees()
        self.show_success_dialog("All fees synced successfully!")

    def show_success_dialog(self, message):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Success")
        dialog.geometry("300x150")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, text=f"✓ {message}", font=ctk.CTkFont(size=16), text_color="#22C55E"
        ).pack(pady=30)
        ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy).pack(
            pady=10
        )

    def show_error_dialog(self, message):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Error")
        dialog.geometry("350x150")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, text=f"✗ {message}", font=ctk.CTkFont(size=16), text_color="#FF0000"
        ).pack(pady=30)
        ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy).pack(
            pady=10
        )


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Fee Management")
    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    # Pass None or your real controllers
    app = FeeManagement(container, None, None, None)
    root.mainloop()
