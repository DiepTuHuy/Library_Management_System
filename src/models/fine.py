from bson import ObjectId
from datetime import datetime
from .database import get_db


class Fine:
    def __init__(
        self, record_id, amount, status="pending", fine_id=None
    ):
        self._id = fine_id
        self.record_id = (
            record_id if not isinstance(record_id, str) else ObjectId(record_id)
        )
        self.amount = amount
        self.status = status  # pending, paid
        self.created_at = datetime.utcnow()
        self.paid_date = None

    def save(self, db):
        """Save or update fine"""
        try:
            # Try to include user_id for easier queries
            user_id = None
            try:
                borrow = db["borrow_records"].find_one({"_id": self.record_id})
                if borrow:
                    user_id = borrow.get("user_id")
            except Exception:
                user_id = None

            fine_dict = {
                "record_id": self.record_id,
                "user_id": user_id,
                "amount": self.amount,
                "status": self.status,
                "created_at": self.created_at,
                "paid_date": self.paid_date,
                "is_active": False if self.status == "paid" else True,
            }
            if self._id:
                db["fines"].update_one({"_id": self._id}, {"$set": fine_dict})
            else:
                result = db["fines"].insert_one(fine_dict)
                self._id = result.inserted_id
            return True
        except Exception as e:
            print(f"Error saving fine: {e}")
            return False

    def mark_paid(self, db):
        """Mark fine as paid"""
        try:
            self.status = "paid"
            self.paid_date = datetime.utcnow()
            return self.save(db)
        except Exception as e:
            print(f"Error marking fine as paid: {e}")
            return False

    @staticmethod
    def get_by_id(db, fine_id):
        if isinstance(fine_id, str):
            fine_id = ObjectId(fine_id)
        fine_dict = db["fines"].find_one({"_id": fine_id})
        if fine_dict:
            return Fine._dict_to_fine(fine_dict)
        return None

    @staticmethod
    def get_by_record_id(db, record_id):
        """Get fine for a borrow record"""
        if isinstance(record_id, str):
            record_id = ObjectId(record_id)
        fine_dict = db["fines"].find_one({"record_id": record_id})
        if fine_dict:
            return Fine._dict_to_fine(fine_dict)
        return None

    @staticmethod
    def get_by_user_id(db, user_id):
        """Get all fines for a user via borrow records"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        fines = []
        # Get all borrow records for user
        borrow_records = db["borrow_records"].find({"user_id": user_id})
        record_ids = [rec["_id"] for rec in borrow_records]
        # Get all fines for those records
        for fine_dict in db["fines"].find({"record_id": {"$in": record_ids}}):
            fines.append(Fine._dict_to_fine(fine_dict))
        return fines

    @staticmethod
    def get_all_pending(db):
        """Get all pending fines"""
        fines = []
        for fine_dict in db["fines"].find({"status": "pending"}):
            fines.append(Fine._dict_to_fine(fine_dict))
        return fines

    @staticmethod
    def get_all(db):
        """Get all fines"""
        fines = []
        for fine_dict in db["fines"].find():
            fines.append(Fine._dict_to_fine(fine_dict))
        return fines

    # Fines → Payments (1-1)
    @staticmethod
    def get_payment(db, fine_id):
        if isinstance(fine_id, str):
            fine_id = ObjectId(fine_id)
        return db["payments"].find_one({"fine_id": fine_id})

    @staticmethod
    def _dict_to_fine(fine_dict):
        """Convert dict to Fine object"""
        fine = Fine(
            record_id=fine_dict.get("record_id"),
            amount=fine_dict.get("amount", 0),
            status=fine_dict.get("status", "pending"),
            fine_id=fine_dict.get("_id"),
        )
        fine.created_at = fine_dict.get("created_at")
        fine.paid_date = fine_dict.get("paid_date")
        return fine