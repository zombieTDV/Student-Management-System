import customtkinter as ctk
from tkinter import ttk


class StudentManagement:
    def __init__(self, parent, back_callback=None):
        self.parent = parent
        self.back_callback = back_callback

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

        # Header with back arrow
        header_frame = ctk.CTkFrame(main_frame, fg_color="white")
        header_frame.pack(anchor="w", padx=60, pady=(40, 30))

        # Back arrow button
        back_arrow = ctk.CTkLabel(
            header_frame,
            text="🔙",  # the typical back arrow
            font=ctk.CTkFont(size=70, weight="bold"),
            text_color="#FF7B7B",
            cursor="hand2",
        )
        back_arrow.pack(side="left", padx=(0, 20))

        if back_callback:
            back_arrow.bind("<Button-1>", lambda e: back_callback())

        # Header title
        header_label = ctk.CTkLabel(
            header_frame,
            text="Student",
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

        # Create Treeview for table
        style = ttk.Style()
        style.theme_use("default")

        # Configure Treeview colors
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

        # Create frame for treeview and scrollbar
        tree_frame = ctk.CTkFrame(table_container, fg_color="white")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        # Define columns
        columns = (
            "StudentID",
            "Username",
            "Password",
            "Email",
            "FullName",
            "DOB",
            "Gender",
            "Address",
            "Contact",
            "Major",
            "ImageURL",
        )

        # Create Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12,
        )

        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)

        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=100, anchor="w")

        self.tree.pack(fill="both", expand=True)

        # Load sample data
        self.load_sample_data()

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="white")
        buttons_frame.pack(fill="x", padx=60, pady=(20, 40))

        # Register new student button
        register_btn = ctk.CTkButton(
            buttons_frame,
            text="Resigter new\nstudent",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#FF7B7B",
            hover_color="#FF6B6B",
            text_color="white",
            width=220,
            height=80,
            corner_radius=15,
            command=self.register_new_student,
        )
        register_btn.pack(side="left", padx=(0, 20))

        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Save",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            text_color="white",
            width=220,
            height=80,
            corner_radius=15,
            command=self.save_changes,
        )
        save_btn.pack(side="left")

        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.on_double_click)

    def load_sample_data(self):
        """Load sample student data"""
        sample_students = [
            (
                "2021001",
                "john_doe",
                "********",
                "john@email.com",
                "John Doe",
                "01/15/2000",
                "Male",
                "123 Main St",
                "555-0101",
                "Computer Science",
                "",
            ),
            (
                "2021002",
                "jane_smith",
                "********",
                "jane@email.com",
                "Jane Smith",
                "03/22/2001",
                "Female",
                "456 Oak Ave",
                "555-0102",
                "Business Admin",
                "",
            ),
            (
                "2021003",
                "bob_jones",
                "********",
                "bob@email.com",
                "Bob Jones",
                "07/10/1999",
                "Male",
                "789 Pine Rd",
                "555-0103",
                "Engineering",
                "",
            ),
            (
                "2021004",
                "alice_wong",
                "********",
                "alice@email.com",
                "Alice Wong",
                "11/05/2000",
                "Female",
                "321 Elm St",
                "555-0104",
                "Mathematics",
                "",
            ),
            (
                "2021005",
                "charlie_brown",
                "********",
                "charlie@email.com",
                "Charlie Brown",
                "09/18/2001",
                "Male",
                "654 Maple Dr",
                "555-0105",
                "Physics",
                "",
            ),
        ]

        for student in sample_students:
            self.tree.insert("", "end", values=student)

    def on_double_click(self, event):
        """Handle double-click on table row"""
        item = self.tree.selection()
        if item:
            values = self.tree.item(item[0])["values"]
            print(f"Edit student: {values}")
            # Open edit dialog or form
            self.open_edit_dialog(values)

    def open_edit_dialog(self, student_data):
        """Open dialog to edit student information"""
        # Create a popup window
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Student")
        dialog.geometry("600x700")

        # Make it modal
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Edit Student Information",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=20)

        # Create form fields
        fields = [
            "StudentID",
            "Username",
            "Password",
            "Email",
            "FullName",
            "DOB",
            "Gender",
            "Address",
            "Contact",
            "Major",
            "ImageURL",
        ]

        entries = {}
        for i, (field, value) in enumerate(zip(fields, student_data)):
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=40, pady=5)

            ctk.CTkLabel(frame, text=field + ":", width=100, anchor="w").pack(
                side="left"
            )
            entry = ctk.CTkEntry(frame, width=350)
            entry.insert(0, str(value))
            entry.pack(side="left", padx=10)
            entries[field] = entry

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            width=120,
            command=lambda: self.save_edit(dialog, entries),
        ).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", width=120, command=dialog.destroy).pack(
            side="left", padx=10
        )

    def save_edit(self, dialog, entries):
        """Save edited student data"""
        # Get values from entries
        values = [entry.get() for entry in entries.values()]
        print(f"Saving: {values}")

        # Update the selected row in treeview
        selected = self.tree.selection()
        if selected:
            self.tree.item(selected[0], values=values)

        dialog.destroy()

    def register_new_student(self):
        """Open form to register new student - only username and password required"""
        print("Register new student clicked")
        # Create registration form
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Register New Student")
        dialog.geometry("550x350")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Register New Student",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=30)

        ctk.CTkLabel(
            dialog,
            text="Only username and password are required.\n\
                Other fields will be auto-generated.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(pady=10)

        # Only username and password fields
        entries = {}

        # Username field
        username_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        username_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(
            username_frame,
            text="Username:",
            width=100,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(side="left")
        username_entry = ctk.CTkEntry(
            username_frame,
            width=300,
            placeholder_text="Enter username",
            font=ctk.CTkFont(size=14),
        )
        username_entry.pack(side="left", padx=10)
        entries["Username"] = username_entry

        # Password field
        password_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        password_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkLabel(
            password_frame,
            text="Password:",
            width=100,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        ).pack(side="left")
        password_entry = ctk.CTkEntry(
            password_frame,
            width=300,
            placeholder_text="Enter password",
            show="●",
            font=ctk.CTkFont(size=14),
        )
        password_entry.pack(side="left", padx=10)
        entries["Password"] = password_entry

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=30)

        ctk.CTkButton(
            btn_frame,
            text="Register",
            width=140,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#45A049",
            command=lambda: self.add_new_student(dialog, entries),
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=140,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="gray",
            hover_color="#666666",
            command=dialog.destroy,
        ).pack(side="left", padx=10)

    def add_new_student(self, dialog, entries):
        """Add new student to table - auto-generate StudentID \
            and leave other fields blank"""
        username = entries["Username"].get().strip()
        password = entries["Password"].get().strip()

        # Validate that username and password are filled
        if not username or not password:
            error_dialog = ctk.CTkToplevel(dialog)
            error_dialog.title("Error")
            error_dialog.geometry("350x150")
            error_dialog.grab_set()

            ctk.CTkLabel(
                error_dialog,
                text="⚠️ Username and Password are required!",
                font=ctk.CTkFont(size=16),
                text_color="#FF0000",
            ).pack(pady=30)
            ctk.CTkButton(
                error_dialog, text="OK", width=100, command=error_dialog.destroy
            ).pack(pady=10)
            return

        # Check if username already exists
        for item in self.tree.get_children():
            existing_username = self.tree.item(item)["values"][1]
            if existing_username == username:
                error_dialog = ctk.CTkToplevel(dialog)
                error_dialog.title("Error")
                error_dialog.geometry("350x150")
                error_dialog.grab_set()

                ctk.CTkLabel(
                    error_dialog,
                    text="⚠️ Username already exists!",
                    font=ctk.CTkFont(size=16),
                    text_color="#FF0000",
                ).pack(pady=30)
                ctk.CTkButton(
                    error_dialog, text="OK", width=100, command=error_dialog.destroy
                ).pack(pady=10)
                return

        # Auto-generate StudentID
        import random
        from datetime import datetime

        year = datetime.now().year
        student_id = f"{year}{random.randint(1000, 9999)}"

        # Create student with only username and password, rest are blank
        values = [
            student_id,  # Auto-generated StudentID
            username,  # Username (required)
            password,  # Password (required) - will be hashed in real implementation
            "",  # Email (blank)
            "",  # FullName (blank)
            "",  # DOB (blank)
            "",  # Gender (blank)
            "",  # Address (blank)
            "",  # Contact (blank)
            "",  # Major (blank)
            "",  # ImageURL (blank)
        ]

        # Add to treeview
        self.tree.insert("", "end", values=values)
        print(f"New student registered: ID={student_id}, Username={username}")

        dialog.destroy()

        # Show success message
        success_dialog = ctk.CTkToplevel(self.parent)
        success_dialog.title("Success")
        success_dialog.geometry("400x200")
        success_dialog.grab_set()

        ctk.CTkLabel(
            success_dialog,
            text="✓ Student Registered Successfully!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#22C55E",
        ).pack(pady=20)
        ctk.CTkLabel(
            success_dialog,
            text=f"Student ID: {student_id}\nUsername: {username}",
            font=ctk.CTkFont(size=14),
        ).pack(pady=10)
        ctk.CTkLabel(
            success_dialog,
            text="Student can update other details later.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(pady=5)
        ctk.CTkButton(
            success_dialog,
            text="OK",
            width=120,
            height=40,
            command=success_dialog.destroy,
        ).pack(pady=20)

    def save_changes(self):
        """Save all changes to database"""
        print("Saving all changes to database...")
        # Get all data from treeview
        all_students = []
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            all_students.append(values)

        print(f"Total students: {len(all_students)}")
        # TODO: Save to MongoDB

        # Show success message
        success_dialog = ctk.CTkToplevel(self.parent)
        success_dialog.title("Success")
        success_dialog.geometry("300x150")
        success_dialog.grab_set()

        ctk.CTkLabel(
            success_dialog,
            text="✓ Changes saved successfully!",
            font=ctk.CTkFont(size=16),
        ).pack(pady=30)
        ctk.CTkButton(
            success_dialog, text="OK", width=100, command=success_dialog.destroy
        ).pack(pady=10)


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Student Management")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    app = StudentManagement(container)
    root.mainloop()
