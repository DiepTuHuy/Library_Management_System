from ..models.book import Book
from ..models.borrow_record import BorrowRecord
from ..models.database import get_db
from ..services.book_service import BookService
from bson.objectid import ObjectId


class BookController:
    """Controller for book management operations with role-based access"""

    def __init__(self):
        self.db = get_db()
        self.book_service = BookService()

    def add_book(self, user_role, title, author, publisher, year, category, isbn, 
                 quantity, book_id=None):
        """
        Add a new book (Admin/Librarian only)
        
        Args:
            user_role (str): Current user's role
            title, author, publisher, year, category (str): Book details
            isbn (str): ISBN
            quantity (int): Total quantity
            book_id (str, optional): Custom BookID
        
        Returns:
            dict: {success: bool, message: str, book_id: str}
        """
        # Role check
        if user_role not in ["admin", "librarian"]:
            return {
                "success": False,
                "message": "Permission denied. Only Admin/Librarian can add books"
            }
        
        return self.book_service.create_book(
            title=title,
            author=author,
            publisher=publisher,
            year=year,
            category=category,
            isbn=isbn,
            quantity=quantity,
            book_id=book_id
        )

    def get_book(self, book_id):
        """Get book details (all users)"""
        return self.book_service.get_book(book_id)

    def get_all_books(self):
        """Get all books (all users)"""
        return self.book_service.get_all_books()

    def search_books(self, query, search_by="title"):
        """Search books by title, author, category, or ISBN (all users)"""
        return self.book_service.search_books(query, search_by)

    def get_available_books(self):
        """Get all available books (all users)"""
        return self.book_service.get_all_books(only_available=True)

    def update_book(self, user_role, book_id, **kwargs):
        """
        Update book information (Admin/Librarian only)
        
        Args:
            user_role (str): Current user's role
            book_id (str): MongoDB ObjectId
            **kwargs: Fields to update
        
        Returns:
            dict: {success: bool, message: str}
        """
        # Role check
        if user_role not in ["admin", "librarian"]:
            return {
                "success": False,
                "message": "Permission denied. Only Admin/Librarian can update books"
            }
        
        return self.book_service.update_book(book_id, **kwargs)

    def delete_book(self, user_role, book_id):
        """
        Delete book (Admin/Librarian only)
        Cannot delete if currently borrowed
        
        Args:
            user_role (str): Current user's role
            book_id (str): MongoDB ObjectId
        
        Returns:
            dict: {success: bool, message: str}
        """
        # Role check
        if user_role not in ["admin", "librarian"]:
            return {
                "success": False,
                "message": "Permission denied. Only Admin/Librarian can delete books"
            }
        
        return self.book_service.delete_book(book_id)

    def get_book_borrow_history(self, book_id):
        """Get all borrow records for a book (all users)"""
        try:
            records = Book.get_borrow_records(self.db, book_id)
            records_data = []
            for record in records:
                records_data.append({
                    "id": str(record.get("_id")),
                    "user_id": str(record.get("user_id")),
                    "borrow_date": record.get("borrow_date").isoformat() if record.get("borrow_date") else None,
                    "due_date": record.get("due_date").isoformat() if record.get("due_date") else None,
                    "return_date": record.get("return_date").isoformat() if record.get("return_date") else None,
                })
            return {
                "success": True,
                "records": records_data,
                "count": len(records_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "records": [], "count": 0}

    def update_available_quantity(self, book_id, quantity_change):
        """
        Update available quantity when borrowing/returning
        (Called by BorrowController)
        
        Args:
            book_id (str): MongoDB ObjectId
            quantity_change (int): Negative for borrow, positive for return
        
        Returns:
            dict: {success: bool, message: str, available: int}
        """
        return self.book_service.update_available_quantity(book_id, quantity_change)
    
    def get_dashboard_stats(self):
        """Get dashboard statistics (total users, total books, categories)"""
        from ..models.user import User
        
        try:
            # Get total books
            books_result = self.book_service.get_all_books()
            total_books = books_result['count'] if books_result['success'] else 0
            
            # Get total members (users with role 'member')
            members = User.get_all(self.db, role="member", include_inactive=True)
            total_members = len(members)
            
            # Get categories
            categories_result = self.book_service.get_categories()
            categories = categories_result.get('categories', []) if categories_result.get('success') else []
            
            return {
                "success": True,
                "total_books": total_books,
                "total_members": total_members,
                "categories": categories,
                "category_count": len(categories)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting dashboard stats: {str(e)}"
            }
    
    def get_category_report(self):
        """Get category report with book counts"""
        return self.book_service.get_category_report()
