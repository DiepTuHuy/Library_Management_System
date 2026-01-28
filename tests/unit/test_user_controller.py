"""
Unit tests for User Controller and User Model
Tests user registration, login, and profile management
"""

import pytest
from controllers.user_controller import UserController
from models.user import User


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_user_success(self, user_controller, mock_db):
        """Test successful user registration"""
        result = user_controller.register_user(
            name="New User",
            email="newuser@example.com",
            password="password123",
            role="member"
        )
        
        assert result["success"] is True
        assert "user_id" in result
        assert result["message"] == "User registered successfully"
    
    def test_register_duplicate_email(self, user_controller, sample_user):
        """Test registration with duplicate email"""
        result = user_controller.register_user(
            name="Another User",
            email=sample_user.email,
            password="password123",
            role="member"
        )
        
        assert result["success"] is False
        assert "already exists" in result["message"]
    
    def test_register_user_with_admin_role(self, user_controller):
        """Test registering a user with admin role"""
        result = user_controller.register_user(
            name="Admin User",
            email="admin2@example.com",
            password="adminpass",
            role="admin"
        )
        
        assert result["success"] is True
        assert result["message"] == "User registered successfully"
    
    def test_register_user_with_librarian_role(self, user_controller):
        """Test registering a user with librarian role"""
        result = user_controller.register_user(
            name="Librarian User",
            email="librarian2@example.com",
            password="libpass",
            role="librarian"
        )
        
        assert result["success"] is True


class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_success(self, user_controller, sample_user):
        """Test successful login"""
        result = user_controller.login(
            email=sample_user.email,
            password="testpass123"
        )
        
        assert result["success"] is True
        assert result["user"]["name"] == sample_user.name
        assert result["user"]["email"] == sample_user.email
        assert result["user"]["role"] == sample_user.role
    
    def test_login_invalid_email(self, user_controller):
        """Test login with invalid email"""
        result = user_controller.login(
            email="nonexistent@example.com",
            password="password123"
        )
        
        assert result["success"] is False
        assert "Invalid" in result["message"]
    
    def test_login_invalid_password(self, user_controller, sample_user):
        """Test login with wrong password"""
        result = user_controller.login(
            email=sample_user.email,
            password="wrongpassword"
        )
        
        assert result["success"] is False
        assert "Invalid" in result["message"]
    
    def test_login_empty_credentials(self, user_controller):
        """Test login with empty credentials"""
        result = user_controller.login(email="", password="")
        
        assert result["success"] is False


class TestUserModel:
    """Test User model functionality"""
    
    def test_user_creation(self):
        """Test creating a user object"""
        user = User(
            name="Test User",
            email="test@example.com",
            password="testpass",
            role="member"
        )
        
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.role == "member"
        assert user.is_active is True
    
    def test_user_save_and_retrieve(self, mock_db):
        """Test saving and retrieving user from database"""
        user = User(
            name="Save Test",
            email="save@example.com",
            password="savepass",
            role="member"
        )
        
        user.save(mock_db)
        assert user._id is not None
        
        retrieved_user = User.get_by_email(mock_db, "save@example.com")
        assert retrieved_user is not None
        assert retrieved_user.name == "Save Test"
    
    def test_user_soft_delete(self, mock_db):
        """Test soft delete of user"""
        user = User(
            name="Delete Test",
            email="delete@example.com",
            password="delpass",
            role="member"
        )
        
        user.save(mock_db)
        user_id = user._id
        
        user.delete(mock_db)
        assert user.is_active is False
        
        # Deleted user should not be found
        retrieved_user = User.get_by_email(mock_db, "delete@example.com")
        assert retrieved_user is None
    
    def test_user_get_by_id(self, mock_db, sample_user):
        """Test retrieving user by ID"""
        retrieved_user = User.get_by_id(mock_db, str(sample_user._id))
        
        assert retrieved_user is not None
        assert retrieved_user.name == sample_user.name
        assert retrieved_user.email == sample_user.email


class TestUserRoles:
    """Test user role functionality"""
    
    def test_admin_role(self, user_controller, sample_admin):
        """Test admin user"""
        assert sample_admin.role == "admin"
        assert sample_admin.is_active is True
    
    def test_librarian_role(self, user_controller, sample_librarian):
        """Test librarian user"""
        assert sample_librarian.role == "librarian"
        assert sample_librarian.is_active is True
    
    def test_member_role(self, user_controller, sample_user):
        """Test member user"""
        assert sample_user.role == "member"
        assert sample_user.is_active is True
    
    def test_login_as_admin(self, user_controller, sample_admin):
        """Test admin login"""
        result = user_controller.login(
            email=sample_admin.email,
            password="adminpass123"
        )
        
        assert result["success"] is True
        assert result["user"]["role"] == "admin"
    
    def test_login_as_librarian(self, user_controller, sample_librarian):
        """Test librarian login"""
        result = user_controller.login(
            email=sample_librarian.email,
            password="librarianpass123"
        )
        
        assert result["success"] is True
        assert result["user"]["role"] == "librarian"
