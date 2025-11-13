# controllers/admin_controller.py
from models.account import Account

try:
    # If you have a dedicated Admin model, prefer that
    from models.admin import Admin  # optional
except Exception:
    Admin = None

import re
from bson.objectid import ObjectId


class AdminController:
    """Controller for simple admin account operations used by AdminManagement view."""

    # ------------------------
    # Core list/get methods
    # ------------------------
    def get_all_admins(self):
        """
        Return list of admin accounts in a serializable format:
        {"success": True, "admins": [...], "count": N}
        Falls back gracefully if model lacks helper methods.
        """
        try:
            # Prefer model-level helper if available
            if hasattr(Account, "find_all_admins"):
                admins = Account.find_all_admins()
            elif hasattr(Account, "find_all_accounts"):
                # fetch all and filter
                admins = [
                    a
                    for a in Account.find_all_accounts()
                    if getattr(a, "role", "") == "admin"
                ]
            else:
                # fallback to generic find_all_students style name
                admins = [
                    a
                    for a in Account.find_all_students()
                    if getattr(a, "role", "") == "admin"
                ]

            admins_data = []
            for a in admins:
                created_at = getattr(a, "createAt", None) or getattr(
                    a, "createdAt", None
                )
                created_str = created_at.strftime("%Y-%m-%d") if created_at else "N/A"

                admins_data.append(
                    {
                        "id": str(a._id),
                        "_id": str(a._id),
                        "username": getattr(a, "username", ""),
                        "email": getattr(a, "email", ""),
                        "fullName": getattr(a, "fullName", ""),
                        "role": getattr(a, "role", "admin"),
                        "contact": getattr(a, "contact", "")
                        or getattr(a, "phoneNumber", ""),
                        "createAt": created_str,
                    }
                )

            return {"success": True, "admins": admins_data, "count": len(admins_data)}

        except Exception as e:
            print(f"Error getting admins: {e}")
            return {"success": False, "message": str(e), "admins": [], "count": 0}

    def get_admin_by_id(self, admin_id):
        """
        Get single admin by ID.
        Returns: {"success": True, "admin": {...}} or {"success": False, "message": ...}
        """
        try:
            admin = Account.find_by_id(admin_id)
            if not admin or getattr(admin, "role", "") != "admin":
                return {"success": False, "message": "Admin not found"}

            created_at = getattr(admin, "createAt", None) or getattr(
                admin, "createdAt", None
            )
            created_str = created_at.strftime("%Y-%m-%d") if created_at else "N/A"

            admin_data = {
                "id": str(admin._id),
                "_id": str(admin._id),
                "username": admin.username,
                "email": admin.email,
                "fullName": getattr(admin, "fullName", ""),
                "role": getattr(admin, "role", "admin"),
                "contact": getattr(admin, "contact", "")
                or getattr(admin, "phoneNumber", ""),
                "createAt": created_str,
            }
            return {"success": True, "admin": admin_data}
        except Exception as e:
            print(f"Error getting admin by id: {e}")
            return {"success": False, "message": str(e)}

    # ------------------------
    # Search / helper methods
    # ------------------------
    def search_admins(self, search_term):
        """
        Search admins by username, email or fullName.
        Returns same shape as get_all_admins but filtered.
        """
        try:
            # Reuse get_all_admins and filter in memory (keeps single source of truth)
            res = self.get_all_admins()
            if not res.get("success"):
                return {
                    "success": False,
                    "message": res.get("message", "Failed to fetch admins"),
                    "admins": [],
                    "count": 0,
                }

            filtered = []
            for a in res["admins"]:
                if (
                    search_term.lower() in (a.get("username") or "").lower()
                    or search_term.lower() in (a.get("email") or "").lower()
                    or search_term.lower() in (a.get("fullName") or "").lower()
                ):
                    filtered.append(a)

            return {"success": True, "admins": filtered, "count": len(filtered)}
        except Exception as e:
            print(f"Error searching admins: {e}")
            return {"success": False, "message": str(e), "admins": [], "count": 0}

    def get_all_usernames(self):
        """
        Return all admin usernames (useful for dropdowns).
        Shape: {"success": True, "admins_usernames": [...], "count": N}
        """
        try:
            res = self.get_all_admins()
            if not res.get("success"):
                return {
                    "success": False,
                    "message": res.get("message", "Failed to fetch admins"),
                    "admins_usernames": [],
                    "count": 0,
                }

            usernames = [a["username"] for a in res["admins"]]
            return {
                "success": True,
                "admins_usernames": usernames,
                "count": len(usernames),
            }
        except Exception as e:
            print(f"Error getting admin usernames: {e}")
            return {
                "success": False,
                "message": str(e),
                "admins_usernames": [],
                "count": 0,
            }

    # ------------------------
    # Create / Delete helpers
    # ------------------------
    def create_admin(self, admin_profile):
        """
        Create a new admin account. admin_profile should contain at least username and password.
        Returns {"success": True, "admin": {...}} or {"success": False, "message": ...}
        """
        try:
            username = admin_profile.get("username")
            password = admin_profile.get("password")
            email = admin_profile.get("email", "")

            if not username or not password:
                return {
                    "success": False,
                    "message": "username and password are required",
                }

            # check existing username/email
            if Account.find_by_username(username):
                return {"success": False, "message": "Username already exists"}

            if email and Account.find_by_email(email):
                return {"success": False, "message": "Email already exists"}

            # Prefer Admin model if available
            if Admin is not None:
                new_admin = Admin(username=username, password=password, email=email)
                success = new_admin.save()
            else:
                new_admin = Account(
                    username=username, password=password, email=email, role="admin"
                )
                success = new_admin.save()

            if not success:
                return {"success": False, "message": "Failed to create admin"}

            return {
                "success": True,
                "admin": {
                    "id": str(new_admin._id),
                    "_id": str(new_admin._id),
                    "username": new_admin.username,
                    "email": new_admin.email,
                    "fullName": getattr(new_admin, "fullName", ""),
                    "role": getattr(new_admin, "role", "admin"),
                },
            }
        except Exception as e:
            print(f"Error creating admin: {e}")
            return {"success": False, "message": str(e)}

    def delete_admin(self, admin_id):
        """
        Delete an admin account by id (hard delete).
        Returns {"success": True, "message": "..."} or {"success": False, "message": "..."}
        """
        try:
            admin = Account.find_by_id(admin_id)
            if not admin or getattr(admin, "role", "") != "admin":
                return {"success": False, "message": "Admin not found"}

            # Call model delete if available
            deleted = False
            if hasattr(admin, "delete"):
                deleted = admin.delete()
            else:
                # fallback - try direct collection delete if available on Account
                if hasattr(Account, "delete_by_id"):
                    deleted = Account.delete_by_id(admin_id)
                else:
                    # as a last resort, attempt to remove via accounts collection if exposed
                    try:
                        from models.database import db

                        ACCOUNTS_COLLECTION = db.get_db()["accounts"]
                        result = ACCOUNTS_COLLECTION.delete_one(
                            {"_id": ObjectId(admin_id), "role": "admin"}
                        )
                        deleted = result.deleted_count > 0
                    except Exception:
                        deleted = False

            if deleted:
                return {"success": True, "message": "Admin deleted successfully"}
            else:
                return {"success": False, "message": "Failed to delete admin"}
        except Exception as e:
            print(f"Error deleting admin: {e}")
            return {"success": False, "message": str(e)}

    # ------------------------
    # Small validators (copied / adapted from StudentController)
    # ------------------------
    @staticmethod
    def _validate_username(username):
        if not username or len(username) < 3:
            return {"valid": False, "message": "Username must be at least 3 characters"}
        if len(username) > 50:
            return {
                "valid": False,
                "message": "Username must be less than 50 characters",
            }
        if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
            return {"valid": False, "message": "Username contains invalid characters"}
        return {"valid": True, "message": "Valid username"}

    @staticmethod
    def _validate_password(password):
        if not password:
            return {"valid": False, "message": "Password is required"}
        if len(password) > 128:
            return {
                "valid": False,
                "message": "Password must be less than 128 characters",
            }
        return {"valid": True, "message": "Valid password"}
