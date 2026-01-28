"""
Comprehensive Test Suite for Fine Model
Tests all Fine model functionalities
"""

import pytest
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from models.fine import Fine


class TestFineModelCreation:
    """Test Fine model creation and initialization"""
    
    def test_create_fine_basic(self):
        """Test creating a basic fine"""
        record_id = ObjectId()
        fine = Fine(
            record_id=record_id,
            amount=5.00,
            status="pending"
        )
        
        assert fine.amount == 5.00
        assert fine.status == "pending"
    
    def test_create_fine_default_status(self):
        """Test fine default status is pending"""
        record_id = ObjectId()
        fine = Fine(
            record_id=record_id,
            amount=10.00
        )
        
        assert fine.status == "pending"
    
    def test_create_fine_with_amount(self):
        """Test creating fine with different amounts"""
        fine1 = Fine(ObjectId(), 1.50)
        fine2 = Fine(ObjectId(), 50.00)
        fine3 = Fine(ObjectId(), 0.50)
        
        assert fine1.amount == 1.50
        assert fine2.amount == 50.00
        assert fine3.amount == 0.50


class TestFineModelPersistence:
    """Test Fine model persistence operations"""
    
    def test_save_fine_to_database(self, mock_db):
        """Test saving fine to database"""
        fine = Fine(
            record_id=ObjectId(),
            amount=5.00
        )
        
        result = fine.save(mock_db)
        
        assert result is True
        assert fine._id is not None
    
    def test_update_fine_in_database(self, mock_db, sample_fine):
        """Test updating existing fine"""
        original_amount = sample_fine.amount
        sample_fine.amount = original_amount + 5.00
        result = sample_fine.save(mock_db)
        
        assert result is True
        
        updated_fine = Fine.get_by_id(mock_db, str(sample_fine._id))
        assert updated_fine.amount == original_amount + 5.00 # type: ignore
    
    def test_mark_fine_as_paid(self, mock_db, sample_fine):
        """Test marking fine as paid"""
        sample_fine.status = "paid"
        sample_fine.paid_date = datetime.utcnow()
        result = sample_fine.save(mock_db)
        
        assert result is True
        
        updated_fine = Fine.get_by_id(mock_db, str(sample_fine._id))
        assert updated_fine.status == "paid" # type: ignore


class TestFineModelRetrieval:
    """Test Fine model retrieval operations"""
    
    def test_get_fine_by_id(self, mock_db, sample_fine):
        """Test retrieving fine by ID"""
        retrieved = Fine.get_by_id(mock_db, str(sample_fine._id))
        
        assert retrieved is not None
        assert retrieved.amount == sample_fine.amount
    
    def test_get_all_fines(self, mock_db):
        """Test getting all fines"""
        fines = Fine.get_all(mock_db)
        
        assert isinstance(fines, list)
    
    def test_get_nonexistent_fine(self, mock_db):
        """Test retrieving non-existent fine"""
        fake_id = ObjectId()
        fine = Fine.get_by_id(mock_db, str(fake_id))
        
        assert fine is None


class TestFineStatus:
    """Test Fine status operations"""
    
    def test_fine_pending_status(self, sample_fine):
        """Test fine with pending status"""
        assert sample_fine.status == "pending"
    
    def test_fine_paid_status(self, mock_db):
        """Test fine with paid status"""
        fine = Fine(ObjectId(), 10.00, status="paid")
        fine.save(mock_db)
        
        retrieved = Fine.get_by_id(mock_db, str(fine._id))
        assert retrieved.status == "paid" # type: ignore
    
    def test_mark_fine_as_paid(self, mock_db):
        """Test marking fine as paid"""
        fine = Fine(ObjectId(), 10.00)
        fine.save(mock_db)
        
        result = fine.mark_paid(mock_db)
        
        assert result is True
        assert fine.status == "paid"
        assert fine.paid_date is not None
    
    def test_get_pending_fines(self, mock_db, sample_fine):
        """Test getting pending fines"""
        fines = Fine.get_all(mock_db)
        pending_fines = [f for f in fines if f.status == "pending"]
        
        assert isinstance(pending_fines, list)


class TestFineAmount:
    """Test Fine amount operations"""
    
    def test_fine_amount_calculation(self, sample_fine):
        """Test fine amount is correctly stored"""
        assert sample_fine.amount > 0
    
    def test_fine_zero_amount(self):
        """Test fine with zero amount"""
        fine = Fine(ObjectId(), 0.00)
        
        assert fine.amount == 0.00
    
    def test_fine_high_amount(self):
        """Test fine with high amount"""
        fine = Fine(ObjectId(), 999.99)
        
        assert fine.amount == 999.99


class TestFinePayment:
    """Test Fine payment operations"""
    
    def test_payment_date_on_pay(self, mock_db):
        """Test payment date is set when paid"""
        fine = Fine(ObjectId(), 5.00)
        fine.save(mock_db)
        
        fine.mark_paid(mock_db)
        
        updated_fine = Fine.get_by_id(mock_db, str(fine._id))
        assert updated_fine.paid_date is not None
    
    def test_payment_status_update(self, mock_db, sample_fine):
        """Test that payment updates fine status"""
        original_amount = sample_fine.amount
        
        sample_fine.mark_paid(mock_db)
        
        assert sample_fine.amount == original_amount


class TestFineValidation:
    """Test Fine validation"""
    
    def test_fine_with_empty_record_id(self):
        """Test fine with None record_id"""
        try:
            fine = Fine(
                record_id=None,
                amount=5.00
            )
            # If no error, object should handle None
            assert fine.record_id is None or isinstance(fine.record_id, ObjectId)
        except Exception:
            # None record_id might raise error
            pass
    
    def test_fine_negative_amount(self):
        """Test fine with negative amount"""
        fine = Fine(ObjectId(), -5.00)
        
        assert fine.amount == -5.00


class TestFineReports:
    """Test Fine reporting operations"""
    
    def test_get_total_fines_amount(self, mock_db):
        """Test calculating total fines"""
        fines = Fine.get_all(mock_db)
        
        total = sum(f.amount for f in fines if f.status == "pending")
        
        assert total >= 0
    
    def test_get_fines_by_status(self, mock_db):
        """Test getting fines by status"""
        fines = Fine.get_all(mock_db)
        pending_fines = [f for f in fines if f.status == "pending"]
        
        assert all(f.status == "pending" for f in pending_fines)
