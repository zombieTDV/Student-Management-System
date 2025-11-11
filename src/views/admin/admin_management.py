import customtkinter as ctk
from tkinter import ttk


class AdminManagement:
    """
    Simple admin management view — view-only details + back navigation.
    Expects:
      - admin_controller with get_all_admins() -> {"success": True, "admins": [...], "count": N}
      - admin_controller.get_admin_by_id(admin_id) -> {"success": True, "admin": {...}}
      - auth_controller (optional) if you want to check current account
    """

    def __init__(
        self, parent, back_callback, admin_controller=None, auth_controller=None
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.admin_controller = admin_controller
        self.auth_controller = auth_controller

        # Visual theme (keep consistent with other views)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Main container with rounded border (consistent style)
        main_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=50,
            border_width=3,
            border_color="black",
        )
        main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header: back arrow + title
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
            text="Admin",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold"),
            text_color="#22C55E",
        )
        header_label.pack(side="left")

        # Table container with border
        table_container = ctk.CTkFrame(
            main_frame,
            fg_color="white",
            corner_radius=10,
            border_width=2,
            border_color="black",
        )
        table_container.pack(fill="both", expand=True, padx=60, pady=(0, 30))

        # Treeview styling (consistent with Student management)
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

        # Frame for treeview + scrollbar
        tree_frame = ctk.CTkFrame(table_container, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Columns for admins (kept compact)
        columns = (
            "AdminID",
            "Username",
            "Email",
            "FullName",
            "Role",
            "Contact",
            "CreatedAt",
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
            # set a reasonable width
            self.tree.column(col, width=140, minwidth=100, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Load admins
        self.load_admins_from_controller()

        # Buttons frame (only view detail + refresh + back)
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(20, 40))

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
            command=self.load_admins_from_controller,
        )
        refresh_btn.pack(side="left", padx=(20, 20))

        # Double-click => open detail
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_admins_from_controller(self):
        """Load admin accounts from controller into treeview"""
        print("Refreshed admin management view!")
        # clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if not self.admin_controller:
                # no controller -> load sample data
                self.load_sample_data()
                return

            res = self.admin_controller.get_all_admins()
            if res.get("success"):
                admins = res.get("admins", [])
                for admin in admins:
                    created_at = admin.get("createAt") or admin.get("createdAt") or ""
                    # normalize datetime if necessary
                    if hasattr(created_at, "strftime"):
                        created_at = created_at.strftime("%Y-%m-%d")
                    values = (
                        admin.get("id") or admin.get("_id") or "",
                        admin.get("username", ""),
                        admin.get("email", ""),
                        admin.get("fullName", ""),
                        admin.get("role", "admin"),
                        admin.get("contact", ""),
                        created_at,
                    )
                    self.tree.insert("", "end", values=values)
                return

            # failed -> sample fallback
            print(f"✗ Failed to load admins: {res.get('message', 'Unknown error')}")
            self.load_sample_data()
        except Exception as e:
            print(f"✗ Error loading admins: {e}")
            self.load_sample_data()

    def load_sample_data(self):
        """Fallback sample admins"""
        sample_admins = [
            (
                "A2023001",
                "sys_admin",
                "sys@school.edu",
                "System Admin",
                "admin",
                "0123456789",
                "2023-01-01",
            ),
            (
                "A2023002",
                "alice_admin",
                "alice@school.edu",
                "Alice Admin",
                "admin",
                "0987654321",
                "2024-03-15",
            ),
        ]
        for row in sample_admins:
            self.tree.insert("", "end", values=row)

    def on_double_click(self, event):
        item = self.tree.selection()
        if item:
            self.open_selected_detail()

    def open_selected_detail(self):
        """Open detail modal for selected admin"""
        sel = self.tree.selection()
        if not sel:
            self.show_error_dialog("Please select an admin to view details.")
            return

        values = self.tree.item(sel[0])["values"]
        admin_id = values[0]

        # Fetch detail from controller if available
        admin_data = None
        if self.admin_controller:
            try:
                res = self.admin_controller.get_admin_by_id(admin_id)
                if res.get("success"):
                    admin_data = res.get("admin")
                else:
                    # fallback to row values
                    admin_data = {
                        "_id": admin_id,
                        "username": values[1],
                        "email": values[2],
                        "fullName": values[3],
                        "role": values[4],
                        "contact": values[5],
                        "createAt": values[6],
                    }
            except Exception:
                admin_data = {
                    "_id": admin_id,
                    "username": values[1],
                    "email": values[2],
                    "fullName": values[3],
                    "role": values[4],
                    "contact": values[5],
                    "createAt": values[6],
                }
        else:
            admin_data = {
                "_id": admin_id,
                "username": values[1],
                "email": values[2],
                "fullName": values[3],
                "role": values[4],
                "contact": values[5],
                "createAt": values[6],
            }

        # Show modal detail (read-only)
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Admin Detail")
        dialog.geometry("560x520")
        dialog.grab_set()

        header = ctk.CTkLabel(
            dialog, text="Admin Details", font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=16)

        fields = [
            ("AdminID", admin_data.get("_id", "")),
            ("Username", admin_data.get("username", "")),
            ("Email", admin_data.get("email", "")),
            ("Full Name", admin_data.get("fullName", "")),
            ("Role", admin_data.get("role", "")),
            ("Contact", admin_data.get("contact", "")),
            (
                "Created At",
                admin_data.get("createAt", "") or admin_data.get("createAt", ""),
            ),
        ]

        for label_text, value in fields:
            row = ctk.CTkFrame(dialog, fg_color="transparent")
            row.pack(fill="x", padx=28, pady=6)
            ctk.CTkLabel(row, text=f"{label_text}:", width=120, anchor="w").pack(
                side="left"
            )
            val_label = ctk.CTkLabel(row, text=str(value), anchor="w")
            val_label.pack(side="left", padx=10)

        ctk.CTkButton(dialog, text="Close", width=120, command=dialog.destroy).pack(
            pady=20
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
