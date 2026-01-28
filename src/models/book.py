from bson import ObjectId
from datetime import datetime
from .database import get_db


class Book:
    """
    Book Model
    Represents a book in the library system
    """
    def __init__(
        self,
        title,
        author,
        publisher,
        year,
        category,
        isbn,
        quantity=1,
        available_quantity=None,
        status="Available",
        book_id=None,
    ):
        self._id = None  # MongoDB ObjectId will be assigned on insert
        # Handle book_id as integer or string
        if book_id:
            try:
                self.book_id = int(book_id)
            except (ValueError, TypeError):
                self.book_id = book_id  # Keep as string if not convertible to int
        else:
            self.book_id = None
        self.title = title
        self.author = author
        self.publisher = publisher
        self.year = year
        self.category = category
        self.isbn = isbn  # ISBN - unique constraint
        self.quantity = quantity  # Total copies
        self.available_quantity = available_quantity if available_quantity is not None else quantity
        self.status = status  # "Available" or "Unavailable"
        self.created_at = datetime.utcnow()
        self.is_active = True

    def save(self, db):
        """Save or update book in database"""
        try:
            book_dict = {
                "book_id": self.book_id,
                "title": self.title,
                "author": self.author,
                "publisher": self.publisher,
                "year": self.year,
                "category": self.category,
                "isbn": self.isbn,
                "quantity": self.quantity,
                "available_quantity": self.available_quantity,
                "status": self.status,
                "created_at": self.created_at,
                "is_active": self.is_active,
            }
            
            if self._id:
                # Update existing book
                db["books"].update_one({"_id": self._id}, {"$set": book_dict})
            else:
                # Insert new book
                result = db["books"].insert_one(book_dict)
                self._id = result.inserted_id
            
            return True
        except Exception as e:
            print(f"Error saving book: {e}")
            return False

    def delete(self, db):
        """Soft delete book"""
        try:
            self.is_active = False
            return self.save(db)
        except Exception as e:
            print(f"Error deleting book: {e}")
            return False

    @staticmethod
    def get_by_id(db, book_id):
        """Get book by MongoDB ObjectId"""
        try:
            if isinstance(book_id, str):
                book_id = ObjectId(book_id)
            book_dict = db["books"].find_one({"_id": book_id, "is_active": True})
            if book_dict:
                return Book._dict_to_book(book_dict)
            return None
        except Exception as e:
            print(f"Error getting book by id: {e}")
            return None

    @staticmethod
    def get_by_book_id(db, book_id):
        """Get book by custom BookID"""
        try:
            book_dict = db["books"].find_one({"book_id": book_id, "is_active": True})
            if book_dict:
                return Book._dict_to_book(book_dict)
            return None
        except Exception as e:
            print(f"Error getting book by book_id: {e}")
            return None

    @staticmethod
    def get_by_isbn(db, isbn):
        """Get book by ISBN"""
        try:
            book_dict = db["books"].find_one({"isbn": isbn.strip(), "is_active": True})
            if book_dict:
                return Book._dict_to_book(book_dict)
            return None
        except Exception as e:
            print(f"Error getting book by isbn: {e}")
            return None

    @staticmethod
    def get_by_title(db, title):
        """Search books by title"""
        books = []
        for book_dict in db["books"].find(
            {"title": {"$regex": title, "$options": "i"}, "is_active": True}
        ):
            books.append(Book._dict_to_book(book_dict))
        return books

    @staticmethod
    def get_by_author(db, author):
        """Search books by author"""
        books = []
        for book_dict in db["books"].find(
            {"author": {"$regex": author, "$options": "i"}, "is_active": True}
        ):
            books.append(Book._dict_to_book(book_dict))
        return books

    @staticmethod
    def get_by_category(db, category):
        """Get books by category"""
        books = []
        for book_dict in db["books"].find(
            {"category": category, "is_active": True}
        ):
            books.append(Book._dict_to_book(book_dict))
        return books

    @staticmethod
    def get_all(db):
        """Get all active books"""
        books = []
        for book_dict in db["books"].find({"is_active": True}):
            books.append(Book._dict_to_book(book_dict))
        return books

    @staticmethod
    def get_available_books(db):
        """Get all books with available copies"""
        try:
            books = []
            for book_dict in db["books"].find(
                {"is_active": True, "available_quantity": {"$gt": 0}}
            ):
                books.append(Book._dict_to_book(book_dict))
            return books
        except Exception as e:
            print(f"Error getting available books: {e}")
            return []

    # Books → BorrowRecords (1-n)
    @staticmethod
    def get_borrow_records(db, book_id):
        if isinstance(book_id, str):
            book_id = ObjectId(book_id)
        return list(db["borrow_records"].find({"book_id": book_id}))

    @staticmethod
    def _dict_to_book(book_dict):
        """Convert dict from database to Book object"""
        try:
            book = Book(
                title=book_dict.get("title", ""),
                author=book_dict.get("author", ""),
                publisher=book_dict.get("publisher", ""),
                year=book_dict.get("year", 0),
                category=book_dict.get("category", ""),
                isbn=book_dict.get("isbn", ""),
                quantity=book_dict.get("quantity", 1),
                available_quantity=book_dict.get("available_quantity", 1),
                status=book_dict.get("status", "Available"),
                book_id=book_dict.get("book_id"),
            )
            book._id = book_dict.get("_id")
            book.created_at = book_dict.get("created_at")
            book.is_active = book_dict.get("is_active", True)
            return book
        except Exception as e:
            print(f"Error converting dict to book: {e}")
            return None
