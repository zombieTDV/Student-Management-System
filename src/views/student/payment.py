import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from bson.objectid import ObjectId

# Models
from models.transaction import Transaction


# NOTE: this view expects:
# - student_controller.get_student_by_id(student_id) -> {"success": True, "student": {...}}
# - fee_controller.get_fees_by_student(student_id) -> {"success": True, "fees": [Fee, ...]}
# - Fee objects support ._id, .description, .amount, .student_id, .dueDate, .period, .status, .markPaid(), .save()
class PaymentApp:
    def __init__(
        self, parent, student_id, student_controller, fee_controller, back_callback=None
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.student_controller = student_controller
        self.fee_controller = fee_controller

        # normalize student_id
        self.student_id = (
            ObjectId(student_id)
            if student_id and not isinstance(student_id, ObjectId)
            else student_id
        )

        # hold fee items: fee_id_str -> {"fee": FeeObj, "var": BooleanVar, "frame": Frame}
        self.fee_items = {}
        self.total_fee = 0

        # Theme / container (consistent with other views)
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
        header_frame.pack(fill="x", padx=60, pady=(40, 20))

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

        title_label = ctk.CTkLabel(
            header_frame,
            text="Payment",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        title_label.pack(side="left")

        # Student info (attempt to get from controller)
        student_display = self._fetch_student_info_for_display()

        details_frame = ctk.CTkFrame(main_frame, fg_color="#F9FAFB", corner_radius=10)
        details_frame.pack(fill="x", padx=60, pady=(20, 10))
        details_label = ctk.CTkLabel(
            details_frame,
            text=student_display,
            font=ctk.CTkFont(family="Arial", size=16),
            text_color="black",
            justify="left",
        )
        details_label.pack(anchor="w", padx=20, pady=12)

        # Fee list container
        fee_list_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="#B0B0B0",
        )
        fee_list_container.pack(fill="both", expand=True, padx=60, pady=(10, 20))

        list_title = ctk.CTkLabel(
            fee_list_container,
            text="Unpaid Fees (select to pay)",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="black",
        )
        list_title.pack(anchor="w", padx=20, pady=(12, 6))

        # Scrollable frame for fee items
        self.scroll_frame = ctk.CTkScrollableFrame(
            fee_list_container,
            fg_color="white",
            corner_radius=0,
            scrollbar_button_color="#22C55E",
            scrollbar_button_hover_color="#16A34A",
            height=250,
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(6, 12))

        # Footer with total and buttons
        footer_frame = ctk.CTkFrame(main_frame, fg_color="white")
        footer_frame.pack(fill="x", padx=60, pady=(0, 40))

        # "Select all" checkbox
        self.select_all_var = tk.BooleanVar(value=True)
        select_all_cb = ctk.CTkCheckBox(
            footer_frame,
            text="Select all",
            variable=self.select_all_var,
            command=self._on_select_all_toggle,
        )
        select_all_cb.pack(side="left", padx=(0, 20))

        self.total_label = ctk.CTkLabel(
            footer_frame,
            text="Total: 0",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#EF4444",
        )
        self.total_label.pack(side="left", padx=(10, 20))

        # Pay button
        pay_button = ctk.CTkButton(
            footer_frame,
            text="Pay",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="white",
            width=200,
            height=60,
            corner_radius=10,
            command=self.pay_action,
        )
        pay_button.pack(side="right")

        # Load unpaid fees
        self.load_unpaid_fees()

    def _fetch_student_info_for_display(self):
        try:
            res = self.student_controller.get_student_by_id(str(self.student_id))
            if res.get("success"):
                s = res["student"]
                return (
                    f"Student ID: {s.get('id', '')}\n"
                    f"Full name:  {s.get('fullName', '')}\n"
                    f"Date of birth: {s.get('dob', '')}"
                )
        except Exception:
            pass
        return f"Student ID: {str(self.student_id)}\nFull name: -\nDate of birth: -\n"

    def load_unpaid_fees(self):
        """Fetch unpaid fees for this student and populate the scroll frame"""
        # clear existing
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self.fee_items.clear()

        if not self.fee_controller or not self.student_id:
            return

        res = self.fee_controller.get_fees_by_student(self.student_id)
        if not res.get("success"):
            # show a simple error popup
            self._show_error(f"Failed to load fees: {res.get('message', 'Unknown')}")
            return

        fees = res.get("fees", [])
        # filter unpaid (status not 'paid')
        unpaid_fees = [f for f in fees if getattr(f, "status", "").lower() != "paid"]

        if not unpaid_fees:
            empty_label = ctk.CTkLabel(
                self.scroll_frame,
                text="No unpaid fees found.",
                font=ctk.CTkFont(size=16),
            )
            empty_label.pack(padx=10, pady=20)
            self.total_label.configure(text="Total: 0")
            return

        # create items
        for fee in unpaid_fees:
            self._add_fee_item(fee)

        # after adding all, update total
        self.update_total()

    def _add_fee_item(self, fee):
        """Add one fee row (checkbox + info)"""
        fee_id = str(fee._id)
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=6)

        var = tk.BooleanVar(value=True)
        label_text = f"{fee.description} — {self._format_number(getattr(fee, 'amount', 0))}  (Due: {getattr(fee, 'dueDate', '')})"
        cb = ctk.CTkCheckBox(
            frame, text=label_text, variable=var, command=self.update_total
        )
        cb.pack(fill="x", padx=8, pady=6)

        # store
        self.fee_items[fee_id] = {"fee": fee, "var": var, "frame": frame}

    def _on_select_all_toggle(self):
        v = self.select_all_var.get()
        for item in self.fee_items.values():
            item["var"].set(v)
        self.update_total()

    def update_total(self):
        total = 0
        for item in self.fee_items.values():
            if item["var"].get():
                amt = getattr(item["fee"], "amount", 0)
                try:
                    total += int(round(float(amt)))
                except Exception:
                    total += 0
        self.total_fee = total
        self.total_label.configure(text=f"Total: {self._format_number(self.total_fee)}")

    def pay_action(self):
        """Mark selected fees as paid and create transactions (pseudo payment)."""
        selected = [it for it in self.fee_items.values() if it["var"].get()]
        if not selected:
            self._show_error("No fee selected to pay.")
            return

        total_paid = 0
        paid_descriptions = []

        # process each selected fee
        for item in selected:
            fee = item["fee"]
            try:
                amount = int(round(float(getattr(fee, "amount", 0))))
            except Exception:
                amount = 0

            # mark fee paid (Fee.markPaid does .save())
            try:
                fee.markPaid()
            except Exception:
                # fallback: attempt to set status and save
                try:
                    fee.status = "paid"
                    fee.save()
                except Exception as e:
                    print("Warning: could not mark fee paid:", e)

            # create transaction record
            try:
                tx = Transaction(
                    amount=amount,
                    method="manual",  # pseudo
                    student_id=fee.student_id,
                    fee_id=fee._id,
                    status="completed",
                    date=datetime.utcnow(),
                )
                tx.save()
            except Exception as e:
                print("Warning: transaction save failed:", e)

            total_paid += amount
            paid_descriptions.append(fee.description)

        # reload unpaid fees list
        self.load_unpaid_fees()

        # show success dialog
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Payment Success")
        dialog.geometry("420x220")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="✓ Payment Completed",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#22C55E",
        ).pack(pady=(20, 8))
        ctk.CTkLabel(
            dialog,
            text=f"Total paid: {self._format_number(total_paid)}",
            font=ctk.CTkFont(size=16),
        ).pack(pady=(0, 8))
        ctk.CTkLabel(
            dialog, text="Items paid:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(6, 0))
        ctk.CTkLabel(
            dialog, text=", ".join(paid_descriptions), wraplength=380, justify="left"
        ).pack(pady=(4, 10))

        ctk.CTkButton(dialog, text="OK", width=120, command=dialog.destroy).pack(pady=6)

    def _show_error(self, message):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Error")
        dialog.geometry("360x140")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, text=f"✗ {message}", font=ctk.CTkFont(size=14), text_color="#FF0000"
        ).pack(pady=20)
        ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy).pack(pady=6)

    def _format_number(self, n):
        try:
            n = int(round(n))
        except Exception:
            n = 0
        return f"{n:,}".replace(",", ".")
