import customtkinter as ctk
from tkinter import ttk
from bson.objectid import ObjectId

from controllers.student_controller import StudentController
from controllers.fee_controller import FeeController


class FinancialSummaryApp:
    def __init__(
        self,
        parent,
        student_id,
        student_controller: StudentController,
        fee_controller: FeeController,
        back_callback=None,
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.student_id = (
            ObjectId(student_id) if not isinstance(student_id, ObjectId) else student_id
        )
        self.student_controller = student_controller
        self.fee_controller = fee_controller

        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # --- Main container with rounded border ---
        main_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=50,
            border_width=3,
            border_color="black",
        )
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # --- Header with back arrow ---
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

        student_name = self._get_student_display_name()
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Financial Summary — {student_name}",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        title_label.pack(side="left")

        # --- Scrollable frame for fees table ---
        scrollable_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="white",
            corner_radius=0,
            scrollbar_button_color="#22C55E",
            scrollbar_button_hover_color="#16A34A",
        )
        scrollable_frame.pack(fill="both", expand=True, padx=60, pady=(0, 40))

        # --- Treeview container ---
        tree_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Columns
        self.column_config = {
            "Index": {"width": 100, "anchor": "center"},
            "Name": {"width": 400, "anchor": "w"},
            "Fee": {"width": 200, "anchor": "center"},
            "Remain": {"width": 200, "anchor": "center"},
        }
        columns = tuple(self.column_config.keys())

        # Treeview style
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=35,
            fieldbackground="white",
            font=("Arial", 14),
        )
        style.configure(
            "Treeview.Heading",
            background="#F0F0F0",
            foreground="black",
            font=("Arial", 14, "bold"),
        )
        style.map("Treeview", background=[("selected", "#22C55E")])

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12,
        )
        scrollbar.configure(command=self.tree.yview)

        for col, cfg in self.column_config.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=cfg["width"], anchor=cfg["anchor"])

        self.tree.pack(fill="both", expand=True)

        # --- Totals row ---
        self.total_row = ctk.CTkFrame(scrollable_frame, fg_color="#FFF7F7", height=60)
        self.total_row.pack(fill="x", pady=(10, 0), padx=0)
        self.total_row.pack_propagate(False)
        self.total_row.grid_columnconfigure(0, weight=1)
        self.total_row.grid_columnconfigure(1, weight=3)
        self.total_row.grid_columnconfigure(2, weight=2)
        self.total_row.grid_columnconfigure(3, weight=2)

        # "Total" label
        total_label_frame = ctk.CTkFrame(self.total_row, fg_color="transparent")
        total_label_frame.grid(row=0, column=1, sticky="w", padx=20)
        total_label = ctk.CTkLabel(
            total_label_frame,
            text="Total",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#111827",
        )
        total_label.pack(side="left", pady=12)

        # Totals columns
        self.total_fee_label = ctk.CTkLabel(
            self.total_row,
            text="0",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#EF4444",
        )
        self.total_fee_label.grid(row=0, column=2, sticky="nsew")
        self.total_unpaid_label = ctk.CTkLabel(
            self.total_row,
            text="0",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#EF4444",
        )
        self.total_unpaid_label.grid(row=0, column=3, sticky="nsew")

        # Load data
        self.load_financial_data()

    # -----------------------
    # Helpers
    # -----------------------
    def _get_student_display_name(self):
        try:
            if hasattr(self.student_controller, "get_student_by_id"):
                res = self.student_controller.get_student_by_id(str(self.student_id))
                if res.get("success") and res.get("student"):
                    return (
                        res["student"].get("fullName")
                        or res["student"].get("username")
                        or str(self.student_id)
                    )
        except Exception:
            pass
        return str(self.student_id)

    def load_financial_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        result = self.fee_controller.get_fees_by_student(self.student_id)
        if not result.get("success"):
            self.tree.insert("", "end", values=("", "No fees found or error", "", ""))
            self._update_totals(0, 0)
            return

        fees = result.get("fees", [])
        total_all = 0
        total_unpaid = 0
        for idx, fee in enumerate(fees, start=1):
            amount = self._safe_number(
                getattr(
                    fee, "amount", fee.get("amount") if isinstance(fee, dict) else 0
                )
            )
            status = (
                getattr(fee, "status", None)
                or (fee.get("status") if isinstance(fee, dict) else "")
            ).lower()
            remain = 0 if status == "paid" else amount
            total_all += amount
            total_unpaid += remain
            desc = getattr(fee, "description", None) or (
                fee.get("description") if isinstance(fee, dict) else ""
            )
            self.tree.insert(
                "",
                "end",
                values=(
                    str(idx),
                    desc or "(no description)",
                    self._format_number(amount),
                    self._format_number(remain),
                ),
            )

        self._update_totals(total_all, total_unpaid)

    def _update_totals(self, total_all, total_unpaid):
        self.total_fee_label.configure(text=self._format_number(total_all))
        self.total_unpaid_label.configure(text=self._format_number(total_unpaid))

    def _safe_number(self, v):
        if v is None:
            return 0
        if isinstance(v, (int, float)):
            return int(round(v))
        s = str(v).replace(".", "").replace(",", "")
        try:
            return int(float(s))
        except Exception as e:
            print(e)
            return 0

    def _format_number(self, n):
        try:
            n = int(round(n))
        except Exception as e:
            print(e)
            n = 0
        return f"{n:,}".replace(",", ".")
