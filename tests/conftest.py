import pytest
import sys
import os
import hashlib
from mongomock import MongoClient

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from models.user import User
from models.book import Book
from models.borrow_record import BorrowRecord
from models.fine import Fine


@pytest.fixture
def mock_db():
    """Create a mock MongoDB client for testing"""
    client = MongoClient()
    db = client.test_library_db
    
    # Create collections
    db.create_collection("users")
    db.create_collection("books")
    db.create_collection("borrow_records")
    db.create_collection("fines")
    db.create_collection("payments")
    
    yield db
    
    # Cleanup
    client.drop_database("test_library_db")


@pytest.fixture
def sample_user(mock_db):
    """Create a sample user for testing"""
    user = User(
        name="Test User",
        email="test@example.com",
        password="testpass123",
        role="member"
    )
    user.save(mock_db)
    return user


@pytest.fixture
def sample_admin(mock_db):
    """Create a sample admin for testing"""
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password="adminpass123",
        role="admin"
    )
    admin.save(mock_db)
    return admin


@pytest.fixture
def sample_librarian(mock_db):
    """Create a sample librarian for testing"""
    librarian = User(
        name="Librarian User",
        email="librarian@example.com",
        password="librarianpass123",
        role="librarian"
    )
    librarian.save(mock_db)
    return librarian


@pytest.fixture
def sample_book(mock_db):
    """Create a sample book for testing"""
    book = Book(
        title="Test Book",
        author="Test Author",
        publisher="Test Publisher",
        year=2023,
        category="Science",
        quantity=5,
        available=5
    )
    book.save(mock_db)
    return book


@pytest.fixture
def sample_books(mock_db):
    """Create multiple sample books for testing"""
    books_data = [
        ("Python Programming", "Guido van Rossum", "Python Press", 2020, "Technology", 3),
        ("Data Science 101", "John Doe", "Tech Books", 2021, "Science", 2),
        ("Web Development", "Jane Smith", "Web Press", 2022, "Technology", 4),
        ("History of AI", "AI Master", "AI Press", 2023, "Science", 1),
    ]
    
    books = []
    for title, author, publisher, year, category, quantity in books_data:
        book = Book(
            title=title,
            author=author,
            publisher=publisher,
            year=year,
            category=category,
            quantity=quantity,
            available=quantity
        )
        book.save(mock_db)
        books.append(book)
    
    return books


@pytest.fixture
def sample_borrow_record(mock_db, sample_user, sample_book):
    """Create a sample borrow record for testing"""
    borrow = BorrowRecord(
        user_id=str(sample_user._id),
        book_id=str(sample_book._id)
    )
    borrow.save(mock_db)
    return borrow


@pytest.fixture
def sample_fine(mock_db, sample_borrow_record):
    """Create a sample fine for testing"""
    fine = Fine(
        record_id=str(sample_borrow_record._id),
        amount=5.00
    )
    fine.save(mock_db)
    return fine


@pytest.fixture
def user_controller(mock_db):
    """Create a UserController instance with mock database"""
    from controllers.user_controller import UserController
    controller = UserController()
    controller.db = mock_db
    return controller


@pytest.fixture
def book_controller(mock_db):
    """Create a BookController instance with mock database"""
    from controllers.book_controller import BookController
    controller = BookController()
    controller.db = mock_db
    return controller


@pytest.fixture
def borrow_controller(mock_db):
    """Create a BorrowController instance with mock database"""
    from controllers.borrow_controller import BorrowController
    controller = BorrowController()
    controller.db = mock_db
    return controller


@pytest.fixture
def fine_controller(mock_db):
    """Create a FineController instance with mock database"""
    from controllers.fine_controller import FineController
    controller = FineController()
    controller.db = mock_db
    return controller


@pytest.fixture
def auth_controller(mock_db):
    """Create an AuthController instance with mock database"""
    from controllers.auth_controller import AuthController
    controller = AuthController()
    controller.set_db(mock_db)
    return controller
