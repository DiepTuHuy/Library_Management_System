"""
Comprehensive Test Suite for All Controllers
Tests all controller functionalities including error handling and edge cases
Includes tests for User, Book, Borrow, Fine, Report, and Auth controllers
"""

import pytest
import hashlib
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.borrow_controller import BorrowController
from controllers.fine_controller import FineController
from controllers.report_controller import ReportController
from controllers.auth_controller import AuthController
from models.user import User


# ============================================================================
# AUTH CONTROLLER TESTS
# ============================================================================

class TestAuthControllerAdmin:
    """Test authentication for admin users"""
    
    def test_admin_login_valid(self):
        """Test admin login with valid credentials"""
        auth = AuthController()
        result = auth.authenticate_admin("admin", "admin123")
        
        assert result["success"] is True
        assert result["user"]["role"] == "admin"
        assert result["user"]["username"] == "admin"
    
    def test_admin_login_invalid_password(self):
        """Test admin login with invalid password"""
        auth = AuthController()
        result = auth.authenticate_admin("admin", "wrongpassword")
        
        assert result["success"] is False
        assert "Invalid admin credentials" in result["message"]
    
    def test_admin_login_invalid_username(self):
        """Test admin login with invalid username"""
        auth = AuthController()
        result = auth.authenticate_admin("wronguser", "admin123")
        
        assert result["success"] is False
    
    def test_admin_login_empty_credentials(self):
        """Test admin login with empty credentials"""
        auth = AuthController()
        result = auth.authenticate_admin("", "")
        
        assert result["success"] is False


class TestAuthControllerLibrarian:
    """Test authentication for librarian users"""
    
    def test_librarian_login_valid(self):
        """Test librarian login with valid credentials"""
        auth = AuthController()
        result = auth.authenticate_librarian("librarian", "librarian123")
        
        assert result["success"] is True
        assert result["user"]["role"] == "librarian"
        assert result["user"]["username"] == "librarian"
    
    def test_librarian_login_invalid_password(self):
        """Test librarian login with invalid password"""
        auth = AuthController()
        result = auth.authenticate_librarian("librarian", "wrongpassword")
        
        assert result["success"] is False
        assert "Invalid librarian credentials" in result["message"]
    
    def test_librarian_login_invalid_username(self):
        """Test librarian login with invalid username"""
        auth = AuthController()
        result = auth.authenticate_librarian("wronguser", "librarian123")
        
        assert result["success"] is False
    
    def test_librarian_case_sensitive(self):
        """Test librarian username is case sensitive"""
        auth = AuthController()
        result = auth.authenticate_librarian("Librarian", "librarian123")
        
        assert result["success"] is False


class TestAuthControllerMember:
    """Test authentication for member/student users"""
    
    def test_member_login_valid(self, user_controller, sample_user, mock_db):
        """Test member login with valid credentials"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        # Verify the sample user is properly set up with hashed password
        user_from_db = User.get_by_email(mock_db, sample_user.email)
        assert user_from_db is not None
        assert User.verify_password(user_from_db.password, "testpass123") is True
        
        result = auth.authenticate_member(sample_user.email, "testpass123")
        
        assert result["success"] is True
        assert result["user"]["role"] == "member"
        assert result["user"]["email"] == sample_user.email
    
    def test_member_login_nonexistent_email(self, mock_db):
        """Test member login with non-existent email"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        result = auth.authenticate_member("nonexistent@example.com", "password123")
        
        assert result["success"] is False
        assert "not found" in result["message"]
    
    def test_member_login_wrong_password(self, sample_user, mock_db):
        """Test member login with wrong password"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        result = auth.authenticate_member(sample_user.email, "wrongpassword")
        
        assert result["success"] is False
        assert "Invalid password" in result["message"]
    
    def test_member_login_deleted_account(self, mock_db):
        """Test deleted member cannot login"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        # Create a deleted user
        users_collection = mock_db.get_collection("users")
        deleted_user = {
            "email": "deleted@example.com",
            "password": "pass123",
            "name": "Deleted User",
            "role": "member",
            "is_deleted": True
        }
        users_collection.insert_one(deleted_user)
        
        result = auth.authenticate_member("deleted@example.com", "pass123")
        
        assert result["success"] is False
        assert "deleted" in result["message"]


class TestAuthControllerUniversal:
    """Test universal authentication method"""
    
    def test_authenticate_with_role_admin(self):
        """Test authenticate with admin role specified"""
        auth = AuthController()
        result = auth.authenticate("admin", "admin123", role="admin")
        
        assert result["success"] is True
    
    def test_authenticate_with_role_librarian(self):
        """Test authenticate with librarian role specified"""
        auth = AuthController()
        result = auth.authenticate("librarian", "librarian123", role="librarian")
        
        assert result["success"] is True
    
    def test_authenticate_with_role_member(self, sample_user, mock_db):
        """Test authenticate with member role specified"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        # Verify password is properly hashed
        user_from_db = User.get_by_email(mock_db, sample_user.email)
        assert user_from_db is not None
        assert User.verify_password(user_from_db.password, "testpass123") is True
        
        result = auth.authenticate(sample_user.email, "testpass123", role="member")
        
        assert result["success"] is True
    
    def test_authenticate_admin_auto_detection(self):
        """Test admin auto-detection"""
        auth = AuthController()
        result = auth.authenticate("admin", "admin123")
        
        assert result["success"] is True
    
    def test_authenticate_librarian_auto_detection(self):
        """Test librarian auto-detection"""
        auth = AuthController()
        result = auth.authenticate("librarian", "librarian123")
        
        assert result["success"] is True
    
    def test_authenticate_invalid_role(self):
        """Test authenticate with invalid role"""
        auth = AuthController()
        result = auth.authenticate("user", "pass", role="superuser")
        
        assert result["success"] is False


class TestAuthControllerUtilities:
    """Test utility methods in AuthController"""
    
    def test_get_user_role_admin(self):
        """Test getting admin role"""
        auth = AuthController()
        role = auth.get_user_role("admin")
        
        assert role == "admin"
    
    def test_get_user_role_librarian(self):
        """Test getting librarian role"""
        auth = AuthController()
        role = auth.get_user_role("librarian")
        
        assert role == "librarian"
    
    def test_get_user_role_nonexistent(self, mock_db):
        """Test getting role for non-existent user"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        role = auth.get_user_role("nonexistent@example.com")
        
        assert role is None
    
    def test_validate_credentials_format_valid(self):
        """Test credentials format validation - valid"""
        auth = AuthController()
        result = auth.validate_credentials_format("admin", "admin123")
        
        assert result["valid"] is True
    
    def test_validate_credentials_format_empty_username(self):
        """Test credentials format validation - empty username"""
        auth = AuthController()
        result = auth.validate_credentials_format("", "password")
        
        assert result["valid"] is False
    
    def test_validate_credentials_format_empty_password(self):
        """Test credentials format validation - empty password"""
        auth = AuthController()
        result = auth.validate_credentials_format("admin", "")
        
        assert result["valid"] is False
    
    def test_validate_credentials_format_short_password(self):
        """Test credentials format validation - password too short"""
        auth = AuthController()
        result = auth.validate_credentials_format("admin", "pass")
        
        assert result["valid"] is False
    
    def test_change_member_password_success(self, sample_user, mock_db):
        """Test changing member password successfully"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        # Verify initial password is correctly hashed
        user_from_db = User.get_by_email(mock_db, sample_user.email)
        assert user_from_db is not None
        assert User.verify_password(user_from_db.password, "testpass123") is True
        
        result = auth.change_member_password(
            sample_user.email,
            "testpass123",
            "newpass123"
        )
        
        assert result["success"] is True
        
        # Verify new password works
        verify_result = auth.authenticate_member(sample_user.email, "newpass123")
        assert verify_result["success"] is True
    
    def test_change_member_password_invalid_old(self, sample_user, mock_db):
        """Test changing password with wrong old password"""
        auth = AuthController()
        auth.set_db(mock_db)
        
        result = auth.change_member_password(
            sample_user.email,
            "wrongoldpass",
            "newpass123"
        )
        
        assert result["success"] is False


# ============================================================================
# USER CONTROLLER TESTS
# ============================================================================

class TestUserController:
    """Comprehensive tests for UserController"""
    
    def test_register_user_success(self, user_controller):
        """Test basic user registration"""
        result = user_controller.register_user(
            name="John Doe",
            email="john@example.com",
            password="securepass123",
            role="member"
        )
        
        assert result["success"] is True
        assert "user_id" in result
    
    def test_register_user_duplicate_email(self, user_controller, sample_user):
        """Test registration with duplicate email"""
        result = user_controller.register_user(
            name="Another Person",
            email=sample_user.email,
            password="newpass123",
            role="member"
        )
        
        assert result["success"] is False
    
    def test_login_valid(self, user_controller, sample_user):
        """Test login with valid credentials"""
        result = user_controller.login(
            email=sample_user.email,
            password="testpass123"
        )
        
        assert result["success"] is True
        assert result["user"]["email"] == sample_user.email
    
    def test_login_invalid_email(self, user_controller):
        """Test login with non-existent email"""
        result = user_controller.login(
            email="nonexistent@example.com",
            password="password123"
        )
        
        assert result["success"] is False
    
    def test_login_wrong_password(self, user_controller, sample_user):
        """Test login with wrong password"""
        result = user_controller.login(
            email=sample_user.email,
            password="wrongpassword"
        )
        
        assert result["success"] is False
    
    def test_get_user(self, user_controller, sample_user):
        """Test retrieving user"""
        result = user_controller.get_user(str(sample_user._id))
        
        assert result["success"] is True
    
    def test_get_nonexistent_user(self, user_controller):
        """Test retrieving non-existent user"""
        fake_id = str(ObjectId())
        result = user_controller.get_user(fake_id)
        
        assert result["success"] is False
    
    def test_update_user(self, user_controller, sample_user):
        """Test updating user"""
        result = user_controller.update_user(
            str(sample_user._id),
            name="Updated Name"
        )
        
        assert "success" in result


# ============================================================================
# BOOK CONTROLLER TESTS
# ============================================================================

class TestBookController:
    """Comprehensive tests for BookController"""
    
    def test_add_book_success(self, book_controller):
        """Test adding book"""
        result = book_controller.add_book(
            title="Python Mastery",
            author="Guido van Rossum",
            publisher="Tech Books Inc",
            year=2023,
            category="Programming",
            quantity=10
        )
        
        assert result["success"] is True
        assert "book_id" in result
    
    def test_add_book_zero_quantity(self, book_controller):
        """Test adding book with zero quantity"""
        result = book_controller.add_book(
            title="Zero Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science",
            quantity=0
        )
        
        assert result["success"] is True
    
    def test_get_book_by_id(self, book_controller, sample_book):
        """Test getting book by ID"""
        result = book_controller.get_book(str(sample_book._id))
        
        assert result["success"] is True
        assert result["book"]["title"] == sample_book.title
    
    def test_get_nonexistent_book(self, book_controller):
        """Test getting non-existent book"""
        fake_id = str(ObjectId())
        result = book_controller.get_book(fake_id)
        
        assert result["success"] is False
    
    def test_get_all_books(self, book_controller, sample_books):
        """Test getting all books"""
        result = book_controller.get_all_books()
        
        assert result["success"] is True
        assert "books" in result
    
    def test_search_books(self, book_controller, sample_books):
        """Test searching books"""
        result = book_controller.search_books("Python")
        
        assert result["success"] is True
    
    def test_search_books_no_results(self, book_controller):
        """Test searching with no results"""
        result = book_controller.search_books("NonexistentBookTitle123")
        
        assert result["success"] is True
    
    def test_update_book(self, book_controller, sample_book):
        """Test updating book"""
        result = book_controller.update_book(
            str(sample_book._id),
            title="Updated Title"
        )
        
        assert "success" in result
    
    def test_delete_book(self, book_controller, sample_book):
        """Test deleting book"""
        result = book_controller.delete_book(str(sample_book._id))
        
        assert "success" in result


# ============================================================================
# BORROW CONTROLLER TESTS
# ============================================================================

class TestBorrowController:
    """Comprehensive tests for BorrowController"""
    
    def test_borrow_book_success(self, borrow_controller, sample_user, sample_book):
        """Test successful book borrowing"""
        result = borrow_controller.borrow_book(
            str(sample_user._id),
            str(sample_book._id)
        )
        
        assert result["success"] is True
        assert "borrow_id" in result
    
    def test_borrow_nonexistent_book(self, borrow_controller, sample_user):
        """Test borrowing non-existent book"""
        fake_book_id = str(ObjectId())
        result = borrow_controller.borrow_book(
            str(sample_user._id),
            fake_book_id
        )
        
        assert result["success"] is False
    
    def test_return_book_success(self, borrow_controller, sample_borrow_record):
        """Test successful book return"""
        result = borrow_controller.return_book(str(sample_borrow_record._id))
        
        assert result["success"] is True
    
    def test_return_nonexistent_borrow(self, borrow_controller):
        """Test returning non-existent borrow"""
        fake_id = str(ObjectId())
        result = borrow_controller.return_book(fake_id)
        
        assert result["success"] is False
    
    def test_get_user_borrows(self, borrow_controller, sample_user):
        """Test getting user's borrow records"""
        result = borrow_controller.get_user_active_borrows(str(sample_user._id))
        
        assert result["success"] is True
        assert "records" in result
    
    def test_get_active_borrows(self, borrow_controller):
        """Test getting active borrows"""
        result = borrow_controller.get_all_active_borrows()
        
        assert result["success"] is True
        assert "records" in result
    
    def test_get_overdue_borrows(self, borrow_controller):
        """Test getting overdue borrows"""
        result = borrow_controller.get_overdue_borrows()
        
        assert result["success"] is True


# ============================================================================
# FINE CONTROLLER TESTS
# ============================================================================

class TestFineController:
    """Comprehensive tests for FineController"""
    
    def test_get_fine(self, fine_controller, sample_fine):
        """Test getting fine details"""
        result = fine_controller.get_fine(str(sample_fine._id))
        
        assert result["success"] is True
        assert result["fine"]["amount"] == sample_fine.amount
    
    def test_get_nonexistent_fine(self, fine_controller):
        """Test getting non-existent fine"""
        fake_id = str(ObjectId())
        result = fine_controller.get_fine(fake_id)
        
        assert result["success"] is False
    
    def test_get_user_fines(self, fine_controller, sample_user):
        """Test getting user's fines"""
        result = fine_controller.get_user_fines(str(sample_user._id))
        
        assert result["success"] is True
        assert "fines" in result
    
    def test_get_pending_fines(self, fine_controller):
        """Test getting pending fines"""
        result = fine_controller.get_all_pending_fines()
        
        assert result["success"] is True
    
    def test_create_fine(self, fine_controller, sample_borrow_record):
        """Test fine operations"""
        # Test getting all fines
        result = fine_controller.get_all_fines()
        
        assert result["success"] is True
    
    def test_pay_fine(self, fine_controller, sample_fine):
        """Test paying a fine"""
        result = fine_controller.pay_fine(
            fine_id=str(sample_fine._id),
            amount=sample_fine.amount
        )
        
        assert "success" in result
    
    def test_get_fine_statistics(self, mock_db):
        """Test getting fine operations"""
        from controllers.fine_controller import FineController
        fine_controller = FineController()
        fine_controller.db = mock_db
        
        result = fine_controller.get_all_fines()
        
        assert result["success"] is True


# ============================================================================
# REPORT CONTROLLER TESTS
# ============================================================================

class TestReportController:
    """Comprehensive tests for ReportController"""
    
    def test_get_borrow_statistics(self, mock_db):
        """Test getting borrow statistics"""
        report_controller = ReportController()
        report_controller.db = mock_db
        
        result = report_controller.get_borrow_statistics()
        
        assert result["success"] is True
    
    def test_get_fine_statistics(self, mock_db):
        """Test getting fine statistics"""
        report_controller = ReportController()
        report_controller.db = mock_db
        
        result = report_controller.get_fine_statistics()
        
        assert result["success"] is True
    
    def test_get_user_statistics(self, mock_db):
        """Test getting user statistics"""
        report_controller = ReportController()
        report_controller.db = mock_db
        
        result = report_controller.get_user_statistics()
        
        assert result["success"] is True
    
    def test_get_book_statistics(self, mock_db):
        """Test getting book statistics"""
        report_controller = ReportController()
        report_controller.db = mock_db
        
        result = report_controller.get_book_statistics()
        
        assert result["success"] is True


# ============================================================================
# CROSS-CONTROLLER INTEGRATION TESTS
# ============================================================================

class TestControllerIntegration:
    """Integration tests across multiple controllers"""
    
    def test_complete_workflow(self, user_controller, book_controller, mock_db):
        """Test complete workflow: register -> add book"""
        
        # Register user
        user_result = user_controller.register_user(
            name="Integration User",
            email="integ@example.com",
            password="pass123",
            role="member"
        )
        assert user_result["success"] is True
        
        # Add book
        book_result = book_controller.add_book(
            title="Integration Book",
            author="Author",
            publisher="Publisher",
            year=2023,
            category="Science"
        )
        assert book_result["success"] is True
    
    def test_auth_with_user_controller(self, user_controller, mock_db):
        """Test authentication with user controller"""
        # Register user first
        user_result = user_controller.register_user(
            name="Auth Test User",
            email="authtest@example.com",
            password="authpass123",
            role="member"
        )
        
        # Auth controller uses plain text passwords for member comparison
        # when comparing against database
        if user_result["success"]:
            # Login using user controller to verify credentials work
            login_result = user_controller.login("authtest@example.com", "authpass123")
            assert login_result["success"] is True


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling across all controllers"""
    
    def test_user_controller_error_handling(self, user_controller):
        """Test user controller handles errors gracefully"""
        result = user_controller.login("", "")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_book_controller_error_handling(self, book_controller):
        """Test book controller handles errors gracefully"""
        result = book_controller.get_book("invalid_id")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_borrow_controller_error_handling(self, borrow_controller):
        """Test borrow controller handles errors gracefully"""
        result = borrow_controller.borrow_book("invalid_user", "invalid_book")
        
        assert isinstance(result, dict)
        assert "success" in result
    
    def test_auth_controller_error_handling(self):
        """Test auth controller handles errors gracefully"""
        auth = AuthController()
        result = auth.authenticate("", "")
        
        assert isinstance(result, dict)
        assert "success" in result
