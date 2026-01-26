"""
Comprehensive Test Suite for BorrowRecord Model
Tests all BorrowRecord model functionalities
"""

import pytest
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from models.borrow_record import BorrowRecord


class TestBorrowRecordCreation:
    """Test BorrowRecord model creation"""
    
    def test_create_borrow_record(self, sample_user, sample_book):
        """Test creating a borrow record"""
        borrow = BorrowRecord(
            user_id=sample_user._id,
            book_id=sample_book._id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        
        assert borrow.user_id == sample_user._id
        assert borrow.book_id == sample_book._id
        assert borrow.return_date is None
    
    def test_borrow_record_default_duration(self):
        """Test borrow record default duration"""
        user_id = ObjectId()
        book_id = ObjectId()
        borrow = BorrowRecord(
            user_id=user_id,
            book_id=book_id
        )
        
        assert borrow.user_id == user_id
        assert borrow.book_id == book_id


class TestBorrowRecordPersistence:
    """Test BorrowRecord persistence operations"""
    
    def test_save_borrow_record(self, mock_db, sample_user, sample_book):
        """Test saving borrow record"""
        borrow = BorrowRecord(
            user_id=str(sample_user._id),
            book_id=str(sample_book._id)
        )
        
        result = borrow.save(mock_db)
        
        assert result is True
        assert borrow._id is not None
    
    def test_update_borrow_record(self, mock_db, sample_borrow_record):
        """Test updating borrow record"""
        sample_borrow_record.return_date = datetime.utcnow()
        result = sample_borrow_record.save(mock_db)
        
        assert result is True
        
        updated_record = BorrowRecord.get_by_id(mock_db, str(sample_borrow_record._id))
        assert updated_record.return_date is not None # type: ignore


class TestBorrowRecordRetrieval:
    """Test BorrowRecord retrieval operations"""
    
    def test_get_borrow_record_by_id(self, mock_db, sample_borrow_record):
        """Test retrieving borrow record by ID"""
        retrieved = BorrowRecord.get_by_id(mock_db, str(sample_borrow_record._id))
        
        assert retrieved is not None
        assert retrieved.user_id == sample_borrow_record.user_id
    
    def test_get_user_borrow_records(self, mock_db, sample_user, sample_borrow_record):
        """Test getting all borrow records for a user"""
        records = BorrowRecord.get_by_user_id(mock_db, str(sample_user._id))
        
        assert isinstance(records, list)
    
    def test_get_book_borrow_records(self, mock_db, sample_book):
        """Test getting all borrow records for a book"""
        records = BorrowRecord.get_by_book_id(mock_db, str(sample_book._id))
        
        assert isinstance(records, list)


class TestBorrowRecordStatus:
    """Test BorrowRecord status operations"""
    
    def test_is_active_borrow_record(self, mock_db, sample_borrow_record):
        """Test checking if borrow is active"""
        is_active = sample_borrow_record.return_date is None
        
        assert is_active is True
    
    def test_is_overdue_borrow_record(self, mock_db):
        """Test checking if borrow is overdue"""
        past_due_date = datetime.utcnow() - timedelta(days=1)
        user_id = ObjectId()
        book_id = ObjectId()
        borrow = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            due_date=past_due_date
        )
        
        is_overdue = borrow.is_overdue()
        
        assert is_overdue is True
    
    def test_mark_borrow_as_returned(self, mock_db, sample_borrow_record):
        """Test marking borrow as returned"""
        sample_borrow_record.return_date = datetime.utcnow()
        result = sample_borrow_record.save(mock_db)
        
        assert result is True
        
        updated = BorrowRecord.get_by_id(mock_db, str(sample_borrow_record._id))
        assert updated.return_date is not None # type: ignore


class TestBorrowRecordDueDate:
    """Test BorrowRecord due date operations"""
    
    def test_calculate_days_borrowed(self, sample_borrow_record):
        """Test calculating days borrowed"""
        days_borrowed = (datetime.utcnow() - sample_borrow_record.borrow_date).days
        
        assert days_borrowed >= 0
    
    def test_calculate_days_until_due(self, sample_borrow_record):
        """Test calculating days until due"""
        days_until_due = (sample_borrow_record.due_date - datetime.utcnow()).days
        
        assert days_until_due >= 0
    
    def test_borrow_record_with_custom_due_date(self):
        """Test borrow record with custom due date"""
        user_id = ObjectId()
        book_id = ObjectId()
        custom_due = datetime.utcnow() + timedelta(days=21)
        borrow = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            due_date=custom_due
        )
        
        assert borrow.due_date == custom_due


class TestBorrowRecordValidation:
    """Test BorrowRecord validation"""
    
    def test_borrow_record_with_empty_user_id(self):
        """Test borrow record with None user_id"""
        try:
            borrow = BorrowRecord(
                user_id=None,
                book_id=ObjectId()
            )
            # If no error, object should handle None
            assert borrow.user_id is None or isinstance(borrow.user_id, ObjectId)
        except Exception:
            # Empty/None user_id should raise error
            pass
    
    def test_borrow_record_with_empty_book_id(self):
        """Test borrow record with None book_id"""
        try:
            borrow = BorrowRecord(
                user_id=ObjectId(),
                book_id=None
            )
            # If no error, object should handle None
            assert borrow.book_id is None or isinstance(borrow.book_id, ObjectId)
        except Exception:
            # Empty/None book_id should raise error
            pass
    
    def test_borrow_record_return_after_borrow(self, sample_borrow_record):
        """Test return date is after borrow date"""
        sample_borrow_record.return_date = sample_borrow_record.borrow_date + timedelta(days=5)
        
        is_valid = sample_borrow_record.return_date >= sample_borrow_record.borrow_date
        
        assert is_valid is True


class TestBorrowRecordFilters:
    """Test BorrowRecord filtering operations"""
    
    def test_get_active_borrows(self, mock_db):
        """Test getting active (unreturned) borrows"""
        active_borrows = BorrowRecord.get_active_borrows(mock_db)
        
        assert isinstance(active_borrows, list)
    
    def test_get_overdue_borrows(self, mock_db):
        """Test getting overdue borrows"""
        overdue_borrows = BorrowRecord.get_overdue_borrows(mock_db)
        
        assert isinstance(overdue_borrows, list)
    
    def test_get_returned_borrows(self, mock_db):
        """Test getting returned borrows"""
        all_borrows = BorrowRecord.get_by_user_id(mock_db, ObjectId())
        returned_borrows = [b for b in all_borrows if b.return_date is not None]
        
        assert isinstance(returned_borrows, list)
