from models.payment import Payment
from models.fine import Fine
from models.database import get_db
from datetime import datetime
from bson.objectid import ObjectId


class PaymentController:
    """Controller for payment management operations"""

    def __init__(self):
        self.db = get_db()

    def process_payment(self, fine_id, amount, method="cash"):
        """Process payment for a fine"""
        try:
            fine = Fine.get_by_id(self.db, fine_id)
            if not fine:
                return {"success": False, "message": "Fine not found"}

            if fine.status == "paid":
                return {"success": False, "message": "Fine already paid"}

            if amount < fine.amount:
                return {"success": False, "message": f"Amount insufficient. Required: {fine.amount}"}

            # Create payment record
            payment = Payment(fine_id=fine_id, amount=amount, method=method)
            if not payment.save(self.db):
                return {"success": False, "message": "Failed to process payment"}

            # Mark fine as paid
            if not fine.mark_paid(self.db):
                return {"success": False, "message": "Failed to mark fine as paid"}

            return {
                "success": True,
                "message": "Payment processed successfully",
                "payment_id": str(payment._id),
                "change": amount - fine.amount,
                "paid_at": payment.paid_at.isoformat(),
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_payment(self, payment_id):
        """Get payment details"""
        try:
            payment = Payment.get_by_id(self.db, payment_id)
            if not payment:
                return {"success": False, "message": "Payment not found"}

            return {
                "success": True,
                "payment": {
                    "id": str(payment._id),
                    "fine_id": str(payment.fine_id),
                    "amount": payment.amount,
                    "method": payment.method,
                    "status": payment.status,
                    "paid_at": payment.paid_at.isoformat(),
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_payments_by_fine(self, fine_id):
        """Get all payments for a fine"""
        try:
            if isinstance(fine_id, str):
                fine_id = ObjectId(fine_id)
            
            payments = []
            for payment_dict in self.db["payments"].find({"fine_id": fine_id}):
                payment = Payment._dict_to_payment(payment_dict)
                payments.append({
                    "id": str(payment._id),
                    "amount": payment.amount,
                    "method": payment.method,
                    "status": payment.status,
                    "paid_at": payment.paid_at.isoformat(),
                })

            return {
                "success": True,
                "payments": payments,
                "count": len(payments),
                "total_paid": sum(p["amount"] for p in payments),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "payments": [], "count": 0}

    def get_all_payments(self):
        """Get all payments in the system"""
        try:
            payments = Payment.get_all(self.db)
            payments_data = []
            total_collected = 0

            for payment in payments:
                payment_dict = {
                    "id": str(payment._id),
                    "fine_id": str(payment.fine_id),
                    "amount": payment.amount,
                    "method": payment.method,
                    "status": payment.status,
                    "paid_at": payment.paid_at.isoformat(),
                }
                payments_data.append(payment_dict)
                total_collected += payment.amount

            return {
                "success": True,
                "payments": payments_data,
                "count": len(payments_data),
                "total_collected": total_collected,
            }
        except Exception as e:
            return {"success": False, "message": str(e), "payments": [], "count": 0}

    def get_payments_by_method(self, method):
        """Get payments by payment method"""
        try:
            payments = []
            for payment_dict in self.db["payments"].find({"method": method}):
                payment = Payment._dict_to_payment(payment_dict)
                payments.append({
                    "id": str(payment._id),
                    "fine_id": str(payment.fine_id),
                    "amount": payment.amount,
                    "paid_at": payment.paid_at.isoformat(),
                })

            return {
                "success": True,
                "payments": payments,
                "method": method,
                "count": len(payments),
                "total": sum(p["amount"] for p in payments),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "payments": [], "count": 0}

    def get_payments_by_date_range(self, start_date, end_date):
        """Get payments within a date range"""
        try:
            payments = Payment.get_by_date_range(self.db, start_date, end_date)
            payments_data = []
            total = 0

            for payment in payments:
                payment_dict = {
                    "id": str(payment._id),
                    "fine_id": str(payment.fine_id),
                    "amount": payment.amount,
                    "method": payment.method,
                    "paid_at": payment.paid_at.isoformat(),
                }
                payments_data.append(payment_dict)
                total += payment.amount

            return {
                "success": True,
                "payments": payments_data,
                "count": len(payments_data),
                "total": total,
                "start_date": start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
                "end_date": end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "payments": [], "count": 0}
