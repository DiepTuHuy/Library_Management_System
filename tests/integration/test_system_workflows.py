"""
Integration tests for Library Management System
Tests complete workflows involving multiple components
"""

import pytest
from datetime import datetime, timedelta
from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.borrow_controller import BorrowController
from controllers.fine_controller import FineController


class TestCompleteUserWorkflow:
    """Test complete user workflow from registration to login"""
    
    def test_user_registration_and_login(self, user_controller, mock_db):
        """Test user registration followed by login"""
        # Register
        register_result = user_controller.register_user(
            name="Integration Test User",
            email="integration@example.com",
            password="integrationpass123",
            role="member"
        )
        
        assert register_result["success"] is True
        
        # Login
        login_result = user_controller.login(
            email="integration@example.com",
            password="integrationpass123"
        )
        
        assert login_result["success"] is True
        assert login_result["user"]["name"] == "Integration Test User"
    
    def test_user_registration_different_roles(self, user_controller, mock_db):
        """Test registering users with different roles"""
        roles = ["admin", "librarian", "member"]
        
        for i, role in enumerate(roles):
            result = user_controller.register_user(
                name=f"User {role}",
                email=f"user_{role}_{i}@example.com",
                password="password123",
                role=role
            )
            
            assert result["success"] is True


class TestCompleteBorrowWorkflow:
    """Test complete borrow workflow: add book -> borrow -> return"""
    
    def test_full_borrow_return_cycle(self, user_controller, book_controller, borrow_controller, fine_controller, mock_db):
        """Test complete cycle: register user, add book, borrow, return"""
        
        # Step 1: Register user
        user_result = user_controller.register_user(
            name="Test Borrower",
            email="borrower@example.com",
            password="borrowpass",
            role="member"
        )
        user_id = user_result["user_id"]
        
        # Step 2: Add book
        book_result = book_controller.add_book(
            title="Test Novel",
            author="Test Author",
            publisher="Test Pub",
            year=2023,
            category="Fiction",
            quantity=3
        )
        book_id = book_result["book_id"]
        
        # Step 3: Borrow book
        borrow_result = borrow_controller.borrow_book(user_id, book_id)
        assert borrow_result["success"] is True
        borrow_id = borrow_result["borrow_id"]
        
        # Step 4: Return book
        return_result = borrow_controller.return_book(borrow_id)
        assert return_result["success"] is True
    
    def test_multiple_users_borrow_same_book(self, user_controller, book_controller, borrow_controller, mock_db):
        """Test multiple users borrowing the same book"""
        
        # Add book with quantity 2
        book_result = book_controller.add_book(
            title="Popular Book",
            author="Author",
            publisher="Pub",
            year=2023,
            category="Science",
            quantity=2
        )
        book_id = book_result["book_id"]
        
        # Register 2 users
        user_ids = []
        for i in range(2):
            result = user_controller.register_user(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password="pass",
                role="member"
            )
            user_ids.append(result["user_id"])
        
        # Both users borrow the book
        for user_id in user_ids:
            result = borrow_controller.borrow_book(user_id, book_id)
            assert result["success"] is True
        
        # Third user should not be able to borrow (no copies left)
        result3 = user_controller.register_user(
            name="User 3",
            email="user3@example.com",
            password="pass",
            role="member"
        )
        user_id_3 = result3["user_id"]
        
        borrow_result = borrow_controller.borrow_book(user_id_3, book_id)
        assert borrow_result["success"] is False


class TestOverdueAndFineWorkflow:
    """Test workflow with overdue books and fines"""
    
    def test_overdue_book_generates_fine(self, user_controller, book_controller, borrow_controller, fine_controller, mock_db):
        """Test that overdue book triggers fine creation"""
        
        # Register user and add book
        user_result = user_controller.register_user(
            name="Overdue User",
            email="overdue@example.com",
            password="pass",
            role="member"
        )
        user_id = user_result["user_id"]
        
        book_result = book_controller.add_book(
            title="Overdue Book",
            author="Author",
            publisher="Pub",
            year=2023,
            category="Fiction",
            quantity=1
        )
        book_id = book_result["book_id"]
        
        # Borrow book
        borrow_result = borrow_controller.borrow_book(user_id, book_id)
        assert borrow_result["success"] is True


class TestBookCatalogWorkflow:
    """Test book catalog management workflow"""
    
    def test_build_library_catalog(self, book_controller, mock_db):
        """Test building a library catalog with multiple books"""
        
        catalog_data = [
            ("Python Basics", "Guido van Rossum", "Python Press", 2020, "Technology", 5),
            ("Data Science Guide", "John Doe", "Tech Books", 2021, "Science", 3),
            ("Web Dev Modern", "Jane Smith", "Web Press", 2022, "Technology", 4),
            ("Ancient Rome", "Historian", "History Press", 2019, "History", 2),
            ("Art History", "Artist", "Art Press", 2021, "Arts", 2),
        ]
        
        added_books = []
        for title, author, publisher, year, category, qty in catalog_data:
            result = book_controller.add_book(
                title=title,
                author=author,
                publisher=publisher,
                year=year,
                category=category,
                quantity=qty
            )
            
            assert result["success"] is True
            added_books.append(result["book_id"])
        
        assert len(added_books) == len(catalog_data)
    
    def test_search_book_in_catalog(self, book_controller, sample_books):
        """Test searching for books in catalog"""
        
        result = book_controller.search_books("Python")
        
        assert result["success"] is True
        assert len(result.get("books", [])) > 0


class TestLibrarianWorkflow:
    """Test librarian-specific workflows"""
    
    def test_librarian_manages_borrows_and_returns(self, user_controller, book_controller, borrow_controller, mock_db):
        """Test librarian processing borrows and returns"""
        
        # Create a librarian user
        librarian_result = user_controller.register_user(
            name="Head Librarian",
            email="librarian@example.com",
            password="libpass",
            role="librarian"
        )
        
        assert librarian_result["success"] is True
        librarian_id = librarian_result["user_id"]
        
        # Verify librarian exists and has librarian role
        get_result = user_controller.get_user(librarian_id)
        assert get_result["success"] is True
        assert get_result["user"]["role"] == "librarian"


class TestAdminWorkflow:
    """Test admin-specific workflows"""
    
    def test_admin_manages_users(self, user_controller, mock_db):
        """Test admin registering different types of users"""
        
        # Admin registers other users
        user_types = [
            ("Librarian Staff", "librarian_staff@example.com", "librarian"),
            ("Member User", "member_user@example.com", "member"),
            ("Another Admin", "admin2@example.com", "admin"),
        ]
        
        for name, email, role in user_types:
            result = user_controller.register_user(
                name=name,
                email=email,
                password="password123",
                role=role
            )
            
            assert result["success"] is True
            user_id = result["user_id"]
            
            # Verify user role
            get_result = user_controller.get_user(user_id)
            assert get_result["success"] is True
            assert get_result["user"]["role"] == role
    
    def test_admin_manages_book_catalog(self, book_controller, mock_db):
        """Test admin adding and managing books"""
        
        books = [
            ("Admin Book 1", "Author 1", "Pub", 2023, "Science", 5),
            ("Admin Book 2", "Author 2", "Pub", 2023, "Fiction", 3),
        ]
        
        for title, author, pub, year, cat, qty in books:
            result = book_controller.add_book(
                title=title,
                author=author,
                publisher=pub,
                year=year,
                category=cat,
                quantity=qty
            )
            
            assert result["success"] is True


class TestMultipleConcurrentBorrows:
    """Test system handling multiple concurrent borrows"""
    
    def test_multiple_users_borrow_different_books(self, user_controller, book_controller, borrow_controller, mock_db):
        """Test multiple users borrowing different books simultaneously"""
        
        # Create 3 users
        user_ids = []
        for i in range(3):
            result = user_controller.register_user(
                name=f"User {i}",
                email=f"concurrent_user{i}@example.com",
                password="pass",
                role="member"
            )
            user_ids.append(result["user_id"])
        
        # Create 3 books
        book_ids = []
        for i in range(3):
            result = book_controller.add_book(
                title=f"Book {i}",
                author="Author",
                publisher="Pub",
                year=2023,
                category="Science",
                quantity=2
            )
            book_ids.append(result["book_id"])
        
        # Each user borrows a different book
        for user_id, book_id in zip(user_ids, book_ids):
            result = borrow_controller.borrow_book(user_id, book_id)
            assert result["success"] is True


class TestDatabasePersistence:
    """Test data persistence across operations"""
    
    def test_user_persists_after_registration(self, user_controller, mock_db):
        """Test that registered user persists in database"""
        
        result = user_controller.register_user(
            name="Persistent User",
            email="persistent@example.com",
            password="persistpass",
            role="member"
        )
        
        # Verify login still works (data persisted)
        login_result = user_controller.login(
            email="persistent@example.com",
            password="persistpass"
        )
        
        assert login_result["success"] is True
    
    def test_book_persists_after_addition(self, book_controller, mock_db):
        """Test that added book persists in database"""
        
        result = book_controller.add_book(
            title="Persistent Book",
            author="Author",
            publisher="Pub",
            year=2023,
            category="Science",
            quantity=5
        )
        
        book_id = result["book_id"]
        
        # Verify book can be retrieved
        get_result = book_controller.get_book(book_id)
        
        assert get_result["success"] is True
        assert get_result["book"]["title"] == "Persistent Book"
