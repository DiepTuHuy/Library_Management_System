from models.fine import Fine
from models.payment import Payment
from models.database import get_db
from datetime import datetime
from bson.objectid import ObjectId


class FineController:
    """Controller for fine management operations"""

    def __init__(self):
        self.db = get_db()

    def get_fine(self, fine_id):
        """Get fine details"""
        try:
            fine = Fine.get_by_id(self.db, fine_id)
            if not fine:
                return {"success": False, "message": "Fine not found"}

            return {
                "success": True,
                "fine": {
                    "id": str(fine._id),
                    "record_id": str(fine.record_id),
                    "amount": fine.amount,
                    "status": fine.status,
                    "created_at": fine.created_at.isoformat(),
                    "paid_date": fine.paid_date.isoformat() if fine.paid_date else None,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user_fines(self, user_id):
        """Get all fines for a user"""
        try:
            fines = Fine.get_by_user_id(self.db, user_id)
            fines_data = []
            total_amount = 0
            for fine in fines:
                fine_dict = {
                    "id": str(fine._id),
                    "record_id": str(fine.record_id),
                    "amount": fine.amount,
                    "status": fine.status,
                    "created_at": fine.created_at.isoformat(),
                }
                if fine.status == "pending":
                    total_amount += fine.amount
                fines_data.append(fine_dict)

            return {
                "success": True,
                "fines": fines_data,
                "total_pending": total_amount,
                "count": len(fines_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "fines": [], "count": 0}

    def get_all_pending_fines(self):
        """Get all pending fines in the system"""
        try:
            fines = Fine.get_all_pending(self.db)
            fines_data = []
            total_amount = 0
            for fine in fines:
                fines_data.append({
                    "id": str(fine._id),
                    "record_id": str(fine.record_id),
                    "amount": fine.amount,
                    "status": fine.status,
                    "created_at": fine.created_at.isoformat(),
                })
                total_amount += fine.amount

            return {
                "success": True,
                "fines": fines_data,
                "total_amount": total_amount,
                "count": len(fines_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "fines": [], "count": 0}

    def get_all_fines(self):
        """Get all fines"""
        try:
            fines = Fine.get_all(self.db)
            fines_data = []
            for fine in fines:
                fines_data.append({
                    "id": str(fine._id),
                    "record_id": str(fine.record_id),
                    "amount": fine.amount,
                    "status": fine.status,
                    "created_at": fine.created_at.isoformat(),
                    "paid_date": fine.paid_date.isoformat() if fine.paid_date else None,
                })

            return {
                "success": True,
                "fines": fines_data,
                "count": len(fines_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "fines": [], "count": 0}

    def pay_fine(self, fine_id, amount, method="cash"):
        """Pay a fine"""
        try:
            fine = Fine.get_by_id(self.db, fine_id)
            if not fine:
                return {"success": False, "message": "Fine not found"}

            if fine.status == "paid":
                return {"success": False, "message": "Fine already paid"}

            if amount < fine.amount:
                return {
                    "success": False,
                    "message": f"Insufficient amount. Required: {fine.amount}",
                }

            # Create payment
            payment = Payment(fine_id=fine_id, amount=amount, method=method)
            if not payment.save(self.db):
                return {"success": False, "message": "Failed to create payment"}

            # Mark fine as paid
            if not fine.mark_paid(self.db):
                return {"success": False, "message": "Failed to mark fine as paid"}

            change = amount - fine.amount
            return {
                "success": True,
                "message": "Fine paid successfully",
                "payment_id": str(payment._id),
                "amount_paid": amount,
                "change": change,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
