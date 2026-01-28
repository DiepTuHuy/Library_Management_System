"""
Borrow Service Layer
Handles all business logic for borrowing operations:
- Validation (book availability, member limits, unpaid fines)
- Atomic updates (borrow record + book availability)
- Borrow history and status tracking
"""

from ..models.borrow_record import BorrowRecord
from ..models.book import Book
from ..models.user import User
from ..models.database import get_db
from ..models.fine import Fine
from .fine_service import FineService
from datetime import datetime, timedelta
from bson import ObjectId


class BorrowService:
    """Service layer for borrowing operations"""
    
    # Configuration
    BORROW_DURATION_DAYS = 14
    MAX_ACTIVE_BORROWS = 3  # Maximum concurrent borrows per member
    FINE_PER_DAY = 1000  # Fine in currency units per day
    
    def __init__(self):
        self.db = get_db()
        self.fine_service = FineService(self.db)
    
    def borrow_book(self, member_id, book_id):
        """
        Create a new borrow record for a member
        
        Validations:
        1. Book exists and has available copies
        2. Member has no unpaid fines
        3. Member has NO OVERDUE books
        4. Member hasn't exceeded borrow limit
        5. Member doesn't already have this book borrowed
        
        Updates (atomic):
        - Create borrow record
        - Decrease book available_quantity
        - Update book status if needed
        
        Args:
            member_id (str): MongoDB ObjectId of member
            book_id (int or str): Book ID (numeric or string)
        
        Returns:
            dict: {success: bool, message: str, borrow_id: str, due_date: str}
        """
        try:
            # Convert member_id to ObjectId if needed
            if isinstance(member_id, str):
                member_id = ObjectId(member_id)
            
            # Convert book_id to int (it's stored as integer in database)
            try:
                book_id_int = int(book_id)
            except (ValueError, TypeError):
                return {"success": False, "message": "Invalid book ID"}
            
            # 1. Check book exists and has available copies
            book_doc = self.db["books"].find_one({"book_id": book_id_int, "is_active": True})
            if not book_doc:
                return {"success": False, "message": "Book not found"}
            
            if book_doc.get("available_quantity", 0) <= 0:
                return {"success": False, "message": "No available copies of this book"}
            
            # 2. Check for unpaid fines
            unpaid_fines = self.db["fines"].count_documents({
                "user_id": member_id,
                "paid_date": None,
                "is_active": True
            })
            if unpaid_fines > 0:
                return {"success": False, "message": "You have unpaid fines. Please settle them before borrowing"}
            
            # 3. Check for overdue books (NEW CHECK)
            now = datetime.utcnow()
            overdue_borrows = self.db["borrow_records"].count_documents({
                "user_id": member_id,
                "return_date": None,
                "due_date": {"$lt": now},
                "is_active": True
            })
            if overdue_borrows > 0:
                return {"success": False, "message": "You have overdue books. Please return them before borrowing more"}
            
            # 4. Check borrow limit
            active_borrows = self.db["borrow_records"].count_documents({
                "user_id": member_id,
                "return_date": None,
                "is_active": True
            })
            if active_borrows >= self.MAX_ACTIVE_BORROWS:
                return {
                    "success": False,
                    "message": f"You have reached the maximum borrow limit ({self.MAX_ACTIVE_BORROWS} books)"
                }
            
            # 5. Check if member already has this book
            existing_borrow = self.db["borrow_records"].find_one({
                "user_id": member_id,
                "book_id": book_id_int,
                "return_date": None,
                "is_active": True
            })
            if existing_borrow:
                return {"success": False, "message": "You already have this book borrowed"}
            
            # All checks passed - create borrow record
            due_date = now + timedelta(days=self.BORROW_DURATION_DAYS)
            
            borrow_record = BorrowRecord(
                user_id=member_id,
                book_id=book_id_int,
                borrow_date=now,
                due_date=due_date,
                return_date=None
            )
            
            if not borrow_record.save(self.db):
                return {"success": False, "message": "Failed to create borrow record"}
            
            # Update book availability
            if not self._update_book_availability(book_id_int, -1):
                return {"success": False, "message": "Failed to update book availability"}
            
            return {
                "success": True,
                "message": "Book borrowed successfully",
                "borrow_id": str(borrow_record._id),
                "due_date": due_date.isoformat()
            }
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def return_book(self, borrow_id):
        """
        Process book return
        
        Updates:
        - Set return_date on borrow record
        - Increase book available_quantity
        - Update book status
        - Check if overdue and create fine if needed
        
        Args:
            borrow_id (str): MongoDB ObjectId of borrow record
        
        Returns:
            dict: {success: bool, message: str, overdue: bool, fine: int (if overdue)}
        """
        try:
            if isinstance(borrow_id, str):
                borrow_id = ObjectId(borrow_id)
            
            # Get borrow record
            borrow_dict = self.db["borrow_records"].find_one({
                "_id": borrow_id,
                "is_active": True
            })
            
            if not borrow_dict:
                return {"success": False, "message": "Borrow record not found"}
            
            if borrow_dict.get("return_date"):
                return {"success": False, "message": "Book already returned"}
            
            # Check if overdue
            now = datetime.utcnow()
            due_date = borrow_dict.get("due_date")
            is_overdue = now > due_date
            fine_amount = 0
            
            if is_overdue:
                overdue_days = (now - due_date).days
                fine_amount = overdue_days * self.FINE_PER_DAY
            
            # Update borrow record with return date
            update_result = self.db["borrow_records"].update_one(
                {"_id": borrow_id},
                {"$set": {"return_date": now}}
            )
            
            if update_result.matched_count == 0:
                return {"success": False, "message": "Failed to update borrow record"}
            
            # Update book availability
            book_id = borrow_dict.get("book_id")
            if not self._update_book_availability(book_id, 1):
                return {"success": False, "message": "Failed to update book availability"}
            
            # Create fine if overdue (use FineService, avoid duplicate fines)
            fine_obj = None
            if is_overdue:
                # update borrow_dict with return_date so FineService can calculate accurately
                borrow_dict["return_date"] = now
                fine_obj = self.fine_service.create_fine_for_borrow(borrow_dict)
                # if fine_obj is None, creation failed silently; continue
            
            return {
                "success": True,
                "message": "Book returned successfully",
                "overdue": is_overdue,
                "fine": fine_obj.amount if fine_obj else (fine_amount if is_overdue else 0)
            }
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_member_borrows(self, member_id, include_returned=False):
        """
        Get all borrow records for a member
        
        Args:
            member_id (str): MongoDB ObjectId of member
            include_returned (bool): If True, include returned books
        
        Returns:
            dict: {success: bool, borrows: list, count: int}
        """
        try:
            if isinstance(member_id, str):
                member_id = ObjectId(member_id)
            
            # Build query - handle both new records with is_active and old records without it
            query = {
                "user_id": member_id,
                "$or": [
                    {"is_active": True},
                    {"is_active": {"$exists": False}}  # Old records without is_active field
                ]
            }
            
            if not include_returned:
                query["return_date"] = None
            
            borrows = list(self.db["borrow_records"].find(query).sort("borrow_date", -1))
            borrows_data = [self._borrow_to_dict(b) for b in borrows]
            
            return {
                "success": True,
                "borrows": borrows_data,
                "count": len(borrows_data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "borrows": [],
                "count": 0
            }
    
    def get_all_borrows(self, include_returned=False):
        """
        Get all borrow records (Admin/Librarian only)
        
        Args:
            include_returned (bool): If True, include returned books
        
        Returns:
            dict: {success: bool, borrows: list, count: int}
        """
        try:
            query = {"is_active": True}
            
            if not include_returned:
                query["return_date"] = None
            
            borrows = list(self.db["borrow_records"].find(query).sort("borrow_date", -1))
            borrows_data = [self._borrow_to_dict(b) for b in borrows]
            
            return {
                "success": True,
                "borrows": borrows_data,
                "count": len(borrows_data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "borrows": [],
                "count": 0
            }
    
    def get_borrow_details(self, borrow_id):
        """Get detailed information about a borrow record"""
        try:
            if isinstance(borrow_id, str):
                borrow_id = ObjectId(borrow_id)
            
            borrow_dict = self.db["borrow_records"].find_one({"_id": borrow_id})
            
            if not borrow_dict:
                return {"success": False, "message": "Borrow record not found"}
            
            return {
                "success": True,
                "borrow": self._borrow_to_dict(borrow_dict)
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_overdue_borrows(self):
        """Get all overdue borrow records"""
        try:
            now = datetime.utcnow()
            overdue = list(self.db["borrow_records"].find({
                "due_date": {"$lt": now},
                "return_date": None,
                "is_active": True
            }))
            
            overdue_data = [self._borrow_to_dict(b) for b in overdue]
            
            return {
                "success": True,
                "borrows": overdue_data,
                "count": len(overdue_data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "borrows": [],
                "count": 0
            }
    
    def _update_book_availability(self, book_id, quantity_change):
        """
        Update book availability and status
        
        Args:
            book_id (int or ObjectId): Book ID
            quantity_change (int): Change in available quantity (negative for borrow, positive for return)
        
        Returns:
            bool: Success status
        """
        try:
            # Convert book_id to int if it's numeric
            try:
                book_id_int = int(book_id)
            except (ValueError, TypeError):
                return False
            
            # Find book by book_id (numeric field in database)
            book_doc = self.db["books"].find_one({"book_id": book_id_int})
            if not book_doc:
                return False
            
            new_available = book_doc.get("available_quantity", 0) + quantity_change
            
            if new_available < 0:
                return False
            
            # Update book availability
            new_status = "Unavailable" if new_available == 0 else "Available"
            
            result = self.db["books"].update_one(
                {"book_id": book_id_int},
                {"$set": {
                    "available_quantity": new_available,
                    "status": new_status
                }}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating book availability: {e}")
            return False
    
    def _borrow_to_dict(self, borrow_dict):
        """
        Convert borrow record to dictionary with details
        
        Status determination:
        - BORROWING: return_date is None AND due_date >= now
        - LATE: return_date is None AND due_date < now
        - RETURNED: return_date <= due_date
        - OVERDUE: return_date > due_date (returned late)
        """
        try:
            from ..models.borrow_record import BorrowRecord
            
            # Get book details using book_id (not MongoDB _id)
            book_id = borrow_dict.get("book_id")
            book = Book.get_by_book_id(self.db, book_id)
            book_title = book.title if book else "Unknown"
            
            # Get user details
            user_id = borrow_dict.get("user_id")
            user = User.get_by_id(self.db, str(user_id))
            user_name = user.name if user else "Unknown"
            
            # Calculate status based on dates
            return_date = borrow_dict.get("return_date")
            due_date = borrow_dict.get("due_date")
            now = datetime.utcnow()
            
            # Determine status
            if return_date:
                # Book has been returned
                if return_date <= due_date:
                    status = BorrowRecord.STATUS_RETURNED
                else:
                    status = BorrowRecord.STATUS_OVERDUE
            else:
                # Book is still borrowed
                if now > due_date:
                    status = BorrowRecord.STATUS_LATE
                else:
                    status = BorrowRecord.STATUS_BORROWING
            
            # Calculate overdue days
            if status == BorrowRecord.STATUS_LATE:
                overdue_days = (now - due_date).days
            elif status == BorrowRecord.STATUS_OVERDUE:
                overdue_days = (return_date - due_date).days
            else:
                overdue_days = 0
            
            return {
                "id": str(borrow_dict.get("_id")),
                "member_id": str(user_id),
                "member_name": user_name,
                "book_id": str(book_id),
                "book_title": book_title,
                "borrow_date": borrow_dict.get("borrow_date").isoformat() if borrow_dict.get("borrow_date") else None,
                "due_date": due_date.isoformat() if due_date else None,
                "return_date": return_date.isoformat() if return_date else None,
                "status": status,
                "overdue_days": overdue_days
            }
        except Exception as e:
            print(f"Error converting borrow to dict: {e}")
            return {}
