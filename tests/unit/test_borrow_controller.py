"""
Unit tests for Borrow Controller and Borrow Record Model
Tests book borrowing, returning, and borrow record management
"""

import pytest
from datetime import datetime, timedelta
from controllers.borrow_controller import BorrowController
from models.borrow_record import BorrowRecord
from bson import ObjectId


class TestBorrowBook:
    """Test book borrowing functionality"""
    
    def test_borrow_book_success(self, borrow_controller, sample_user, sample_book):
        """Test successfully borrowing a book"""
        result = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        assert result["success"] is True
        assert "borrow_id" in result
        assert "due_date" in result
    
    def test_borrow_book_not_found(self, borrow_controller, sample_user):
        """Test borrowing non-existent book"""
        fake_book_id = ObjectId()
        result = borrow_controller.borrow_book(
            str(sample_user._id),
            str(fake_book_id)
        )
        
        assert result["success"] is False
        assert "not found" in result["message"]
    
    def test_borrow_no_available_copies(self, borrow_controller, sample_user, mock_db, sample_book):
        """Test borrowing when no copies available"""
        sample_book.available = 0
        sample_book.save(mock_db)
        
        result = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        assert result["success"] is False
        assert "No available copies" in result["message"]
    
    def test_borrow_same_book_twice(self, borrow_controller, sample_user, mock_db, sample_book):
        """Test borrowing same book twice (should fail)"""
        # Borrow once
        result1 = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        assert result1["success"] is True
        
        # Try to borrow again
        result2 = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        assert result2["success"] is False
        assert "already have this book" in result2["message"]
    
    def test_borrow_decreases_availability(self, borrow_controller, sample_user, mock_db, sample_book):
        """Test that borrowing decreases available count"""
        initial_available = sample_book.available
        
        borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        from models.book import Book
        updated_book = Book.get_by_id(mock_db, str(sample_book._id))
        assert updated_book.available == initial_available - 1 # type: ignore


class TestReturnBook:
    """Test book return functionality"""
    
    def test_return_book_success(self, borrow_controller, sample_borrow_record):
        """Test successfully returning a book"""
        result = borrow_controller.return_book(str(sample_borrow_record._id))
        
        assert result["success"] is True
        assert "fine_amount" in result
    
    def test_return_nonexistent_borrow(self, borrow_controller):
        """Test returning non-existent borrow record"""
        fake_id = ObjectId()
        result = borrow_controller.return_book(str(fake_id))
        
        assert result["success"] is False
        assert "not found" in result["message"]
    
    def test_return_already_returned_book(self, borrow_controller, mock_db, sample_borrow_record):
        """Test returning already returned book"""
        # Return once
        borrow_controller.return_book(str(sample_borrow_record._id))
        
        # Try to return again
        result = borrow_controller.return_book(str(sample_borrow_record._id))
        
        assert result["success"] is False
        assert "already returned" in result["message"]
    
    def test_return_increases_availability(self, borrow_controller, sample_user, mock_db, sample_book):
        """Test that returning increases available count"""
        initial_available = sample_book.available
        
        # Borrow
        borrow_result = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        borrow_id = borrow_result["borrow_id"]
        
        # Return
        borrow_controller.return_book(borrow_id)
        
        from models.book import Book
        updated_book = Book.get_by_id(mock_db, str(sample_book._id))
        assert updated_book.available == initial_available # type: ignore


class TestBorrowRecordModel:
    """Test BorrowRecord model functionality"""
    
    def test_borrow_record_creation(self, sample_user, sample_book):
        """Test creating a borrow record"""
        borrow = BorrowRecord(
            user_id=str(sample_user._id),
            book_id=str(sample_book._id)
        )
        
        # BorrowRecord converts string to ObjectId
        assert str(borrow.user_id) == str(sample_user._id)
        assert str(borrow.book_id) == str(sample_book._id)
        assert borrow.return_date is None
    
    def test_borrow_record_save_and_retrieve(self, mock_db, sample_user, sample_book):
        """Test saving and retrieving borrow record"""
        borrow = BorrowRecord(
            user_id=str(sample_user._id),
            book_id=str(sample_book._id)
        )
        
        borrow.save(mock_db)
        assert borrow._id is not None
        
        retrieved = BorrowRecord.get_by_id(mock_db, str(borrow._id))
        assert retrieved is not None
        assert retrieved.user_id == borrow.user_id
    
    def test_borrow_due_date_set(self, sample_borrow_record):
        """Test that due date is set on borrow"""
        assert sample_borrow_record.due_date is not None
        assert isinstance(sample_borrow_record.due_date, datetime)


class TestBorrowDueDate:
    """Test borrow due date functionality"""
    
    def test_due_date_is_14_days(self, sample_borrow_record):
        """Test that due date is 14 days from borrow date"""
        expected_due = sample_borrow_record.borrow_date + timedelta(days=14)
        assert sample_borrow_record.due_date.date() == expected_due.date()
    
    def test_overdue_check(self, mock_db):
        """Test checking if borrow is overdue"""
        # Create a borrow record with past borrow date using valid ObjectIds
        user_id = ObjectId()
        book_id = ObjectId()
        borrow = BorrowRecord(
            user_id=str(user_id),
            book_id=str(book_id)
        )
        
        # Manually set borrow date to 20 days ago
        borrow.borrow_date = datetime.utcnow() - timedelta(days=20)
        borrow.due_date = borrow.borrow_date + timedelta(days=14)
        
        assert borrow.is_overdue() is True


class TestBorrowFilters:
    """Test borrow record filtering"""
    
    def test_get_user_borrows(self, borrow_controller, sample_user, sample_books):
        """Test getting all borrows for a user"""
        result = borrow_controller.get_user_active_borrows(str(sample_user._id))
        
        assert result["success"] is True
        assert "records" in result
    
    def test_get_active_borrows(self, borrow_controller, sample_user, mock_db, sample_book):
        """Test getting active borrows"""
        # Create active borrow
        borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        result = borrow_controller.get_all_active_borrows()
        
        assert result["success"] is True
        assert "records" in result
        assert len(result["records"]) > 0
    
    def test_get_overdue_borrows(self, borrow_controller):
        """Test getting overdue borrows"""
        result = borrow_controller.get_overdue_borrows()
        
        assert result["success"] is True
        assert "records" in result
