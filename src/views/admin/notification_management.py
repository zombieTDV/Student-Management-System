# notification_management.py
import customtkinter as ctk
from tkinter import ttk
from bson.objectid import ObjectId

from controllers.notifications_controller import NotificationsController
from controllers.auth_controller import AuthController


class NotificationManagement:
    def __init__(
        self,
        parent,
        back_callback,
        notifications_controller: NotificationsController,
        auth_controller: AuthController,  # optional; used to prefill admin id if available
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.notifications_controller = notifications_controller
        self.auth_controller = auth_controller

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
            text="Notifications",
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
            "AnnouncementID",
            "Title",
            "ContentPreview",
            "CreatedBy",
            "Status",
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

        # heading & column sizing
        self.tree.heading("AnnouncementID", text="AnnouncementID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("ContentPreview", text="Content (preview)")
        self.tree.heading("CreatedBy", text="CreatedBy")
        self.tree.heading("Status", text="Status")
        self.tree.heading("CreatedAt", text="CreatedAt")

        self.tree.column("AnnouncementID", width=160, minwidth=120, anchor="w")
        self.tree.column("Title", width=220, minwidth=150, anchor="w")
        self.tree.column("ContentPreview", width=420, minwidth=200, anchor="w")
        self.tree.column("CreatedBy", width=160, minwidth=120, anchor="w")
        self.tree.column("Status", width=120, minwidth=80, anchor="w")
        self.tree.column("CreatedAt", width=160, minwidth=120, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(20, 40))

        ctk.CTkButton(
            buttons_frame,
            text="New Announcement",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=220,
            height=60,
            corner_radius=15,
            command=self.add_notification_dialog,
        ).pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            buttons_frame,
            text="Delete Announcement",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#FF3B3B",
            hover_color="#FF0000",
            text_color="white",
            width=220,
            height=60,
            corner_radius=15,
            command=self.delete_notification,
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
            command=self.load_notifications,  # note: no parentheses here
        )
        refresh_btn.pack(side="left", padx=(0, 20))

        # double-click to view full announcement
        self.tree.bind("<Double-1>", self.on_double_click)

        # initial load
        self.load_notifications()

    def _preview_text(self, text, length=140):
        if not text:
            return ""
        s = str(text).replace("\n", " ")
        return s if len(s) <= length else s[: length - 3] + "..."

    def load_notifications(self):
        """Load announcements from controller. Handles lists of objects or dicts."""
        # clear tree
        self.tree.delete(*self.tree.get_children())

        try:
            res = self.notifications_controller.student_view_all_notifications()
            anns = res
            # if controller returned a dict with key 'announcements' or 'data' or 'success'
            if isinstance(res, dict):
                # try common keys
                if res.get("success") and "announcements" in res:
                    anns = res["announcements"]
                elif "announcements" in res:
                    anns = res["announcements"]
                elif "data" in res:
                    anns = res["data"]
                elif "result" in res:
                    anns = res["result"]
                else:
                    # fall back if the dict is actually a single announcement
                    anns = [res]
            if anns is None:
                anns = []

            for ann in anns:
                # support either object-like (attributes) or dict-like
                try:
                    ann_id = str(
                        getattr(
                            ann, "_id", ann.get("_id") if isinstance(ann, dict) else ""
                        )
                    )
                except Exception:
                    ann_id = (
                        str(ann.get("_id"))
                        if isinstance(ann, dict) and ann.get("_id")
                        else ""
                    )

                title = getattr(
                    ann, "title", ann.get("title") if isinstance(ann, dict) else ""
                )
                content = getattr(
                    ann, "content", ann.get("content") if isinstance(ann, dict) else ""
                )
                created_by = getattr(
                    ann,
                    "createBy",
                    ann.get("createBy") if isinstance(ann, dict) else "",
                )
                status = getattr(
                    ann, "status", ann.get("status") if isinstance(ann, dict) else ""
                )
                created_at = getattr(
                    ann,
                    "createdAt",
                    ann.get("createdAt") if isinstance(ann, dict) else "",
                )

                # if created_by is an ObjectId convert to str
                try:
                    if isinstance(created_by, ObjectId):
                        created_by = str(created_by)
                except Exception:
                    pass

                created_at_str = ""
                try:
                    if hasattr(created_at, "strftime"):
                        created_at_str = created_at.strftime("%d/%m/%Y %H:%M")
                    else:
                        created_at_str = str(created_at)
                except Exception:
                    created_at_str = str(created_at)

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        ann_id,
                        str(title),
                        self._preview_text(content, length=100),
                        str(created_by),
                        str(status),
                        created_at_str,
                    ),
                )
        except Exception as e:
            self.show_error_dialog(f"Failed to load announcements: {e}")

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        ann_id = self.tree.item(item[0])["values"][0]
        # Try to fetch the full announcement (best-effort)
        full_ann = None
        # 1) try controller.announcement_model.find_by_id if available
        try:
            model = getattr(self.notifications_controller, "announcement_model", None)
            if model and hasattr(model, "find_by_id"):
                full_ann = model.find_by_id(ann_id)
        except Exception:
            full_ann = None

        # 2) if still None, attempt to ask controller if it has a find_by_id naming variant
        if not full_ann:
            for name in ("find_by_id", "get_by_id", "get_announcement_by_id"):
                fn = getattr(self.notifications_controller, name, None)
                if callable(fn):
                    try:
                        full_ann = fn(ann_id)
                        break
                    except Exception:
                        full_ann = None

        # 3) if still None, just show the values we have in the tree (preview)
        if not full_ann:
            # show preview dialog with what's in the row
            values = self.tree.item(item[0])["values"]
            self.show_view_dialog(
                title=str(values[1]),
                content=f"(Full content unavailable)\n\nPreview:\n{values[2]}",
                meta=f"CreatedBy: {values[3]}\nStatus: {values[4]}\nCreatedAt: {values[5]}",
            )
            return

        # Try to extract fields from returned object/dict
        title = getattr(
            full_ann,
            "title",
            full_ann.get("title") if isinstance(full_ann, dict) else "",
        )
        content = getattr(
            full_ann,
            "content",
            full_ann.get("content") if isinstance(full_ann, dict) else "",
        )
        created_by = getattr(
            full_ann,
            "createBy",
            full_ann.get("createBy") if isinstance(full_ann, dict) else "",
        )
        status = getattr(
            full_ann,
            "status",
            full_ann.get("status") if isinstance(full_ann, dict) else "",
        )
        created_at = getattr(
            full_ann,
            "createdAt",
            full_ann.get("createdAt") if isinstance(full_ann, dict) else "",
        )

        meta = f"CreatedBy: {created_by}\nStatus: {status}\nCreatedAt: {created_at}"
        self.show_view_dialog(title=str(title), content=str(content), meta=meta)

    def add_notification_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Create Announcement")
        dialog.geometry("700x600")
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Title
        title_frame = ctk.CTkFrame(frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="Title:", width=120, anchor="w").pack(
            side="left"
        )
        title_entry = ctk.CTkEntry(title_frame, width=460)
        title_entry.pack(side="left", padx=10, fill="x", expand=True)

        # Content (multi-line)
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(content_frame, text="Content:", anchor="nw").pack(anchor="nw")
        content_text = ctk.CTkTextbox(content_frame, width=640, height=300)
        content_text.pack(pady=(8, 0), fill="both", expand=True)
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=12)

        ctk.CTkButton(
            btn_frame,
            text="Publish",
            width=140,
            command=lambda: self.post_notification(
                dialog,
                title_entry.get().strip(),
                content_text.get("0.0", "end").strip(),
            ),
        ).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="Cancel", width=140, command=dialog.destroy).pack(
            side="left", padx=8
        )

    def post_notification(self, dialog, title, content):
        if not title:
            self.show_error_dialog("Title is required.")
            return
        if not content:
            self.show_error_dialog("Content is required.")
            return

        try:
            result = self.notifications_controller.admin_post_announcement(
                title, content, self.auth_controller.current_account._id
            )
            if isinstance(result, dict) and result.get("success"):
                self.load_notifications()
                dialog.destroy()
                self.show_success_dialog(result.get("message", "Announcement posted"))
            else:
                # fallback if controller returns something else
                if isinstance(result, dict):
                    self.show_error_dialog(
                        result.get("message", "Failed to post announcement")
                    )
                else:
                    self.load_notifications()
                    self.show_success_dialog(
                        "Posted announcement (controller returned non-standard response)."
                    )
        except Exception as e:
            self.show_error_dialog(f"Failed to post announcement: {e}")

    def delete_notification(self):
        item = self.tree.selection()
        if not item:
            self.show_error_dialog("Select an announcement to delete!")
            return
        ann_id = self.tree.item(item[0])["values"][0]
        if not ann_id:
            self.show_error_dialog("Cannot determine announcement id.")
            return

        # Best-effort delete without asking for "DELETE" text
        deleted = False
        # 1) try controller has a delete method
        try:
            if hasattr(self.notifications_controller, "delete_announcement"):
                res = self.notifications_controller.delete_announcement(ann_id)
                if isinstance(res, dict) and res.get("success"):
                    deleted = True
                elif res is True:
                    deleted = True
        except Exception:
            pass

        # 2) try announcement_model on controller
        if not deleted:
            try:
                model = getattr(
                    self.notifications_controller, "announcement_model", None
                )
                if model:
                    if hasattr(model, "find_by_id"):
                        ann_obj = model.find_by_id(ann_id)
                    elif hasattr(model, "get_by_id"):
                        ann_obj = model.get_by_id(ann_id)
                    else:
                        ann_obj = None

                    if ann_obj:
                        for name in ("delete", "remove", "delete_one"):
                            fn = getattr(ann_obj, name, None)
                            if callable(fn):
                                fn()  # assume deletion
                                deleted = True
                                break
            except Exception:
                pass

        if deleted:
            self.load_notifications()
            self.show_success_dialog("Announcement deleted successfully!")
        else:
            self.show_error_dialog(
                "Failed to delete announcement (no delete method found)."
            )

    # Dialog helpers
    def show_view_dialog(self, title, content, meta=""):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title(title or "Announcement")
        dialog.geometry("700x520")
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=20, weight="bold")).pack(
            anchor="w", pady=(0, 8)
        )
        meta_label = ctk.CTkLabel(frame, text=meta, font=ctk.CTkFont(size=12))
        meta_label.pack(anchor="w", pady=(0, 8))

        txt = ctk.CTkTextbox(frame, width=640, height=360)
        txt.pack(fill="both", expand=True)
        txt.insert("0.0", content)
        txt.configure(state="disabled")

        ctk.CTkButton(dialog, text="Close", width=120, command=dialog.destroy).pack(
            pady=8
        )

    def show_success_dialog(self, message):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Success")
        dialog.geometry("350x150")
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
        dialog.geometry("500x260")
        dialog.grab_set()
        ctk.CTkLabel(
            dialog,
            text=f"✗ {message}",
            font=ctk.CTkFont(size=14),
            text_color="#FF0000",
            wraplength=440,
        ).pack(pady=20)
        ctk.CTkButton(dialog, text="OK", width=100, command=dialog.destroy).pack(
            pady=10
        )
