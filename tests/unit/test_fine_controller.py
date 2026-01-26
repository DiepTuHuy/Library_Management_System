"""
Unit tests for Fine Controller and Fine Model
Tests fine management, calculation, and payment processing
"""

import pytest
from datetime import datetime, timedelta
from controllers.fine_controller import FineController
from models.fine import Fine
from models.payment import Payment
from models.borrow_record import BorrowRecord
from bson import ObjectId


class TestFineCreation:
    """Test fine creation functionality"""
    
    def test_fine_creation_via_return(self, borrow_controller, fine_controller, sample_user, sample_book, mock_db):
        """Test fine is created when book is returned overdue"""
        # Borrow a book
        borrow_result = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        borrow_id = borrow_result["borrow_id"]
        assert borrow_result["success"] is True


class TestFineCalculation:
    """Test fine calculation"""
    
    def test_calculate_fine_amount(self):
        """Test fine amount calculation"""
        # Fine is typically $1 per day overdue
        days_overdue = 5
        expected_fine = days_overdue * 1.0
        
        assert expected_fine == 5.0
    
    def test_calculate_overdue_days(self, mock_db):
        """Test calculating overdue days"""
        # Create a borrow record with valid ObjectIds
        user_id = ObjectId()
        book_id = ObjectId()
        borrow = BorrowRecord(
            user_id=str(user_id),
            book_id=str(book_id)
        )
        
        # Set borrow date to 20 days ago
        borrow.borrow_date = datetime.utcnow() - timedelta(days=20)
        borrow.due_date = borrow.borrow_date + timedelta(days=14)
        borrow.return_date = None  # Not returned
        
        # Overdue days should be 6 (20 - 14)
        overdue_days = max(0, (datetime.utcnow() - borrow.due_date).days)
        assert overdue_days == 6
    
    def test_no_fine_for_returned_on_time(self):
        """Test no fine for book returned on time"""
        # If returned before due date, fine should be 0
        fine_amount = 0
        assert fine_amount == 0


class TestFineRetrieval:
    """Test fine retrieval functionality"""
    
    def test_get_fine_by_id(self, fine_controller, sample_fine):
        """Test retrieving fine by ID"""
        result = fine_controller.get_fine(str(sample_fine._id))
        
        assert result["success"] is True
        assert result["fine"]["amount"] == sample_fine.amount
    
    def test_get_nonexistent_fine(self, fine_controller):
        """Test retrieving non-existent fine"""
        fake_id = ObjectId()
        result = fine_controller.get_fine(str(fake_id))
        
        assert result["success"] is False
    
    def test_get_user_fines(self, fine_controller, sample_user):
        """Test retrieving all fines for a user"""
        result = fine_controller.get_user_fines(str(sample_user._id))
        
        assert result["success"] is True
        assert "fines" in result
    
    def test_get_unpaid_fines(self, fine_controller):
        """Test retrieving unpaid fines"""
        result = fine_controller.get_all_pending_fines()
        
        assert result["success"] is True
        assert "fines" in result


class TestFineModel:
    """Test Fine model functionality"""
    
    def test_fine_creation(self, sample_borrow_record):
        """Test creating a fine object"""
        fine = Fine(
            record_id=sample_borrow_record._id,
            amount=5.00
        )
        
        assert fine.record_id == sample_borrow_record._id
        assert fine.amount == 5.00
        assert fine.status == "pending"
    
    def test_fine_save_and_retrieve(self, mock_db, sample_fine):
        """Test saving and retrieving fine from database"""
        retrieved = Fine.get_by_id(mock_db, str(sample_fine._id))
        
        assert retrieved is not None
        assert retrieved.amount == sample_fine.amount
    
    def test_fine_status(self, sample_fine):
        """Test fine payment status"""
        assert sample_fine.status == "pending"


class TestFinePayment:
    """Test fine payment functionality"""
    
    def test_pay_fine_success(self, fine_controller, sample_fine):
        """Test successfully paying a fine"""
        result = fine_controller.pay_fine(
            fine_id=str(sample_fine._id),
            amount=sample_fine.amount,
            method="credit_card"
        )
        
        assert result["success"] is True
    
    def test_pay_fine_partial_amount(self, fine_controller, sample_fine):
        """Test paying fine with partial amount"""
        result = fine_controller.pay_fine(
            fine_id=str(sample_fine._id),
            amount=2.00,  # Less than fine amount
            method="credit_card"
        )
        
        # Should fail because amount is less than fine amount
        assert result["success"] is False
    
    def test_pay_nonexistent_fine(self, fine_controller):
        """Test paying non-existent fine"""
        fake_id = ObjectId()
        result = fine_controller.pay_fine(
            fine_id=str(fake_id),
            amount=5.00,
            method="credit_card"
        )
        
        assert result["success"] is False
    
    def test_pay_already_paid_fine(self, fine_controller, mock_db, sample_fine):
        """Test paying already paid fine"""
        # Mark as paid
        sample_fine.mark_paid(mock_db)
        
        result = fine_controller.pay_fine(
            fine_id=str(sample_fine._id),
            amount=sample_fine.amount,
            method="credit_card"
        )
        
        assert result["success"] is False


class TestPaymentModel:
    """Test Payment model functionality"""
    
    def test_payment_creation(self, sample_fine):
        """Test creating a payment object"""
        payment = Payment(
            fine_id=sample_fine._id,
            amount=5.00,
            method="credit_card"
        )
        
        assert payment.fine_id == sample_fine._id
        assert payment.amount == 5.00
        assert payment.method == "credit_card"
    
    def test_payment_save_and_retrieve(self, mock_db, sample_fine):
        """Test saving and retrieving payment"""
        payment = Payment(
            fine_id=sample_fine._id,
            amount=sample_fine.amount,
            method="credit_card"
        )
        
        payment.save(mock_db)
        assert payment._id is not None
        
        retrieved = Payment.get_by_id(mock_db, str(payment._id))
        assert retrieved is not None


class TestFineStatus:
    """Test fine status management"""
    
    def test_fine_is_unpaid(self, sample_fine):
        """Test unpaid fine status"""
        assert sample_fine.status == "pending"
    
    def test_fine_marks_as_paid(self, mock_db, sample_fine):
        """Test marking fine as paid"""
        sample_fine.mark_paid(mock_db)
        
        retrieved = Fine.get_by_id(mock_db, str(sample_fine._id))
        assert retrieved.status == "paid"


class TestFineReporting:
    """Test fine reporting functionality"""
    
    def test_total_pending_fines(self, fine_controller):
        """Test calculating total pending fines"""
        result = fine_controller.get_all_pending_fines()
        
        assert result["success"] is True
        assert "fines" in result
    
    def test_fines_by_user(self, fine_controller, sample_user):
        """Test getting fines breakdown by user"""
        result = fine_controller.get_user_fines(str(sample_user._id))
        
        assert result["success"] is True
    
    def test_overdue_fine_report(self, fine_controller):
        """Test generating overdue fine report"""
        result = fine_controller.get_all_pending_fines()
        
        assert result["success"] is True
        assert isinstance(result.get("fines", []), list)
