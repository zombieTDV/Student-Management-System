import customtkinter as ctk
from tkinter import ttk

from controllers.student_controller import StudentController
from controllers.auth_controller import AuthController


class StudentManagement:
    def __init__(
        self,
        parent,
        back_callback,
        student_controller: StudentController,
        auth_controller: AuthController,
    ):
        self.parent = parent
        self.back_callback = back_callback
        self.student_controller = student_controller  # Store controller reference
        self.auth_controller = auth_controller

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

        # Load student data from controller
        self.load_students_from_controller()

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

    def load_students_from_controller(self):
        """Load student data from student_controller"""
        try:
            # Get all students from controller
            result = self.student_controller.get_all_students()

            if result["success"]:
                # Clear existing data in treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)

                # Load students into treeview
                for student in result["students"]:
                    # Map student data to table columns
                    values = (
                        student.get("id", ""),  # StudentID (MongoDB _id)
                        student.get("username", ""),  # Username
                        "*******",  # Password
                        student.get("email", ""),  # Email
                        student.get("fullName", ""),  # FullName
                        student.get("dob", ""),  # DOB
                        student.get("gender", ""),  # Gender
                        student.get("address", ""),  # Address
                        student.get("contact", ""),  # Contact
                        student.get("major", ""),  # Major
                        student.get("imageURL", ""),  # ImageURL
                    )
                    self.tree.insert("", "end", values=values)

                print(f"✓ Loaded {result['count']} students from database")
            else:
                print(
                    f"✗ Failed to load students: {result.get('message', 'Unknown error')}"
                )
                # Load sample data as fallback
                self.load_sample_data()

        except Exception as e:
            print(f"✗ Error loading students from controller: {e}")
            # Load sample data as fallback
            self.load_sample_data()

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
        resigter_callback = self.student_controller.register_student_by_admin(
            self.auth_controller.current_account, values[1], values[2]
        )
        if resigter_callback["success"] is True:
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
        else:
            print(resigter_callback)

    def save_changes(self):
        """Save all changes to database"""
        print("Saving all changes to database...")

        # Get all data from treeview
        all_students = []
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            all_students.append(values)

        print(f"Total students: {len(all_students)}")

        # Track results
        success_count = 0
        error_count = 0
        error_messages = []
        print("ok")
        # Update each student in database
        for student_values in all_students:
            try:
                # Extract student data from treeview row
                student_id = student_values[0]  # StudentID (MongoDB _id)
                username = student_values[1]
                # password = student_values[2]  # Skip password (it's masked)
                email = student_values[3]
                full_name = student_values[4]
                dob = student_values[5]
                gender = student_values[6]
                address = student_values[7]
                contact = student_values[8]
                major = student_values[9]
                image_url = student_values[10]

                # Get the student object from database
                from models.account import Account

                student = Account.find_by_id(student_id)

                if not student:
                    error_count += 1
                    error_messages.append(f"Student {username} not found in database")
                    continue

                # Prepare update data (only include non-empty fields)
                updated_data = {}

                if email and email.strip():
                    updated_data["email"] = email.strip()
                if full_name and full_name.strip():
                    updated_data["fullName"] = full_name.strip()
                if dob and dob.strip():
                    updated_data["dob"] = dob.strip()
                if gender and gender.strip():
                    updated_data["gender"] = gender.strip()
                if address and address.strip():
                    updated_data["address"] = address.strip()
                if contact and str(contact).strip():
                    updated_data["contact"] = str(contact).strip()
                if major and major.strip():
                    updated_data["major"] = major.strip()
                if image_url and str(image_url).strip() and str(image_url) != "None":
                    updated_data["imageURL"] = str(image_url).strip()

                # Update student profile using controller
                result = self.student_controller.update_student_profile(
                    student, updated_data
                )

                if result["success"]:
                    success_count += 1
                    print(f"✓ Updated {username}: {result.get('message', '')}")
                else:
                    error_count += 1
                    error_msg = f"{username}: {result.get('message', 'Unknown error')}"
                    error_messages.append(error_msg)
                    print(f"✗ Failed to update {username}: {result.get('message', '')}")

            except Exception as e:
                print(f"✗ Error updating student: {e}")

        # Show result dialog
        if error_count == 0:
            # All successful
            success_dialog = ctk.CTkToplevel(self.parent)
            success_dialog.title("Success")
            success_dialog.geometry("400x200")
            success_dialog.grab_set()

            ctk.CTkLabel(
                success_dialog,
                text="✓ All changes saved successfully!",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#22C55E",
            ).pack(pady=20)

            ctk.CTkLabel(
                success_dialog,
                text=f"Updated {success_count} student(s)",
                font=ctk.CTkFont(size=14),
            ).pack(pady=10)

            ctk.CTkButton(
                success_dialog,
                text="OK",
                width=120,
                height=40,
                command=success_dialog.destroy,
            ).pack(pady=20)
        else:
            # Some errors occurred
            result_dialog = ctk.CTkToplevel(self.parent)
            result_dialog.title("Save Results")
            result_dialog.geometry("500x400")
            result_dialog.grab_set()

            ctk.CTkLabel(
                result_dialog,
                text="Save Results",
                font=ctk.CTkFont(size=20, weight="bold"),
            ).pack(pady=20)

            # Success count
            ctk.CTkLabel(
                result_dialog,
                text=f"✓ Successfully saved: {success_count}",
                font=ctk.CTkFont(size=14),
                text_color="#22C55E",
            ).pack(pady=5)

            # Error count
            ctk.CTkLabel(
                result_dialog,
                text=f"✗ Failed to save: {error_count}",
                font=ctk.CTkFont(size=14),
                text_color="#FF0000",
            ).pack(pady=5)

            if error_messages:
                ctk.CTkLabel(
                    result_dialog,
                    text="Error Details:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                ).pack(pady=(10, 5))

                # Scrollable frame for error messages
                error_frame = ctk.CTkScrollableFrame(
                    result_dialog, width=450, height=150, fg_color="#FFF0F0"
                )
                error_frame.pack(pady=10, padx=20)

                for error_msg in error_messages:
                    ctk.CTkLabel(
                        error_frame,
                        text=f"• {error_msg}",
                        font=ctk.CTkFont(size=11),
                        text_color="#FF0000",
                        anchor="w",
                        wraplength=400,
                    ).pack(anchor="w", padx=10, pady=2)

            ctk.CTkButton(
                result_dialog,
                text="OK",
                width=120,
                height=40,
                command=result_dialog.destroy,
            ).pack(pady=20)


# Example usage
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1400x800")
    root.title("Student Management")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True)

    app = StudentManagement(container, None, None)
    root.mainloop()
