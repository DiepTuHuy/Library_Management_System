from ..models.borrow_record import BorrowRecord
from ..models.book import Book
from ..models.database import get_db
from ..services.borrow_service import BorrowService
from datetime import datetime
from bson.objectid import ObjectId


class BorrowController:
    """Controller for book borrowing operations with role-based access"""

    def __init__(self):
        self.db = get_db()
        self.borrow_service = BorrowService()

    def borrow_book(self, user_role, member_id, book_id):
        """
        Member borrows a book
        
        Args:
            user_role (str): Current user's role
            member_id (str): MongoDB ObjectId of member
            book_id (str): MongoDB ObjectId of book
        
        Returns:
            dict: {success: bool, message: str, borrow_id: str, due_date: str}
        """
        # Only members can borrow
        if user_role not in ["member"]:
            return {
                "success": False,
                "message": "Only members can borrow books"
            }
        
        return self.borrow_service.borrow_book(member_id, book_id)

    def return_book(self, user_role, borrow_id):
        """
        Process book return (Librarian/Admin can process for anyone)
        
        Args:
            user_role (str): Current user's role
            borrow_id (str): MongoDB ObjectId of borrow record
        
        Returns:
            dict: {success: bool, message: str, overdue: bool, fine: int}
        """
        # Only librarian and admin can process returns
        if user_role not in ["librarian", "admin"]:
            return {
                "success": False,
                "message": "Only librarians and admins can process returns"
            }
        
        return self.borrow_service.return_book(borrow_id)

    def get_member_borrows(self, member_id, include_returned=False):
        """
        Get all borrow records for a member (member can only see their own)
        
        Args:
            member_id (str): MongoDB ObjectId of member
            include_returned (bool): Include returned books
        
        Returns:
            dict: {success: bool, borrows: list, count: int}
        """
        return self.borrow_service.get_member_borrows(member_id, include_returned)

    def get_all_borrows(self, user_role, include_returned=False):
        """
        Get all borrow records (Librarian/Admin only)
        
        Args:
            user_role (str): Current user's role
            include_returned (bool): Include returned books
        
        Returns:
            dict: {success: bool, borrows: list, count: int}
        """
        # Only librarian and admin can view all borrows
        if user_role not in ["librarian", "admin"]:
            return {
                "success": False,
                "message": "Permission denied. Only librarians and admins can view all borrows"
            }
        
        return self.borrow_service.get_all_borrows(include_returned)

    def get_overdue_borrows(self, user_role):
        """
        Get all overdue borrow records (Librarian/Admin only)
        
        Args:
            user_role (str): Current user's role
        
        Returns:
            dict: {success: bool, borrows: list, count: int}
        """
        # Only librarian and admin can view overdue
        if user_role not in ["librarian", "admin"]:
            return {
                "success": False,
                "message": "Permission denied. Only librarians and admins can view overdue borrows"
            }
        
        return self.borrow_service.get_overdue_borrows()

    def get_borrow_details(self, borrow_id):
        """Get detailed information about a borrow record"""
        return self.borrow_service.get_borrow_details(borrow_id)

