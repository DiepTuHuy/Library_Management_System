from bson import ObjectId
from datetime import datetime, timedelta
from models.database import get_db


class BorrowRecord:
    BORROW_DURATION_DAYS = 14  # Default borrow period
    FINE_PER_DAY = 1000  # 1000 VND per day

    def __init__(
        self,
        user_id,
        book_id,
        borrow_date=None,
        due_date=None,
        return_date=None,
        record_id=None,
    ):
        self._id = record_id
        self.user_id = user_id if not isinstance(user_id, str) else ObjectId(user_id)
        self.book_id = book_id if not isinstance(book_id, str) else ObjectId(book_id)
        self.borrow_date = borrow_date or datetime.utcnow()
        self.due_date = due_date or (
            datetime.utcnow() + timedelta(days=self.BORROW_DURATION_DAYS)
        )
        self.return_date = return_date  # None if not returned
        self.fine_id = None  # Linked to Fine record if late

    def save(self, db):
        """Save or update borrow record"""
        try:
            record_dict = {
                "user_id": self.user_id,
                "book_id": self.book_id,
                "borrow_date": self.borrow_date,
                "due_date": self.due_date,
                "return_date": self.return_date,
                "fine_id": self.fine_id,
            }
            if self._id:
                db["borrow_records"].update_one(
                    {"_id": self._id}, {"$set": record_dict}
                )
            else:
                result = db["borrow_records"].insert_one(record_dict)
                self._id = result.inserted_id
            return True
        except Exception as e:
            print(f"Error saving borrow record: {e}")
            return False

    def is_overdue(self):
        """Check if book is overdue"""
        if self.return_date:
            return False  # Already returned
        return datetime.utcnow() > self.due_date

    def get_overdue_days(self):
        """Get number of overdue days"""
        if self.return_date:
            if self.return_date > self.due_date:
                return (self.return_date - self.due_date).days
            return 0
        if datetime.utcnow() > self.due_date:
            return (datetime.utcnow() - self.due_date).days
        return 0

    def calculate_fine(self):
        """Calculate fine amount"""
        overdue_days = self.get_overdue_days()
        return overdue_days * self.FINE_PER_DAY

    @staticmethod
    def get_by_id(db, record_id):
        if isinstance(record_id, str):
            record_id = ObjectId(record_id)
        record_dict = db["borrow_records"].find_one({"_id": record_id})
        if record_dict:
            return BorrowRecord._dict_to_record(record_dict)
        return None

    @staticmethod
    def get_by_user_id(db, user_id):
        """Get all borrow records for a user"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        records = []
        for record_dict in db["borrow_records"].find({"user_id": user_id}):
            records.append(BorrowRecord._dict_to_record(record_dict))
        return records

    @staticmethod
    def get_by_book_id(db, book_id):
        """Get all borrow records for a book"""
        if isinstance(book_id, str):
            book_id = ObjectId(book_id)
        records = []
        for record_dict in db["borrow_records"].find({"book_id": book_id}):
            records.append(BorrowRecord._dict_to_record(record_dict))
        return records

    @staticmethod
    def get_active_borrows(db):
        """Get all active (not returned) borrow records"""
        records = []
        for record_dict in db["borrow_records"].find({"return_date": None}):
            records.append(BorrowRecord._dict_to_record(record_dict))
        return records

    @staticmethod
    def get_overdue_borrows(db):
        """Get all overdue borrow records"""
        overdue_date = datetime.utcnow()
        records = []
        for record_dict in db["borrow_records"].find(
            {"due_date": {"$lt": overdue_date}, "return_date": None}
        ):
            records.append(BorrowRecord._dict_to_record(record_dict))
        return records

    # BorrowRecords → Fines (1-1)
    @staticmethod
    def get_fine(db, record_id):
        if isinstance(record_id, str):
            record_id = ObjectId(record_id)
        return db["fines"].find_one({"record_id": record_id})

    @staticmethod
    def _dict_to_record(record_dict):
        """Convert dict to BorrowRecord object"""
        record = BorrowRecord(
            user_id=record_dict.get("user_id"),
            book_id=record_dict.get("book_id"),
            borrow_date=record_dict.get("borrow_date"),
            due_date=record_dict.get("due_date"),
            return_date=record_dict.get("return_date"),
            record_id=record_dict.get("_id"),
        )
        record.fine_id = record_dict.get("fine_id")
        return record

    @staticmethod
    def get_by_user_and_status(db, user_id, status="active"):
        """Get borrow records by user and status (active/returned/overdue)"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        
        records = []
        if status == "active":
            query = {"user_id": user_id, "return_date": None}
        elif status == "returned":
            query = {"user_id": user_id, "return_date": {"$ne": None}}
        elif status == "overdue":
            query = {
                "user_id": user_id,
                "due_date": {"$lt": datetime.utcnow()},
                "return_date": None,
            }
        else:
            return []
        
        for record_dict in db["borrow_records"].find(query):
            records.append(BorrowRecord._dict_to_record(record_dict))
        return records

    @staticmethod
    def get_late_returns(db, days=0):
        """Get borrow records returned after due date by specified days"""
        records = []
        threshold_date = datetime.utcnow() - timedelta(days=days)
        
        for record_dict in db["borrow_records"].find({
            "return_date": {"$exists": True, "$ne": None},
            "$expr": {"$gt": ["$return_date", "$due_date"]}
        }):
            record = BorrowRecord._dict_to_record(record_dict)
            if record.return_date and record.return_date > record.due_date:
                records.append(record)
        return records
