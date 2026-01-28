"""
Book Service Layer
Handles all business logic for book management
- Validation (duplicate ISBN/BookID)
- Availability updates
- Deletion constraints
- Search operations
"""

from ..models.book import Book
from ..models.database import get_db
from datetime import datetime


class BookService:
    """Service layer for book operations"""
    
    def __init__(self):
        self.db = get_db()
    
    def _get_next_book_id(self):
        """
        Get next sequential book_id (starts from 1)
        """
        try:
            # Find the highest book_id currently in database
            result = self.db["books"].find_one(
                {"is_active": True},
                sort=[("book_id", -1)]
            )
            
            if result and result.get("book_id"):
                # book_id is stored as integer, get next one
                current_max = int(result.get("book_id", 0))
                return current_max + 1
            else:
                # No books yet, start from 1
                return 1
        except Exception as e:
            print(f"Error getting next book_id: {e}")
            return 1
    
    def create_book(self, title, author, publisher, year, category, isbn, 
                    quantity, book_id=None):
        """
        Create new book with validation
        
        Args:
            title (str): Book title
            author (str): Author name
            publisher (str): Publisher
            year (int): Publication year
            category (str): Book category
            isbn (str): ISBN (must be unique)
            quantity (int): Total quantity
            book_id (str, optional): Custom BookID
        
        Returns:
            dict: {success: bool, message: str, book_id: str}
        """
        try:
            # Check for duplicate ISBN
            if Book.get_by_isbn(self.db, isbn):
                return {
                    "success": False,
                    "message": "ISBN already exists"
                }
            
            # Auto-generate sequential book_id starting from 1 if not provided
            if not book_id:
                book_id = self._get_next_book_id()
            else:
                # Check for duplicate BookID if manually provided
                if Book.get_by_book_id(self.db, book_id):
                    return {
                        "success": False,
                        "message": f"BookID {book_id} already exists"
                    }
            
            # Validate inputs
            if not all([title, author, publisher, category, isbn]):
                return {
                    "success": False,
                    "message": "Missing required fields"
                }
            
            if quantity < 1:
                return {
                    "success": False,
                    "message": "Quantity must be at least 1"
                }
            
            # Create book
            book = Book(
                title=title,
                author=author,
                publisher=publisher,
                year=int(year),
                category=category,
                isbn=isbn.strip(),
                quantity=int(quantity),
                available_quantity=int(quantity),
                status="Available" if quantity > 0 else "Unavailable",
                book_id=book_id
            )
            
            if book.save(self.db):
                return {
                    "success": True,
                    "message": "Book created successfully",
                    "book_id": str(book._id)
                }
            else:
                return {"success": False, "message": "Failed to create book"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def update_book(self, book_id, **kwargs):
        """
        Update book information
        
        Args:
            book_id (str): MongoDB ObjectId
            **kwargs: Fields to update
        
        Returns:
            dict: {success: bool, message: str}
        """
        try:
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}
            
            # Check for duplicate ISBN if being updated
            if 'isbn' in kwargs:
                new_isbn = kwargs['isbn'].strip()
                existing = Book.get_by_isbn(self.db, new_isbn)
                if existing and str(existing._id) != book_id:
                    return {"success": False, "message": "ISBN already exists"}
            
            # Update fields
            for key, value in kwargs.items():
                if key in ['title', 'author', 'publisher', 'year', 'category', 'isbn']:
                    setattr(book, key, value)
                elif key == 'quantity':
                    old_quantity = book.quantity
                    book.quantity = int(value)
                    # Adjust available quantity if total decreased
                    if book.quantity < old_quantity:
                        reduction = old_quantity - book.quantity
                        book.available_quantity = max(0, book.available_quantity - reduction)
            
            # Update status based on availability
            if book.available_quantity == 0:
                book.status = "Unavailable"
            else:
                book.status = "Available"
            
            if book.save(self.db):
                return {"success": True, "message": "Book updated successfully"}
            else:
                return {"success": False, "message": "Failed to update book"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def delete_book(self, book_id):
        """
        Delete book (soft delete)
        Cannot delete if book is currently borrowed
        
        Args:
            book_id (str): MongoDB ObjectId
        
        Returns:
            dict: {success: bool, message: str}
        """
        try:
            from bson import ObjectId
            
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}
            
            # Check if book is currently borrowed
            borrowed_count = self.db["borrow_records"].count_documents({
                "book_id": ObjectId(book_id),
                "return_date": None,
                "is_active": True
            })
            
            if borrowed_count > 0:
                return {
                    "success": False,
                    "message": f"Cannot delete. {borrowed_count} copy/copies are currently borrowed"
                }
            
            if book.delete(self.db):
                return {"success": True, "message": "Book deleted successfully"}
            else:
                return {"success": False, "message": "Failed to delete book"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_book(self, book_id):
        """Get single book by ID"""
        try:
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}
            
            return {
                "success": True,
                "book": self._book_to_dict(book)
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_all_books(self, only_available=False):
        """
        Get all books
        
        Args:
            only_available (bool): If True, return only books with available copies
        
        Returns:
            dict: {success: bool, books: list, count: int}
        """
        try:
            if only_available:
                books = Book.get_available_books(self.db)
            else:
                books = Book.get_all(self.db)
            
            books_data = [self._book_to_dict(book) for book in books]
            
            return {
                "success": True,
                "books": books_data,
                "count": len(books_data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "books": [],
                "count": 0
            }
    
    def search_books(self, query, search_by="title"):
        """
        Search books by title, author, category, or ISBN
        
        Args:
            query (str): Search query
            search_by (str): Search field (title/author/category/isbn)
        
        Returns:
            dict: {success: bool, books: list, count: int}
        """
        try:
            books = []
            
            if search_by == "title":
                books = Book.get_by_title(self.db, query)
            elif search_by == "author":
                books = Book.get_by_author(self.db, query)
            elif search_by == "category":
                books = Book.get_by_category(self.db, query)
            elif search_by == "isbn":
                book = Book.get_by_isbn(self.db, query)
                books = [book] if book else []
            else:
                books = Book.get_by_title(self.db, query)
            
            books_data = [self._book_to_dict(book) for book in books]
            
            return {
                "success": True,
                "books": books_data,
                "count": len(books_data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "books": [],
                "count": 0
            }
    
    def get_books_by_category(self, category):
        """Get all books in a category"""
        try:
            books = Book.get_by_category(self.db, category)
            books_data = [self._book_to_dict(book) for book in books]
            
            return {
                "success": True,
                "books": books_data,
                "count": len(books_data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "books": [],
                "count": 0
            }
    
    def update_available_quantity(self, book_id, quantity_change):
        """
        Update available quantity (used when borrowing/returning)
        
        Args:
            book_id (str): MongoDB ObjectId
            quantity_change (int): Change in quantity (negative for borrow, positive for return)
        
        Returns:
            dict: {success: bool, message: str}
        """
        try:
            from bson import ObjectId
            
            book = Book.get_by_id(self.db, book_id)
            if not book:
                return {"success": False, "message": "Book not found"}
            
            # Update available quantity
            new_available = book.available_quantity + quantity_change
            
            if new_available < 0:
                return {"success": False, "message": "Not enough available copies"}
            
            if new_available > book.quantity:
                return {"success": False, "message": "Cannot return more than quantity"}
            
            book.available_quantity = new_available
            
            # Update status
            if book.available_quantity == 0:
                book.status = "Unavailable"
            else:
                book.status = "Available"
            
            if book.save(self.db):
                return {
                    "success": True,
                    "message": "Quantity updated",
                    "available": book.available_quantity
                }
            else:
                return {"success": False, "message": "Failed to update"}
        
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _book_to_dict(self, book):
        """Convert Book object to dictionary"""
        return {
            "id": str(book._id),
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "year": book.year,
            "category": book.category,
            "isbn": book.isbn,
            "quantity": book.quantity,
            "available_quantity": book.available_quantity,
            "status": book.status
        }
    
    def get_categories(self):
        """Get all unique book categories from database"""
        try:
            categories = self.db["books"].distinct("category", {"is_active": True})
            # Sort categories alphabetically
            categories.sort()
            return {
                "success": True,
                "categories": categories,
                "count": len(categories)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting categories: {str(e)}",
                "categories": []
            }
    
    def get_category_report(self):
        """Get category report with book counts from database"""
        try:
            # Get all active books
            books = self.db["books"].find({"is_active": True})
            
            # Count books by category
            category_counts = {}
            category_colors = {}
            color_palette = ['#007bff', '#ff3366', '#2ecc71', '#d4a373', '#ffcc00', '#9b59b6', '#e74c3c', '#3498db']
            
            for i, book in enumerate(books):
                category = book.get('category', 'Uncategorized')
                category_counts[category] = category_counts.get(category, 0) + 1
                if category not in category_colors:
                    category_colors[category] = color_palette[len(category_colors) % len(color_palette)]
            
            # Sort by category name
            sorted_categories = sorted(category_counts.keys())
            
            labels = sorted_categories
            data = [category_counts[cat] for cat in sorted_categories]
            colors = [category_colors[cat] for cat in sorted_categories]
            
            return {
                "success": True,
                "labels": labels,
                "data": data,
                "colors": colors,
                "total_categories": len(labels),
                "total_books": sum(data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting category report: {str(e)}"
            }
