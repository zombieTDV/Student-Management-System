from models.fee import Fee
from models.transaction import Transaction
from bson.objectid import ObjectId
from datetime import datetime


class PaymentController:
    """Controller for handling payment operations"""

    def __init__(self):
        pass

    def get_student_payment_data(self, student_id):
        """
        Get payment data for payment view

        Args:
            student_id: Student's MongoDB ObjectId

        Returns:
            dict: {
                "success": bool,
                "student_info": dict,
                "fees": list of fee dicts
            }
        """
        try:
            from models.account import Account

            student = Account.find_by_id(student_id)

            if not student or student.role != "student":
                return {"success": False, "message": "Student not found"}

            # Get unpaid fees
            if not isinstance(student_id, ObjectId):
                student_id = ObjectId(student_id)

            all_fees = Fee.find_by_student_id(student_id)
            unpaid_fees = [f for f in all_fees if f.status in ["pending", "overdue"]]

            # Format fees for view
            formatted_fees = []
            for i, fee in enumerate(unpaid_fees, 1):
                formatted_fees.append(
                    {
                        "id": str(fee._id),
                        "index": str(i),
                        "name": f"{fee.description} - {fee.period}",
                        "fee": self._format_currency(fee.amount),
                        "remain": self._format_currency(fee.amount),
                        "raw_amount": fee.amount,
                    }
                )

            return {
                "success": True,
                "student_info": {
                    "id": str(student._id),
                    "name": getattr(student, "fullName", "N/A"),
                    "dob": getattr(student, "dob", "N/A"),
                    "major": getattr(student, "major", "N/A"),
                },
                "fees": formatted_fees,
            }

        except Exception as e:
            print(f"Error getting payment data: {e}")
            return {"success": False, "message": str(e)}

    def process_payment(self, student_id, selected_fee_ids):
        """
        Process payment for selected fees

        Args:
            student_id: Student's MongoDB ObjectId
            selected_fee_ids: List of fee IDs to pay

        Returns:
            dict: {"success": bool, "message": str, "total_paid": float}
        """
        try:
            if not selected_fee_ids:
                return {"success": False, "message": "No fees selected"}

            if not isinstance(student_id, ObjectId):
                student_id = ObjectId(student_id)

            total_paid = 0
            fees_paid = 0

            for fee_id in selected_fee_ids:
                fee = Fee.find_by_id(fee_id)

                if not fee or fee.student_id != student_id:
                    continue

                if fee.status == "paid":
                    continue

                # Create transaction
                transaction = Transaction(
                    amount=fee.amount,
                    method="student_portal",
                    student_id=student_id,
                    fee_id=fee._id,
                    status="completed",
                    date=datetime.utcnow(),
                )
                transaction.save()

                # Mark fee as paid
                fee.markPaid()

                total_paid += fee.amount
                fees_paid += 1

            if fees_paid == 0:
                return {"success": False, "message": "No fees were paid"}

            return {
                "success": True,
                "message": f"Successfully paid {fees_paid} fee(s)",
                "total_paid": total_paid,
            }

        except Exception as e:
            print(f"Error processing payment: {e}")
            return {"success": False, "message": str(e)}

    @staticmethod
    def _format_currency(amount):
        """Format amount to Vietnamese format (1.000.000)"""
        try:
            return f"{int(amount):,}".replace(",", ".")  # noqa: E231
        except Exception:
            return str(amount)
