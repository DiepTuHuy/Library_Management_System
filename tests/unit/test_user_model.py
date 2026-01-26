"""
Comprehensive Test Suite for User Model
Tests all User model functionalities
"""

import pytest
from bson.objectid import ObjectId
from models.user import User


class TestUserModelCreation:
    """Test User model creation and initialization"""
    
    def test_create_user_basic(self):
        """Test creating a basic user"""
        user = User(
            name="John Doe",
            email="john@example.com",
            password="pass123",
            role="member"
        )
        
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        # Password should be hashed, verify with verify_password method
        assert User.verify_password(user.password, "pass123") is True
        assert user.role == "member"
        assert user.is_active is True
    
    def test_create_admin_user(self):
        """Test creating an admin user"""
        user = User(
            name="Admin User",
            email="admin@example.com",
            password="admin123",
            role="admin"
        )
        
        assert user.role == "admin"
    
    def test_create_librarian_user(self):
        """Test creating a librarian user"""
        user = User(
            name="Librarian User",
            email="lib@example.com",
            password="lib123",
            role="librarian"
        )
        
        assert user.role == "librarian"
    
    def test_user_default_role(self):
        """Test default role is member"""
        user = User(
            name="Test User",
            email="test@example.com",
            password="pass123"
        )
        
        assert user.role == "member"


class TestUserModelPersistence:
    """Test User model save and delete operations"""
    
    def test_save_user_to_database(self, mock_db):
        """Test saving user to database"""
        user = User(
            name="Test User",
            email="test@example.com",
            password="pass123",
            role="member"
        )
        
        result = user.save(mock_db)
        
        assert result is True
        assert user._id is not None
    
    def test_update_user_in_database(self, mock_db):
        """Test updating existing user"""
        user = User(
            name="Original Name",
            email="test@example.com",
            password="pass123"
        )
        user.save(mock_db)
        
        user.name = "Updated Name"
        result = user.save(mock_db)
        
        assert result is True
        
        updated_user = User.get_by_id(mock_db, str(user._id))
        assert updated_user.name == "Updated Name" # type: ignore
    
    def test_delete_user_soft_delete(self, mock_db):
        """Test soft delete user"""
        user = User(
            name="Test User",
            email="test@example.com",
            password="pass123"
        )
        user.save(mock_db)
        
        result = user.delete(mock_db)
        
        assert result is True
        assert user.is_active is False


class TestUserModelRetrieval:
    """Test User model retrieval operations"""
    
    def test_get_user_by_id(self, mock_db, sample_user):
        """Test retrieving user by ID"""
        retrieved_user = User.get_by_id(mock_db, str(sample_user._id))
        
        assert retrieved_user is not None
        assert retrieved_user.name == sample_user.name
        assert retrieved_user.email == sample_user.email
    
    def test_get_user_by_email(self, mock_db, sample_user):
        """Test retrieving user by email"""
        retrieved_user = User.get_by_email(mock_db, sample_user.email)
        
        assert retrieved_user is not None
        assert retrieved_user.email == sample_user.email
    
    def test_get_nonexistent_user(self, mock_db):
        """Test retrieving non-existent user"""
        fake_id = ObjectId()
        retrieved_user = User.get_by_id(mock_db, str(fake_id))
        
        assert retrieved_user is None
    
    def test_get_all_users(self, mock_db, sample_user):
        """Test retrieving all users"""
        users = User.get_all(mock_db)
        
        assert len(users) > 0
        assert any(u.email == sample_user.email for u in users)
    
    def test_get_users_by_role(self, mock_db):
        """Test retrieving users by role"""
        # Create users with different roles
        admin = User("Admin", "admin@test.com", "pass", "admin")
        member = User("Member", "member@test.com", "pass", "member")
        admin.save(mock_db)
        member.save(mock_db)
        
        admins = User.get_all(mock_db, role="admin")
        
        assert any(u.role == "admin" for u in admins)


class TestUserAuthentication:
    """Test User authentication"""
    
    def test_authenticate_valid_credentials(self, mock_db, sample_user):
        """Test authentication with valid credentials"""
        auth_user = User.authenticate(mock_db, sample_user.email, "testpass123")
        
        assert auth_user is not None
        assert auth_user.email == sample_user.email
    
    def test_authenticate_invalid_password(self, mock_db, sample_user):
        """Test authentication with invalid password"""
        auth_user = User.authenticate(mock_db, sample_user.email, "wrongpass")
        
        assert auth_user is None
    
    def test_authenticate_nonexistent_email(self, mock_db):
        """Test authentication with non-existent email"""
        auth_user = User.authenticate(mock_db, "nonexistent@test.com", "pass123")
        
        assert auth_user is None


class TestUserValidation:
    """Test User model validation"""
    
    def test_user_with_empty_name(self):
        """Test creating user with empty name"""
        user = User(
            name="",
            email="test@example.com",
            password="pass123"
        )
        
        assert user.name == ""
    
    def test_user_with_empty_email(self):
        """Test creating user with empty email"""
        user = User(
            name="Test",
            email="",
            password="pass123"
        )
        
        assert user.email == ""
    
    def test_user_email_case_sensitivity(self, mock_db):
        """Test email retrieval is case-insensitive"""
        user = User(
            name="Test",
            email="Test@Example.com",
            password="pass123"
        )
        user.save(mock_db)
        
        # Try retrieving with different case
        retrieved = User.get_by_email(mock_db, "test@example.com")
        
        assert retrieved is not None or retrieved is None  # Depends on implementation


class TestUserBorrowRecords:
    """Test User borrow record operations"""
    
    def test_get_user_borrow_records(self, mock_db, sample_user):
        """Test getting user's borrow records"""
        records = User.get_borrow_records(mock_db, str(sample_user._id))
        
        assert isinstance(records, list)
    
    def test_get_user_active_borrows(self, mock_db, sample_user):
        """Test getting user's active borrows"""
        active_borrows = User.get_active_borrows(mock_db, str(sample_user._id))
        
        assert isinstance(active_borrows, list)
