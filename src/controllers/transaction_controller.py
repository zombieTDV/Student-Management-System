# controllers/transaction_controller.py
from models.transaction import Transaction
from models.database import db
from bson.objectid import ObjectId


# Helper: raw collection for operations not provided by the model
TRANSACTIONS_COLLECTION = db.get_db()["transactions"]


class TransactionController:
    """
    Controller wrapping the Transaction model and the underlying collection.
    Methods return dicts consistent with other controllers in the app.
    """

    @staticmethod
    def _tx_to_dict(tx):
        """Convert a Transaction object to a serializable dict."""
        if tx is None:
            return None
        try:
            tx_id = getattr(tx, "_id", None)
            student_id = getattr(tx, "student_id", None)
            fee_id = getattr(tx, "fee_id", None)
            return {
                "_id": str(tx_id) if tx_id is not None else None,
                "amount": getattr(tx, "amount", None),
                "method": getattr(tx, "method", None),
                "student_id": str(student_id) if student_id is not None else None,
                "fee_id": str(fee_id) if fee_id is not None else None,
                "status": getattr(tx, "status", None),
                "date": getattr(tx, "date", None),
            }
        except Exception:
            # best-effort fallback
            return {
                "_id": str(getattr(tx, "_id", None)),
                "amount": getattr(tx, "amount", None),
                "method": getattr(tx, "method", None),
                "student_id": str(getattr(tx, "student_id", None)),
                "fee_id": str(getattr(tx, "fee_id", None)),
                "status": getattr(tx, "status", None),
                "date": getattr(tx, "date", None),
            }

    def get_all_transactions(self):
        """Return all transactions as a list of dicts."""
        try:
            cursor = TRANSACTIONS_COLLECTION.find().sort("date", -1)
            txs = []
            for doc in cursor:
                # doc is a raw dict from Mongo; convert to nice dict
                txs.append(
                    {
                        "_id": str(doc.get("_id")),
                        "amount": doc.get("amount"),
                        "method": doc.get("method"),
                        "student_id": (
                            str(doc.get("student_id"))
                            if doc.get("student_id")
                            else None
                        ),
                        "fee_id": str(doc.get("fee_id")) if doc.get("fee_id") else None,
                        "status": doc.get("status"),
                        "date": doc.get("date"),
                    }
                )
            return {"success": True, "transactions": txs, "count": len(txs)}
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fetch transactions: {e}",
                "transactions": [],
                "count": 0,
            }

    def find_by_id(self, tx_id):
        """Return single transaction as dict."""
        try:
            if not tx_id:
                return {
                    "success": False,
                    "message": "Transaction id is required",
                    "transaction": None,
                }

            tx_obj = Transaction.find_by_id(tx_id)
            if not tx_obj:
                return {
                    "success": False,
                    "message": "Transaction not found",
                    "transaction": None,
                }

            return {"success": True, "transaction": self._tx_to_dict(tx_obj)}
        except Exception as e:
            return {"success": False, "message": str(e), "transaction": None}

    def get_transactions_by_student(self, student_id):
        """
        Get transactions for a given student_id (string or ObjectId).
        Returns dict: {"success": True, "transactions": [...], "count": N}
        """
        try:
            if not student_id:
                return {
                    "success": False,
                    "message": "student_id required",
                    "transactions": [],
                    "count": 0,
                }

            txs = Transaction.find_by_student_id(student_id)
            tx_list = [self._tx_to_dict(tx) for tx in txs]
            return {"success": True, "transactions": tx_list, "count": len(tx_list)}
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching transactions: {e}",
                "transactions": [],
                "count": 0,
            }

    def get_transactions_by_fee(self, fee_id):
        """Get transactions related to a given fee_id."""
        try:
            if not fee_id:
                return {
                    "success": False,
                    "message": "fee_id required",
                    "transactions": [],
                    "count": 0,
                }

            txs = Transaction.find_by_fee_id(fee_id)
            tx_list = [self._tx_to_dict(tx) for tx in txs]
            return {"success": True, "transactions": tx_list, "count": len(tx_list)}
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching transactions: {e}",
                "transactions": [],
                "count": 0,
            }

    def create_transaction(
        self, amount, method, student_id, fee_id, status="completed", date=None
    ):
        """Create and save a new transaction; returns the created transaction dict."""
        try:
            # Normalize student_id / fee_id to ObjectId when creating Transaction
            sid = student_id
            fid = fee_id
            try:
                if sid and not isinstance(sid, ObjectId):
                    sid = ObjectId(sid)
            except Exception:
                # leave as-is if it cannot convert (model may accept string)
                pass
            try:
                if fid and not isinstance(fid, ObjectId):
                    fid = ObjectId(fid)
            except Exception:
                pass

            tx = Transaction(
                amount=amount,
                method=method,
                student_id=sid,
                fee_id=fid,
                status=status,
                date=date,
            )
            tx.save()
            return {"success": True, "transaction": self._tx_to_dict(tx)}
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create transaction: {e}",
                "transaction": None,
            }

    def delete_transaction(self, tx_id):
        """Delete a transaction by id (permanent)."""
        try:
            if not tx_id:
                return {"success": False, "message": "Transaction id required"}

            # Try model-level find
            tx_obj = Transaction.find_by_id(tx_id)
            if tx_obj and hasattr(tx_obj, "delete") and callable(tx_obj.delete):
                ok = tx_obj.delete()
                if ok:
                    return {"success": True, "message": "Transaction deleted"}
                else:
                    return {"success": False, "message": "Delete failed"}

            # fallback to direct collection delete
            res = TRANSACTIONS_COLLECTION.delete_one({"_id": ObjectId(tx_id)})
            if res.deleted_count == 1:
                return {"success": True, "message": "Transaction deleted"}
            else:
                return {"success": False, "message": "Transaction not found"}
        except Exception as e:
            return {"success": False, "message": f"Error deleting transaction: {e}"}
