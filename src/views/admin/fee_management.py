import customtkinter as ctk
from tkinter import ttk
from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController
from controllers.fee_controller import FeeController
from datetime import datetime


class FeeManagement:
    def __init__(
        self,
        parent,
        back_callback,
        student_controller: StudentController,
        auth_controller: AuthController,
        fee_controller: FeeController,
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.student_controller = student_controller
        self.auth_controller = auth_controller
        self.fee_controller = fee_controller

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

        # Table
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
            "StudentUsername",
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

        ctk.CTkButton(
            buttons_frame,
            text="Add Fee",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=200,
            height=60,
            corner_radius=15,
            command=self.add_fee_dialog,
        ).pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            buttons_frame,
            text="Mark Paid",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#FF7B7B",
            hover_color="#FF6B6B",
            text_color="white",
            width=200,
            height=60,
            corner_radius=15,
            command=self.mark_fee_paid,
        ).pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            buttons_frame,
            text="Delete Fee",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#FF3B3B",
            hover_color="#FF0000",
            text_color="white",
            width=200,
            height=60,
            corner_radius=15,
            command=self.delete_fee,
        ).pack(side="left", padx=(0, 20))

        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            fg_color="#22C55E",
            hover_color="#1e9c4e",
            text_color="white",
            width=200,
            height=60,
            corner_radius=12,
            command=self.load_fees(),
        )
        refresh_btn.pack(side="left", padx=(0, 20))

        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_fees()

    def _validate_fee_date(self, date_str):
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except Exception:
            return False

    # Load fees
    def load_fees(self):
        self.tree.delete(*self.tree.get_children())
        result = self.fee_controller.get_all_fees()
        if result["success"]:
            for fee in result["fees"]:
                student_username = self.student_controller.get_student_by_id(
                    fee.student_id
                )["student"]["username"]
                due_date_str = (
                    fee.dueDate.strftime("%d/%m/%Y")
                    if hasattr(fee.dueDate, "strftime")
                    else fee.dueDate
                )
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        str(fee._id),
                        fee.description,
                        fee.amount,
                        student_username,
                        due_date_str,
                        fee.period,
                        fee.status,
                    ),
                )

    # Double-click edit
    def on_double_click(self, event):
        item = self.tree.selection()
        if item:
            self.open_edit_fee_dialog(item[0], self.tree.item(item[0])["values"])

    def add_fee_dialog(self):
        """Popup to add a new fee"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Fee")
        dialog.geometry("500x450")
        dialog.grab_set()

        fields = ["Description", "Amount", "StudentUsername", "DueDate"]
        entries = {}

        # Create entry fields
        for field in fields:
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=5)

            ctk.CTkLabel(frame, text=field + ":", width=120, anchor="w").pack(
                side="left"
            )

            if field == "StudentUsername":
                usernames = self.student_controller.get_all_usernames()[
                    "students_usernames"
                ]
                if not usernames:
                    usernames = ["No Students Found"]
                var = ctk.StringVar(value=usernames[0])
                menu = ctk.CTkOptionMenu(frame, variable=var, values=usernames)
                menu.pack(side="left", padx=10, fill="x", expand=True)
                entries[field] = var
            else:
                entry = ctk.CTkEntry(frame, width=300)
                entry.pack(side="left", padx=10, fill="x", expand=True)
                entries[field] = entry

        # Period dropdown (Month + Year)
        period_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        period_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(period_frame, text="Period:", width=120, anchor="w").pack(
            side="left"
        )

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        month_var = ctk.StringVar(value=months[0])
        month_menu = ctk.CTkOptionMenu(period_frame, variable=month_var, values=months)
        month_menu.pack(side="left", padx=(0, 10))

        years = [str(y) for y in range(2023, 2031)]
        year_var = ctk.StringVar(value=years[0])
        year_menu = ctk.CTkOptionMenu(period_frame, variable=year_var, values=years)
        year_menu.pack(side="left", padx=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Add Fee",
            width=120,
            command=lambda: self.add_fee(dialog, entries, month_var, year_var),
        ).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, command=dialog.destroy).pack(
            side="left", padx=10
        )

    def add_fee(self, dialog, entries, month_var, year_var):
        try:
            period = f"{month_var.get()} {year_var.get()}"
            student_id = self.student_controller.get_student_id_by_username(
                entries["StudentUsername"].get()
            )
            fee = self.fee_controller.create_fee(
                description=entries["Description"].get().strip(),
                amount=float(entries["Amount"].get().strip()),
                student_id=student_id,
                dueDate=datetime.strptime(entries["DueDate"].get().strip(), "%d/%m/%Y"),
                period=period,
            )
            fee.save()
            self.load_fees()
            dialog.destroy()
            self.show_success_dialog("Fee added successfully!")
        except Exception as e:
            self.show_error_dialog(str(e))

    # Edit Fee dialog
    def open_edit_fee_dialog(self, tree_item, fee_values):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Fee")
        dialog.geometry("500x450")
        dialog.grab_set()

        # fields presented (StudentUsername is a dropdown)
        fields = ["Description", "Amount", "StudentUsername", "DueDate"]
        entries = {}

        # fee_values layout: [FeeID, Description, Amount, StudentID, DueDate, Period, Status]
        # fee_values[3] is expected to be the StudentID (string)
        current_student_id_str = str(fee_values[3])

        # Try to find the current student's username (fallback to raw id)
        current_username = None
        try:
            res = self.student_controller.get_student_by_id(current_student_id_str)
            if res.get("success") and res.get("student"):
                current_username = res["student"].get("username")
        except Exception:
            current_username = None

        # get usernames list (ensure it's a list of strings)
        usernames_res = self.student_controller.get_all_usernames()
        usernames = []
        if isinstance(usernames_res, dict) and "students_usernames" in usernames_res:
            usernames = usernames_res["students_usernames"] or []
        elif isinstance(usernames_res, list):
            usernames = usernames_res
        # ensure at least one placeholder exists
        if not usernames:
            usernames = ["No Students Found"]

        for i, field in enumerate(fields):
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=5)
            ctk.CTkLabel(frame, text=field + ":", width=100, anchor="w").pack(
                side="left"
            )

            if field == "StudentUsername":
                # If current_username present and in list, use it; otherwise default to first
                default_value = (
                    current_username if current_username in usernames else usernames[0]
                )
                var = ctk.StringVar(value=default_value)
                menu = ctk.CTkOptionMenu(frame, variable=var, values=usernames)
                menu.pack(side="left", padx=10, fill="x", expand=True)
                entries[field] = var
            else:
                entry = ctk.CTkEntry(frame, width=300)
                # Description -> fee_values[1], Amount -> fee_values[2], DueDate -> fee_values[4]
                if field == "Description":
                    entry.insert(0, str(fee_values[1]))
                elif field == "Amount":
                    entry.insert(0, str(fee_values[2]))
                elif field == "DueDate":
                    entry.insert(0, str(fee_values[4]))
                entry.pack(side="left", padx=10, fill="x", expand=True)
                entries[field] = entry

        # Period dropdown
        period_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        period_frame.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(period_frame, text="Period:", width=100, anchor="w").pack(
            side="left"
        )

        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        # safe split of period (fee_values[5]) — if malformed, fallback to first month/year
        period_raw = fee_values[5] if len(fee_values) > 5 else ""
        try:
            month_str, year_str = period_raw.split()
            if month_str not in months:
                month_str = months[0]
        except Exception:
            month_str = months[0]
            year_str = "2023"

        month_var = ctk.StringVar(value=month_str)
        ctk.CTkOptionMenu(period_frame, variable=month_var, values=months).pack(
            side="left", padx=(0, 10)
        )

        years = [str(y) for y in range(2023, 2031)]
        if year_str not in years:
            year_str = years[0]
        year_var = ctk.StringVar(value=year_str)
        ctk.CTkOptionMenu(period_frame, variable=year_var, values=years).pack(
            side="left", padx=(0, 10)
        )

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(
            btn_frame,
            text="Save",
            width=120,
            command=lambda: self.save_fee_edit(
                dialog, tree_item, entries, fee_values[0], month_var, year_var
            ),
        ).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, command=dialog.destroy).pack(
            side="left", padx=10
        )

    def save_fee_edit(self, dialog, tree_item, entries, fee_id, month_var, year_var):
        # find fee object from controller
        fee = self.fee_controller.find_by_id(fee_id)
        if not fee:
            self.show_error_dialog("Fee not found!")
            return
        try:
            fee.description = entries["Description"].get().strip()
            fee.amount = float(entries["Amount"].get().strip())

            # get username from the StringVar (OptionMenu)
            selected_username = entries["StudentUsername"].get()
            # Convert to student id using controller
            try:
                student_obj_id = self.student_controller.get_student_id_by_username(
                    selected_username
                )
            except Exception as e:
                raise ValueError(f"Cannot resolve student username -> id: {e}")

            fee.student_id = student_obj_id
            # parse due date in DD/MM/YYYY (you use that format across app)
            fee.dueDate = datetime.strptime(
                entries["DueDate"].get().strip(), "%d/%m/%Y"
            )
            fee.period = f"{month_var.get()} {year_var.get()}"

            fee.save()
            self.load_fees()
            dialog.destroy()
            self.show_success_dialog("Fee updated successfully!")
        except Exception as e:
            # provide a helpful message instead of raw tkinter error
            self.show_error_dialog(f"Failed to update fee: {e}")

    # Delete
    def delete_fee(self):
        item = self.tree.selection()
        if not item:
            self.show_error_dialog("Select a fee to delete!")
            return
        fee_id = self.tree.item(item[0])["values"][0]
        fee = self.fee_controller.find_by_id(fee_id)
        if fee:
            fee.delete()
            self.load_fees()
            self.show_success_dialog("Fee deleted successfully!")

    # Mark Paid
    def mark_fee_paid(self):
        item = self.tree.selection()
        if not item:
            self.show_error_dialog("Select a fee to mark as paid!")
            return
        fee_id = self.tree.item(item[0])["values"][0]
        fee = self.fee_controller.find_by_id(fee_id)
        if fee:
            fee.markPaid()
            self.load_fees()
            self.show_success_dialog("Fee marked as paid!")

    # Dialog helpers
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
        dialog.geometry("500x300")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, text=f"✗ {message}", font=ctk.CTkFont(size=16), text_color="#FF0000"
        ).pack(pady=30)
        ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy).pack(
            pady=10
        )
