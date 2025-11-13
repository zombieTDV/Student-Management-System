from models.fee import Fee
from models.transaction import Transaction
from bson.objectid import ObjectId


class FinancialController:
    """Controller for handling financial summary operations"""

    def __init__(self):
        pass

    def get_financial_summary(self, student_id):
        """
        Get financial summary data for financial summary view

        Args:
            student_id: Student's MongoDB ObjectId

        Returns:
            dict: {
                "success": bool,
                "student_info": dict,
                "financial_data": list of fee dicts
            }
        """
        try:
            from models.account import Account

            student = Account.find_by_id(student_id)

            if not student or student.role != "student":
                return {"success": False, "message": "Student not found"}

            # Get all fees for student
            if not isinstance(student_id, ObjectId):
                student_id = ObjectId(student_id)

            all_fees = Fee.find_by_student_id(student_id)

            # Get all transactions
            all_transactions = Transaction.find_by_student_id(student_id)

            # Calculate paid amount for each fee
            fee_payments = {}
            for trans in all_transactions:
                if trans.status == "completed":
                    fee_id = str(trans.fee_id)
                    fee_payments[fee_id] = fee_payments.get(fee_id, 0) + trans.amount

            # Format fees for view
            formatted_data = []
            for i, fee in enumerate(all_fees, 1):
                fee_id = str(fee._id)
                paid_amount = fee_payments.get(fee_id, 0)
                remain_amount = fee.amount - paid_amount

                formatted_data.append(
                    {
                        "index": str(i),
                        "name": f"{fee.description} - {fee.period}",
                        "fee": self._format_currency(fee.amount),
                        "remain": self._format_currency(remain_amount),
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
                "financial_data": formatted_data,
            }

        except Exception as e:
            print(f"Error getting financial summary: {e}")
            return {"success": False, "message": str(e)}

    @staticmethod
    def _format_currency(amount):
        """Format amount to Vietnamese format (1.000.000)"""
        try:
            return f"{int(amount):,}".replace(",", ".")  # noqa: E231
        except Exception:
            return str(amount)
