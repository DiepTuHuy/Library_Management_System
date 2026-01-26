from bson import ObjectId
from datetime import datetime
from models.database import get_db


class Book:
    def __init__(
        self,
        title,
        author,
        publisher,
        year,
        category,
        quantity=1,
        available=1,
        book_id=None,
    ):
        self._id = book_id
        self.title = title
        self.author = author
        self.publisher = publisher
        self.year = year
        self.category = category
        self.quantity = quantity  # Total copies
        self.available = available  # Available copies
        self.created_at = datetime.utcnow()
        self.is_active = True

    def save(self, db):
        """Save or update book in database"""
        try:
            book_dict = {
                "title": self.title,
                "author": self.author,
                "publisher": self.publisher,
                "year": self.year,
                "category": self.category,
                "quantity": self.quantity,
                "available": self.available,
                "created_at": self.created_at,
                "is_active": self.is_active,
            }
            if self._id:
                db["books"].update_one({"_id": self._id}, {"$set": book_dict})
            else:
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
        if isinstance(book_id, str):
            book_id = ObjectId(book_id)
        book_dict = db["books"].find_one({"_id": book_id, "is_active": True})
        if book_dict:
            return Book._dict_to_book(book_dict)
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
        books = []
        for book_dict in db["books"].find(
            {"is_active": True, "available": {"$gt": 0}}
        ):
            books.append(Book._dict_to_book(book_dict))
        return books

    # Books → BorrowRecords (1-n)
    @staticmethod
    def get_borrow_records(db, book_id):
        if isinstance(book_id, str):
            book_id = ObjectId(book_id)
        return list(db["borrow_records"].find({"book_id": book_id}))

    @staticmethod
    def _dict_to_book(book_dict):
        """Convert dict to Book object"""
        book = Book(
            title=book_dict.get("title", ""),
            author=book_dict.get("author", ""),
            publisher=book_dict.get("publisher", ""),
            year=book_dict.get("year", 0),
            category=book_dict.get("category", ""),
            quantity=book_dict.get("quantity", 1),
            available=book_dict.get("available", 1),
            book_id=book_dict.get("_id"),
        )
        book.created_at = book_dict.get("created_at")
        book.is_active = book_dict.get("is_active", True)
        return book
