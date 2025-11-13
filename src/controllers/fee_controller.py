from models.database import db
from models.fee import Fee

from bson.objectid import ObjectId

try:
    FEES_COLLECTION = db.get_db()["fees"]
except Exception as e:
    print(f"Error connecting to 'fees' collection: {e}")


class FeeController:
    """Controller for managing Fee operations"""

    def get_all_fees(self):
        try:
            fees = Fee.find_all()
            return {"success": True, "fees": fees}
        except Exception as e:
            print(f"Error fetching fees: {e}")
            return {"success": False, "fees": []}

    def find_by_id(self, fee_id):
        """
        Find a fee by ID
        """
        try:
            fee = Fee.find_by_id(ObjectId(fee_id))
            return fee
        except Exception as e:
            print(f"Error finding fee by id {fee_id}: {e}")
            return None

    def create_fee(self, description, amount, student_id, dueDate, period):
        """
        Create a new Fee object
        """
        try:
            new_fee = Fee(
                description=description,
                amount=amount,
                student_id=ObjectId(student_id),
                dueDate=dueDate,
                period=period,
                status="Unpaid",  # default status
            )
            return new_fee
        except Exception as e:
            print(f"Error creating fee: {e}")
            return None

    def update_fee(self, fee_id, **kwargs):
        """
        Update an existing fee by ID
        """
        fee = self.find_by_id(fee_id)
        if not fee:
            return {"success": False, "message": "Fee not found"}
        try:
            for key, value in kwargs.items():
                setattr(fee, key, value)
            fee.save()
            return {"success": True, "message": "Fee updated successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def mark_paid(self, fee_id):
        """
        Mark a fee as paid
        """
        fee = self.find_by_id(fee_id)
        if not fee:
            return {"success": False, "message": "Fee not found"}
        try:
            fee.status = "Paid"
            fee.save()
            return {"success": True, "message": "Fee marked as paid"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_fee(self, fee_id):
        """
        Delete a fee by ID
        """
        fee = self.find_by_id(fee_id)
        if not fee:
            return {"success": False, "message": "Fee not found"}
        try:
            fee.delete()  # Assuming Fee model has a delete() method
            return {"success": True, "message": "Fee deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_fees_by_student(self, student_id):
        """
        Returns all fees for a given student _id.
        Output: {"success": True, "fees": [fee1, fee2, ...]}
        """
        try:
            fees = Fee.find_by_student_id(student_id)  # adjust based on your ORM/DB
            return {"success": True, "fees": fees}
        except Exception as e:
            return {"success": False, "error": str(e)}
