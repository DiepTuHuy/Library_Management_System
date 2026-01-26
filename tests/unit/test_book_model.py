"""
Comprehensive Test Suite for Book Model
Tests all Book model functionalities
"""

import pytest
from bson.objectid import ObjectId
from models.book import Book


class TestBookModelCreation:
    """Test Book model creation and initialization"""
    
    def test_create_book_basic(self):
        """Test creating a basic book"""
        book = Book(
            title="Python Programming",
            author="Guido van Rossum",
            publisher="Tech Books",
            year=2023,
            category="Programming"
        )
        
        assert book.title == "Python Programming"
        assert book.author == "Guido van Rossum"
        assert book.publisher == "Tech Books"
        assert book.year == 2023
        assert book.category == "Programming"
        assert book.quantity == 1
        assert book.available == 1
    
    def test_create_book_with_quantity(self):
        """Test creating book with quantity"""
        book = Book(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            year=2023,
            category="Fiction",
            quantity=5,
            available=3
        )
        
        assert book.quantity == 5
        assert book.available == 3
    
    def test_book_is_active_default(self):
        """Test book is active by default"""
        book = Book(
            title="Test Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science"
        )
        
        assert book.is_active is True


class TestBookModelPersistence:
    """Test Book model save and delete operations"""
    
    def test_save_book_to_database(self, mock_db):
        """Test saving book to database"""
        book = Book(
            title="Test Book",
            author="Test Author",
            publisher="Test Publisher",
            year=2023,
            category="Science"
        )
        
        result = book.save(mock_db)
        
        assert result is True
        assert book._id is not None
    
    def test_update_book_in_database(self, mock_db):
        """Test updating existing book"""
        book = Book(
            title="Original Title",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science"
        )
        book.save(mock_db)
        
        book.title = "Updated Title"
        result = book.save(mock_db)
        
        assert result is True
        
        updated_book = Book.get_by_id(mock_db, str(book._id))
        assert updated_book.title == "Updated Title" # type: ignore
    
    def test_delete_book_soft_delete(self, mock_db):
        """Test soft delete book"""
        book = Book(
            title="Test Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science"
        )
        book.save(mock_db)
        
        result = book.delete(mock_db)
        
        assert result is True
        assert book.is_active is False


class TestBookModelRetrieval:
    """Test Book model retrieval operations"""
    
    def test_get_book_by_id(self, mock_db, sample_book):
        """Test retrieving book by ID"""
        retrieved_book = Book.get_by_id(mock_db, str(sample_book._id))
        
        assert retrieved_book is not None
        assert retrieved_book.title == sample_book.title
    
    def test_get_nonexistent_book(self, mock_db):
        """Test retrieving non-existent book"""
        fake_id = ObjectId()
        retrieved_book = Book.get_by_id(mock_db, str(fake_id))
        
        assert retrieved_book is None
    
    def test_get_all_books(self, mock_db, sample_books):
        """Test retrieving all books"""
        books = Book.get_all(mock_db)
        
        assert len(books) > 0
    
    def test_search_books_by_title(self, mock_db, sample_book):
        """Test searching books by title"""
        results = Book.get_by_title(mock_db, sample_book.title)
        
        assert len(results) > 0
        assert any(b.title == sample_book.title for b in results)
    
    def test_search_books_by_author(self, mock_db, sample_book):
        """Test searching books by author"""
        results = Book.get_by_author(mock_db, sample_book.author)
        
        assert len(results) > 0
    
    def test_search_books_by_category(self, mock_db, sample_book):
        """Test searching books by category"""
        results = Book.get_by_category(mock_db, sample_book.category)
        
        assert len(results) > 0


class TestBookAvailability:
    """Test Book availability operations"""
    
    def test_check_book_available(self, mock_db, sample_book):
        """Test checking if book is available"""
        available_books = Book.get_available_books(mock_db)
        
        assert len(available_books) > 0
        assert any(b._id == sample_book._id for b in available_books)
    
    def test_reduce_availability(self, mock_db, sample_book):
        """Test reducing book availability"""
        original_available = sample_book.available
        sample_book.available -= 1
        sample_book.save(mock_db)
        
        updated_book = Book.get_by_id(mock_db, str(sample_book._id))
        assert updated_book.available == original_available - 1 # type: ignore
    
    def test_increase_availability(self, mock_db, sample_book):
        """Test increasing book availability"""
        original_available = sample_book.available
        sample_book.available += 1
        sample_book.save(mock_db)
        
        updated_book = Book.get_by_id(mock_db, str(sample_book._id))
        assert updated_book.available == original_available + 1 # type: ignore


class TestBookValidation:
    """Test Book model validation"""
    
    def test_book_with_zero_year(self):
        """Test creating book with zero year"""
        book = Book(
            title="Test",
            author="Author",
            publisher="Publisher",
            year=0,
            category="Science"
        )
        
        assert book.year == 0
    
    def test_book_with_negative_quantity(self):
        """Test creating book with negative quantity"""
        book = Book(
            title="Test",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science",
            quantity=-5
        )
        
        assert book.quantity == -5
    
    def test_book_with_empty_title(self):
        """Test creating book with empty title"""
        book = Book(
            title="",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science"
        )
        
        assert book.title == ""


class TestBookStatistics:
    """Test Book statistics and reporting"""
    
    def test_count_total_books(self, mock_db, sample_books):
        """Test counting total books"""
        books = Book.get_all(mock_db)
        
        assert len(books) > 0
    
    def test_get_books_by_category(self, mock_db):
        """Test grouping books by category"""
        book1 = Book("Book1", "Author1", "Pub1", 2023, "Science")
        book2 = Book("Book2", "Author2", "Pub2", 2023, "Fiction")
        book1.save(mock_db)
        book2.save(mock_db)
        
        science_books = Book.get_by_category(mock_db, "Science")
        
        assert any(b.category == "Science" for b in science_books)
