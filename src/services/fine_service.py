"""
Fine Service
Centralized fine calculation and creation logic.
"""
from datetime import datetime
from ..models.fine import Fine


class FineService:
    """Service to handle fine calculation and creation"""

    DAILY_RATE = 1000  # default fine per day, keep in sync with BorrowService

    def __init__(self, db):
        self.db = db

    def calculate_fine_amount(self, days_overdue: int) -> int:
        if days_overdue <= 0:
            return 0
        return days_overdue * self.DAILY_RATE

    def create_fine_for_borrow(self, borrow_record: dict):
        """
        Create a fine for a borrow record if overdue and if a fine doesn't already exist.

        Returns: Fine object or None
        """
        try:
            # ensure borrow_record has _id and user_id
            record_id = borrow_record.get("_id")
            # Check existing fine
            existing = Fine.get_by_record_id(self.db, record_id)
            if existing:
                return existing

            due_date = borrow_record.get("due_date")
            return_date = borrow_record.get("return_date") or datetime.utcnow()
            # calculate overdue days
            days_overdue = (return_date - due_date).days if due_date and return_date else 0
            if days_overdue <= 0:
                return None

            amount = self.calculate_fine_amount(days_overdue)

            fine = Fine(record_id=record_id, amount=amount, status="pending")
            if fine.save(self.db):
                return fine
            return None
        except Exception:
            return None
