from models.book import Book
from models.borrow_record import BorrowRecord
from models.database import get_db
from bson.objectid import ObjectId


class BookController:
    """Controller for book management operations"""

    def __init__(self):
        self.db = get_db()

    def add_book(self, title, author, publisher, year, category, quantity=1):
        """Add a new book to the system"""
        try:
            book = Book(
                title=title,
                author=author,
                publisher=publisher,
                year=year,
                category=category,
                quantity=quantity,
                available=quantity,
            )
            if book.save(self.db):
                return {
                    "success": True,
                    "message": "Book added successfully",
                    "book_id": str(book._id),
                }
            else:
                return {"success": False, "message": "Failed to add book"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_book(self, book_id):
        """Get book details"""
        try:
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}

            return {
                "success": True,
                "book": {
                    "id": str(book._id),
                    "title": book.title,
                    "author": book.author,
                    "publisher": book.publisher,
                    "year": book.year,
                    "category": book.category,
                    "quantity": book.quantity,
                    "available": book.available,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_all_books(self):
        """Get all books"""
        try:
            books = Book.get_all(self.db)
            books_data = []
            for book in books:
                books_data.append({
                    "id": str(book._id),
                    "title": book.title,
                    "author": book.author,
                    "publisher": book.publisher,
                    "year": book.year,
                    "category": book.category,
                    "quantity": book.quantity,
                    "available": book.available,
                })
            return {
                "success": True,
                "books": books_data,
                "count": len(books_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "books": [], "count": 0}

    def search_books(self, query, search_type="title"):
        """Search books by title, author, or category"""
        try:
            if search_type == "title":
                books = Book.get_by_title(self.db, query)
            elif search_type == "author":
                books = Book.get_by_author(self.db, query)
            elif search_type == "category":
                books = Book.get_by_category(self.db, query)
            else:
                books = Book.get_by_title(self.db, query)

            books_data = []
            for book in books:
                books_data.append({
                    "id": str(book._id),
                    "title": book.title,
                    "author": book.author,
                    "publisher": book.publisher,
                    "year": book.year,
                    "category": book.category,
                    "quantity": book.quantity,
                    "available": book.available,
                })
            return {
                "success": True,
                "books": books_data,
                "count": len(books_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "books": [], "count": 0}

    def get_available_books(self):
        """Get all available books"""
        try:
            books = Book.get_available_books(self.db)
            books_data = []
            for book in books:
                books_data.append({
                    "id": str(book._id),
                    "title": book.title,
                    "author": book.author,
                    "publisher": book.publisher,
                    "year": book.year,
                    "category": book.category,
                    "quantity": book.quantity,
                    "available": book.available,
                })
            return {
                "success": True,
                "books": books_data,
                "count": len(books_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "books": [], "count": 0}

    def update_book(self, book_id, **kwargs):
        """Update book information"""
        try:
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}

            for key, value in kwargs.items():
                if hasattr(book, key) and key not in ["_id", "created_at"]:
                    setattr(book, key, value)

            if book.save(self.db):
                return {
                    "success": True,
                    "message": "Book updated successfully",
                }
            else:
                return {"success": False, "message": "Failed to update book"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_book(self, book_id):
        """Delete (soft delete) book"""
        try:
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}

            # FEATURE 3: Check if book is currently borrowed
            borrowed_copies = self.db["borrow_records"].count_documents({
                "book_id": ObjectId(book_id),
                "return_date": None,
            })
            
            if borrowed_copies > 0:
                return {
                    "success": False,
                    "message": f"Cannot delete book. {borrowed_copies} copy/copies are currently borrowed. Please wait until all copies are returned."
                }

            if book.delete(self.db):
                return {"success": True, "message": "Book deleted successfully"}
            else:
                return {"success": False, "message": "Failed to delete book"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_book_borrow_history(self, book_id):
        """Get all borrow records for a book"""
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
