from models.database import db
from models.fee import Fee

try:
    FEES_COLLECTION = db.get_db()["fees"]
except Exception as e:
    print(f"Error connecting to 'fees' collection: {e}")


class FeeController:
    """Controller for handling Fee CRUD operations"""

    def get_all_fees(self):
        """Return all fees as Fee objects"""
        try:
            fees = FEES_COLLECTION.find()
            return {"success": True, "fees": [Fee(**f) for f in fees]}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def find_fee_by_id(self, fee_id):
        """Return a single Fee object by ID"""
        try:
            fee = Fee.find_by_id(fee_id)
            if fee:
                return {"success": True, "fee": fee}
            return {"success": False, "message": "Fee not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def create_fee(
        self, description, amount, student_id, dueDate, period, status="pending"
    ):
        """Create a new fee and save it to DB"""
        try:
            fee = Fee(description, amount, student_id, dueDate, period, status)
            fee.save()
            return {"success": True, "fee": fee}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_fee(self, fee_id, **kwargs):
        """Update fee by ID. kwargs can include description, amount, student_id, dueDate, period, status"""
        try:
            fee = Fee.find_by_id(fee_id)
            if not fee:
                return {"success": False, "message": "Fee not found"}

            for key, value in kwargs.items():
                if hasattr(fee, key):
                    setattr(fee, key, value)
            fee.save()
            return {"success": True, "fee": fee}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def mark_fee_paid(self, fee_id):
        """Mark a fee as paid"""
        try:
            fee = Fee.find_by_id(fee_id)
            if not fee:
                return {"success": False, "message": "Fee not found"}
            fee.markPaid()
            return {"success": True, "fee": fee}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_fees_by_student(self, student_id):
        """Return all fees for a specific student"""
        try:
            fees = Fee.find_by_student_id(student_id)
            return {"success": True, "fees": fees}
        except Exception as e:
            return {"success": False, "message": str(e)}
