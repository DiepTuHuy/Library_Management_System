"""
Unit tests for Book Controller and Book Model
Tests book management, addition, retrieval, and catalog operations
"""

import pytest
from controllers.book_controller import BookController
from models.book import Book
from bson import ObjectId


class TestBookAddition:
    """Test book addition to system"""
    
    def test_add_book_success(self, book_controller):
        """Test successfully adding a book"""
        result = book_controller.add_book(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            year=2023,
            category="Technology",
            quantity=5
        )
        
        assert result["success"] is True
        assert "book_id" in result
        assert result["message"] == "Book added successfully"
    
    def test_add_book_with_zero_quantity(self, book_controller):
        """Test adding book with zero quantity"""
        result = book_controller.add_book(
            title="Zero Qty Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Fiction",
            quantity=0
        )
        
        # Should succeed but with 0 available copies
        assert result["success"] is True
    
    def test_add_book_default_quantity(self, book_controller):
        """Test adding book without specifying quantity"""
        result = book_controller.add_book(
            title="Default Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science"
        )
        
        assert result["success"] is True
    
    def test_add_multiple_books(self, book_controller):
        """Test adding multiple books"""
        for i in range(3):
            result = book_controller.add_book(
                title=f"Book {i}",
                author=f"Author {i}",
                publisher="Publisher",
                year=2023,
                category="Science",
                quantity=2
            )
            assert result["success"] is True


class TestBookRetrieval:
    """Test book retrieval functionality"""
    
    def test_get_book_by_id(self, book_controller, sample_book):
        """Test retrieving book by ID"""
        result = book_controller.get_book(str(sample_book._id))
        
        assert result["success"] is True
        assert result["book"]["title"] == sample_book.title
        assert result["book"]["author"] == sample_book.author
    
    def test_get_nonexistent_book(self, book_controller):
        """Test retrieving non-existent book"""
        fake_id = ObjectId()
        result = book_controller.get_book(str(fake_id))
        
        assert result["success"] is False
        assert "not found" in result["message"]
    
    def test_search_books_by_title(self, book_controller, sample_books):
        """Test searching books by title"""
        result = book_controller.search_books("Python")
        
        assert result["success"] is True
        assert len(result.get("books", [])) > 0
    
    def test_search_books_no_result(self, book_controller, sample_books):
        """Test searching with no matching results"""
        result = book_controller.search_books("NonexistentBook")
        
        assert result["success"] is True
        assert len(result.get("books", [])) == 0


class TestBookUpdate:
    """Test book update functionality"""
    
    def test_update_book_quantity(self, book_controller, sample_book):
        """Test updating book quantity"""
        result = book_controller.update_book(
            str(sample_book._id),
            title=sample_book.title,
            author=sample_book.author,
            publisher=sample_book.publisher,
            year=sample_book.year,
            category=sample_book.category,
            quantity=10
        )
        
        assert result["success"] is True
    
    def test_update_book_details(self, book_controller, sample_book):
        """Test updating book details"""
        result = book_controller.update_book(
            str(sample_book._id),
            title="Updated Title",
            author="Updated Author",
            publisher=sample_book.publisher,
            year=sample_book.year,
            category=sample_book.category,
            quantity=sample_book.quantity
        )
        
        assert result["success"] is True


class TestBookModel:
    """Test Book model functionality"""
    
    def test_book_creation(self):
        """Test creating a book object"""
        book = Book(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            year=2023,
            category="Science",
            quantity=5,
            available=5
        )
        
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.quantity == 5
        assert book.available == 5
    
    def test_book_save_and_retrieve(self, mock_db):
        """Test saving and retrieving book from database"""
        book = Book(
            title="Saved Book",
            author="Saved Author",
            publisher="Publisher",
            year=2023,
            category="Science",
            quantity=3,
            available=3
        )
        
        book.save(mock_db)
        assert book._id is not None
        
        retrieved_book = Book.get_by_id(mock_db, str(book._id))
        assert retrieved_book is not None
        assert retrieved_book.title == "Saved Book"
    
    def test_book_soft_delete(self, mock_db):
        """Test soft delete of book"""
        book = Book(
            title="Delete Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science",
            quantity=1,
            available=1
        )
        
        book.save(mock_db)
        book.delete(mock_db)
        
        assert book.is_active is False
        
        # Deleted book should not be found
        retrieved_book = Book.get_by_id(mock_db, str(book._id))
        assert retrieved_book is None
    
    def test_book_search_by_title(self, mock_db, sample_books):
        """Test searching books by title"""
        books = Book.get_by_title(mock_db, "Python")
        
        assert len(books) > 0
        assert any("Python" in book.title for book in books)


class TestBookAvailability:
    """Test book availability management"""
    
    def test_book_available_count(self, sample_book):
        """Test book available count"""
        assert sample_book.available == sample_book.quantity
    
    def test_decrease_available_count(self, mock_db, sample_book):
        """Test decreasing available book count"""
        initial_available = sample_book.available
        sample_book.available -= 1
        sample_book.save(mock_db)
        
        retrieved = Book.get_by_id(mock_db, str(sample_book._id))
        assert retrieved.available == initial_available - 1 # type: ignore
    
    def test_increase_available_count(self, mock_db, sample_book):
        """Test increasing available book count"""
        sample_book.available += 1
        sample_book.save(mock_db)
        
        retrieved = Book.get_by_id(mock_db, str(sample_book._id))
        assert retrieved.available == sample_book.quantity + 1 # type: ignore


class TestBookCategories:
    """Test book category functionality"""
    
    def test_science_category(self, book_controller):
        """Test adding science category book"""
        result = book_controller.add_book(
            title="Science Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science",
            quantity=2
        )
        
        assert result["success"] is True
    
    def test_technology_category(self, book_controller):
        """Test adding technology category book"""
        result = book_controller.add_book(
            title="Tech Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Technology",
            quantity=2
        )
        
        assert result["success"] is True
    
    def test_fiction_category(self, book_controller):
        """Test adding fiction category book"""
        result = book_controller.add_book(
            title="Fiction Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Fiction",
            quantity=2
        )
        
        assert result["success"] is True
