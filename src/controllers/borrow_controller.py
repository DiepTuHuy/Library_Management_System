from models.borrow_record import BorrowRecord
from models.book import Book
from models.database import get_db
from datetime import datetime
from bson.objectid import ObjectId


class BorrowController:
    """Controller for book borrowing operations"""

    def __init__(self):
        self.db = get_db()

    def borrow_book(self, user_id, book_id):
        """User borrows a book"""
        try:
            # Check if book exists and has available copies
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}

            if book.available <= 0:
                return {"success": False, "message": "No available copies"}

            # Check if user already has this book borrowed
            records = self.db["borrow_records"].find_one({
                "user_id": ObjectId(user_id),
                "book_id": ObjectId(book_id),
                "return_date": None,
            })
            if records:
                return {"success": False, "message": "You already have this book"}

            # FEATURE 1: Check borrow limit (max 3 books at a time)
            BORROW_LIMIT = 3
            active_borrows = self.db["borrow_records"].count_documents({
                "user_id": ObjectId(user_id),
                "return_date": None,
            })
            if active_borrows >= BORROW_LIMIT:
                return {
                    "success": False,
                    "message": f"You have reached the borrow limit ({BORROW_LIMIT} books). Please return a book before borrowing more."
                }

            # FEATURE 2: Check for outstanding fines
            from models.fine import Fine
            outstanding_fines = self.db["fines"].find_one({
                "record_id": {"$in": [
                    br["_id"] for br in self.db["borrow_records"].find({
                        "user_id": ObjectId(user_id),
                        "return_date": None,
                    })
                ]},
                "status": "pending"
            })
            
            # Simpler approach: check if user has any pending fines directly
            user_active_borrows = list(self.db["borrow_records"].find({
                "user_id": ObjectId(user_id),
                "return_date": None,
            }))
            
            if user_active_borrows:
                for borrow in user_active_borrows:
                    fine = self.db["fines"].find_one({
                        "record_id": borrow["_id"],
                        "status": "pending"
                    })
                    if fine:
                        return {
                            "success": False,
                            "message": "You have an outstanding fine. Please pay it before borrowing more books."
                        }

            # Create borrow record
            borrow = BorrowRecord(user_id=user_id, book_id=book_id)
            if not borrow.save(self.db):
                return {"success": False, "message": "Failed to create borrow record"}

            # Decrease available count
            book.available -= 1
            if not book.save(self.db):
                return {"success": False, "message": "Failed to update book availability"}

            return {
                "success": True,
                "message": "Book borrowed successfully",
                "borrow_id": str(borrow._id),
                "due_date": borrow.due_date.isoformat(),
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def return_book(self, borrow_id):
        """User returns a book"""
        try:
            borrow = BorrowRecord.get_by_id(self.db, borrow_id)
            if not borrow:
                return {"success": False, "message": "Borrow record not found"}

            if borrow.return_date:
                return {"success": False, "message": "Book already returned"}

            # Mark as returned
            borrow.return_date = datetime.utcnow()
            if not borrow.save(self.db):
                return {"success": False, "message": "Failed to return book"}

            # Increase available count
            book = Book.get_by_id(self.db, str(borrow.book_id))
            if book:
                book.available += 1
                book.save(self.db)

            # Check for overdue and create fine if necessary
            fine_amount = 0
            if borrow.is_overdue():
                fine_amount = borrow.calculate_fine()
                from models.fine import Fine

                fine = Fine(record_id=borrow._id, amount=fine_amount)
                fine.save(self.db)
                borrow.fine_id = fine._id
                borrow.save(self.db)

            return {
                "success": True,
                "message": "Book returned successfully",
                "overdue": borrow.is_overdue(),
                "fine_amount": fine_amount,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_borrow_record(self, borrow_id):
        """Get borrow record details"""
        try:
            borrow = BorrowRecord.get_by_id(self.db, borrow_id)
            if not borrow:
                return {"success": False, "message": "Borrow record not found"}

            return {
                "success": True,
                "record": {
                    "id": str(borrow._id),
                    "user_id": str(borrow.user_id),
                    "book_id": str(borrow.book_id),
                    "borrow_date": borrow.borrow_date.isoformat(),
                    "due_date": borrow.due_date.isoformat(),
                    "return_date": borrow.return_date.isoformat() if borrow.return_date else None,
                    "is_overdue": borrow.is_overdue(),
                    "overdue_days": borrow.get_overdue_days(),
                    "fine_amount": borrow.calculate_fine(),
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user_active_borrows(self, user_id):
        """Get all active borrow records for a user"""
        try:
            borrows = BorrowRecord.get_by_user_id(self.db, user_id)
            active_borrows = [b for b in borrows if not b.return_date]

            borrows_data = []
            for borrow in active_borrows:
                borrows_data.append({
                    "id": str(borrow._id),
                    "book_id": str(borrow.book_id),
                    "borrow_date": borrow.borrow_date.isoformat(),
                    "due_date": borrow.due_date.isoformat(),
                    "is_overdue": borrow.is_overdue(),
                    "overdue_days": borrow.get_overdue_days(),
                    "fine_amount": borrow.calculate_fine(),
                })

            return {
                "success": True,
                "records": borrows_data,
                "count": len(borrows_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "records": [], "count": 0}

    def get_overdue_borrows(self):
        """Get all overdue borrow records"""
        try:
            borrows = BorrowRecord.get_overdue_borrows(self.db)
            borrows_data = []
            for borrow in borrows:
                borrows_data.append({
                    "id": str(borrow._id),
                    "user_id": str(borrow.user_id),
                    "book_id": str(borrow.book_id),
                    "borrow_date": borrow.borrow_date.isoformat(),
                    "due_date": borrow.due_date.isoformat(),
                    "overdue_days": borrow.get_overdue_days(),
                    "fine_amount": borrow.calculate_fine(),
                })

            return {
                "success": True,
                "records": borrows_data,
                "count": len(borrows_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "records": [], "count": 0}

    def get_all_active_borrows(self):
        """Get all active borrow records in the system"""
        try:
            borrows = BorrowRecord.get_active_borrows(self.db)
            borrows_data = []
            for borrow in borrows:
                borrows_data.append({
                    "id": str(borrow._id),
                    "user_id": str(borrow.user_id),
                    "book_id": str(borrow.book_id),
                    "borrow_date": borrow.borrow_date.isoformat(),
                    "due_date": borrow.due_date.isoformat(),
                    "is_overdue": borrow.is_overdue(),
                    "overdue_days": borrow.get_overdue_days(),
                })

            return {
                "success": True,
                "records": borrows_data,
                "count": len(borrows_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "records": [], "count": 0}
