import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

from controllers.transaction_controller import TransactionController


class TransactionManagement:
    """
    Simple transaction management view:
    - Shows a table of transactions
    - Buttons: Refresh, View Detail, Back
    - Double-click or "View Detail" opens a modal with transaction details
    """

    def __init__(self, parent, back_callback, transaction_controller=None):
        self.parent = parent
        self.back_callback = back_callback
        self.transaction_controller: TransactionController = transaction_controller

        # Theme (consistent with other views)
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
        header_frame = ctk.CTkFrame(main_frame, fg_color="white")
        header_frame.pack(fill="x", padx=60, pady=(40, 30))

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

        title_label = ctk.CTkLabel(
            header_frame,
            text="TRANSACTIONS",
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
            border_color="black",
        )
        table_container.pack(fill="both", expand=True, padx=60, pady=(0, 30))

        # Treeview style
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=30,
            fieldbackground="white",
            font=("Arial", 11),
        )
        style.configure(
            "Treeview.Heading",
            background="#F0F0F0",
            foreground="black",
            font=("Arial", 12, "bold"),
        )
        style.map("Treeview", background=[("selected", "#0078D7")])

        # Tree frame + scrollbar
        tree_frame = ctk.CTkFrame(table_container, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Define columns
        columns = (
            "TransactionID",
            "Amount",
            "Method",
            "StudentID",
            "FeeID",
            "Status",
            "Date",
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
            # give ID columns wider space
            if col in ("TransactionID", "StudentID", "FeeID"):
                self.tree.column(col, width=200, minwidth=120, anchor="w")
            elif col == "Amount":
                self.tree.column(col, width=120, minwidth=100, anchor="e")
            else:
                self.tree.column(col, width=140, minwidth=100, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(10, 40))

        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="Refresh",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            fg_color="#22C55E",
            hover_color="#1e9c4e",
            text_color="white",
            width=160,
            height=60,
            corner_radius=12,
            command=self.load_transactions,
        )
        refresh_btn.pack(side="left", padx=(0, 20))

        view_btn = ctk.CTkButton(
            buttons_frame,
            text="View Detail",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=160,
            height=60,
            corner_radius=12,
            command=self.view_selected_detail,
        )
        view_btn.pack(side="left", padx=(0, 20))

        # Bind double click to view details
        self.tree.bind("<Double-1>", self.on_double_click)

        # Load initial data
        self.load_transactions()

    # -------------------------
    # Data loading / helpers
    # -------------------------
    def _format_dt(self, v):
        if not v:
            return "N/A"
        # Accept datetime or string
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d %H:%M")
        try:
            # Try parsing common isoformat strings
            dt = datetime.fromisoformat(str(v))
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(v)

    def load_transactions(self):
        """Load transactions from controller or sample data"""
        # clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if self.transaction_controller:
                result = self.transaction_controller.get_all_transactions()
            else:
                result = {"success": False, "message": "No controller provided"}
        except Exception as e:
            print(f"Error calling controller: {e}")
            result = {"success": False, "message": str(e)}

        if result.get("success"):
            txs = result.get("transactions", [])
            for tx in txs:
                # tx may be dict or object-like
                tx_id = str(
                    getattr(tx, "_id", None) or tx.get("_id") or tx.get("id") or ""
                )
                amount = getattr(tx, "amount", None) or tx.get("amount", "")
                method = getattr(tx, "method", None) or tx.get("method", "")
                student_id = getattr(tx, "student_id", None) or tx.get("student_id", "")
                fee_id = getattr(tx, "fee_id", None) or tx.get("fee_id", "")
                status = getattr(tx, "status", None) or tx.get("status", "")
                date = (
                    getattr(tx, "date", None)
                    or tx.get("date", "")
                    or tx.get("createAt", "")
                )

                date_str = self._format_dt(date)

                # Format amount nicely if numeric
                try:
                    amt_int = int(round(float(amount)))
                    amt_str = f"{amt_int:,}".replace(",", ".")
                except Exception:
                    amt_str = str(amount)

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        tx_id,
                        amt_str,
                        method,
                        str(student_id),
                        str(fee_id),
                        status,
                        date_str,
                    ),
                )
        else:
            print("Error: Failed to load transactions")

    # -------------------------
    # Selection / detail
    # -------------------------
    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        self.view_selected_detail()

    def view_selected_detail(self):
        sel = self.tree.selection()
        if not sel:
            self.show_error_dialog("Select a transaction first")
            return

        values = self.tree.item(sel[0])["values"]
        tx_id = values[0]

        # Try controller.find_by_id and handle different return shapes
        tx_obj = None
        try:
            if self.transaction_controller and hasattr(
                self.transaction_controller, "find_by_id"
            ):
                res = self.transaction_controller.find_by_id(tx_id)
                # res may be a dict like {"success": True, "transaction": {...}}
                if isinstance(res, dict):
                    if res.get("success") and res.get("transaction"):
                        tx_obj = res.get("transaction")
                    else:
                        # controller couldn't find it — leave tx_obj None and fallback to row values
                        tx_obj = None
                else:
                    # controller returned a raw object (legacy) — use it
                    tx_obj = res
        except Exception:
            tx_obj = None

        # If controller didn't return an object/dict, build a dict from row values
        if not tx_obj:
            tx_obj = {
                "_id": values[0],
                "amount": values[1],
                "method": values[2],
                "student_id": values[3],
                "fee_id": values[4],
                "status": values[5],
                "date": values[6],
            }

        # Ensure we pass a plain dict into the dialog for consistent access
        # If tx_obj is an object with attributes, convert to dict-like mapping
        if not isinstance(tx_obj, dict):
            # try to build a dict from attributes
            try:
                tx_obj = {
                    "_id": str(
                        getattr(tx_obj, "_id", None) or getattr(tx_obj, "id", None)
                    ),
                    "amount": getattr(tx_obj, "amount", None),
                    "method": getattr(tx_obj, "method", None),
                    "student_id": (
                        str(getattr(tx_obj, "student_id", None))
                        if getattr(tx_obj, "student_id", None) is not None
                        else None
                    ),
                    "fee_id": (
                        str(getattr(tx_obj, "fee_id", None))
                        if getattr(tx_obj, "fee_id", None) is not None
                        else None
                    ),
                    "status": getattr(tx_obj, "status", None),
                    "date": getattr(tx_obj, "date", None)
                    or getattr(tx_obj, "createAt", None),
                }
            except Exception:
                # last-resort: keep as-is and let _open_detail_dialog handle it
                pass

        self._open_detail_dialog(tx_obj)

    def _open_detail_dialog(self, tx):
        """
        tx may be:
          - a dict (preferred) with keys: _id, amount, method, student_id, fee_id, status, date
          - an object with attributes
        """
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Transaction Detail")
        dialog.geometry("500x420")
        dialog.grab_set()

        # Content frame
        content = ctk.CTkFrame(dialog, fg_color="white")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        def get(v, fallback="N/A"):
            if v is None:
                return fallback
            if isinstance(v, datetime):
                return v.strftime("%Y-%m-%d %H:%M:%S")
            return str(v)

        # helper to read from dict or object
        def read(key):
            if isinstance(tx, dict):
                return tx.get(key)
            else:
                return getattr(tx, key, None)

        rows = [
            ("Transaction ID:", get(read("_id"))),
            ("Amount:", get(read("amount"))),
            ("Method:", get(read("method"))),
            ("Student ID:", get(read("student_id"))),
            ("Fee ID:", get(read("fee_id"))),
            ("Status:", get(read("status"))),
            ("Date:", self._format_dt(read("date") or read("createAt"))),
        ]

        for label_text, value_text in rows:
            rowf = ctk.CTkFrame(content, fg_color="transparent")
            rowf.pack(fill="x", pady=8)
            ctk.CTkLabel(
                rowf,
                text=label_text,
                width=150,
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(side="left")
            ctk.CTkLabel(
                rowf, text=value_text, anchor="w", font=ctk.CTkFont(size=14)
            ).pack(side="left")

        ctk.CTkButton(dialog, text="Close", width=120, command=dialog.destroy).pack(
            pady=16
        )

    # -------------------------
    # Small helpers
    # -------------------------
    def show_error_dialog(self, message):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Error")
        dialog.geometry("380x160")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog, text=f"✗ {message}", font=ctk.CTkFont(size=16), text_color="#FF0000"
        ).pack(pady=20)
        ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy).pack(pady=8)


# Example usage (for ad-hoc testing)
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x700")
    root.title("Transaction Management")
    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)
    app = TransactionManagement(container, lambda: print("back"), None)
    root.mainloop()
