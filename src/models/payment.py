from bson import ObjectId
from datetime import datetime
from models.database import get_db


class Payment:
    def __init__(self, fine_id, amount, method="cash", payment_id=None):
        self._id = payment_id
        self.fine_id = fine_id if not isinstance(fine_id, str) else ObjectId(fine_id)
        self.amount = amount
        self.method = method  # cash, credit_card, bank_transfer, etc.
        self.status = "completed"
        self.paid_at = datetime.utcnow()

    def save(self, db):
        """Save payment record"""
        try:
            payment_dict = {
                "fine_id": self.fine_id,
                "amount": self.amount,
                "method": self.method,
                "status": self.status,
                "paid_at": self.paid_at,
            }
            if self._id:
                db["payments"].update_one(
                    {"_id": self._id}, {"$set": payment_dict}
                )
            else:
                result = db["payments"].insert_one(payment_dict)
                self._id = result.inserted_id
            return True
        except Exception as e:
            print(f"Error saving payment: {e}")
            return False

    @staticmethod
    def get_by_id(db, payment_id):
        if isinstance(payment_id, str):
            payment_id = ObjectId(payment_id)
        payment_dict = db["payments"].find_one({"_id": payment_id})
        if payment_dict:
            return Payment._dict_to_payment(payment_dict)
        return None

    @staticmethod
    def get_by_fine_id(db, fine_id):
        """Get payment for a fine"""
        if isinstance(fine_id, str):
            fine_id = ObjectId(fine_id)
        payment_dict = db["payments"].find_one({"fine_id": fine_id})
        if payment_dict:
            return Payment._dict_to_payment(payment_dict)
        return None

    @staticmethod
    def get_all(db):
        """Get all payments"""
        payments = []
        for payment_dict in db["payments"].find():
            payments.append(Payment._dict_to_payment(payment_dict))
        return payments

    @staticmethod
    def get_by_date_range(db, start_date, end_date):
        """Get payments within a date range"""
        payments = []
        for payment_dict in db["payments"].find(
            {"paid_at": {"$gte": start_date, "$lte": end_date}}
        ):
            payments.append(Payment._dict_to_payment(payment_dict))
        return payments

    @staticmethod
    def _dict_to_payment(payment_dict):
        """Convert dict to Payment object"""
        payment = Payment(
            fine_id=payment_dict.get("fine_id"),
            amount=payment_dict.get("amount", 0),
            method=payment_dict.get("method", "cash"),
            payment_id=payment_dict.get("_id"),
        )
        payment.status = payment_dict.get("status", "completed")
        payment.paid_at = payment_dict.get("paid_at")
        return payment
