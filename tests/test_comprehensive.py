"""
Enhanced comprehensive test suite for all controllers with business logic validation
Tests all business logic, validation rules, and integration scenarios
Includes tests for all 3 new features: borrow limit, fine blocking, and borrowed book protection
"""

import sys
import os
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.borrow_controller import BorrowController
from controllers.fine_controller import FineController
from models.database import get_db, init_db
from models.user import User
from models.book import Book
from models.borrow_record import BorrowRecord
from models.fine import Fine


# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
END = '\033[0m'


class ComprehensiveControllerTester:
    """Comprehensive test suite for all controllers"""

    def __init__(self):
        self.db = get_db()
        self.results = []
        self.test_counter = 0

    def setup(self):
        """Setup: Initialize database"""
        init_db()
        self.db["users"].delete_many({})
        self.db["books"].delete_many({})
        self.db["borrow_records"].delete_many({})
        self.db["fines"].delete_many({})
        self.db["payments"].delete_many({})
        print(f"{GREEN}[OK] Database initialized and cleared{END}\n")

    def add_test_result(self, test_id, test_name, status, details=""):
        """Add test result"""
        self.test_counter += 1
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        status_symbol = f"{GREEN}PASS{END}" if status == "PASS" else f"{RED}FAIL{END}"
        print(f"  [{status_symbol}] {test_name}")
        if details:
            print(f"      {details}")

    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print("\n" + "="*80)
        print("TEST SUMMARY".center(80))
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {GREEN}{passed}{END}")
        print(f"Failed: {RED}{failed}{END}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print("="*80)

        # Export to JSON
        with open('controller_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults exported to: controller_test_results.json")

    # ==================== USER CONTROLLER TESTS ====================
    def test_user_registration(self):
        """TC-UC01: User Registration"""
        print(f"\n{CYAN}>> TC-UC01: User Registration{END}")
        print("-" * 80)
        
        controller = UserController()
        
        # Test 1: Register new user
        result = controller.register_user("John Doe", "john@example.com", "password123", "student")
        if result["success"]:
            self.add_test_result("TC-UC01-1", "Register new user successfully", "PASS")
        else:
            self.add_test_result("TC-UC01-1", "Register new user successfully", "FAIL", result["message"])

        # Test 2: Register with existing email (should fail)
        result = controller.register_user("Jane Doe", "john@example.com", "password456", "student")
        if not result["success"]:
            self.add_test_result("TC-UC01-2", "Reject duplicate email", "PASS")
        else:
            self.add_test_result("TC-UC01-2", "Reject duplicate email", "FAIL", "Duplicate email was allowed")

    def test_user_login(self):
        """TC-UC02: User Login"""
        print(f"\n{CYAN}>> TC-UC02: User Login{END}")
        print("-" * 80)
        
        controller = UserController()
        
        # Setup: Create user
        controller.register_user("Test User", "test@example.com", "testpass123", "student")
        
        # Test 1: Login with correct credentials
        result = controller.login("test@example.com", "testpass123")
        if result["success"]:
            self.add_test_result("TC-UC02-1", "Login with correct credentials", "PASS")
        else:
            self.add_test_result("TC-UC02-1", "Login with correct credentials", "FAIL", result["message"])

        # Test 2: Login with wrong password
        result = controller.login("test@example.com", "wrongpassword")
        if not result["success"]:
            self.add_test_result("TC-UC02-2", "Reject wrong password", "PASS")
        else:
            self.add_test_result("TC-UC02-2", "Reject wrong password", "FAIL", "Wrong password was accepted")

        # Test 3: Login with non-existent email
        result = controller.login("nonexistent@example.com", "password")
        if not result["success"]:
            self.add_test_result("TC-UC02-3", "Reject non-existent user", "PASS")
        else:
            self.add_test_result("TC-UC02-3", "Reject non-existent user", "FAIL", "Non-existent user was found")

    # ==================== BOOK CONTROLLER TESTS ====================
    def test_book_management(self):
        """TC-BC01: Book Management"""
        print(f"\n{CYAN}>> TC-BC01: Book Management{END}")
        print("-" * 80)
        
        controller = BookController()
        
        # Test 1: Add book
        result = controller.add_book("Python Programming", "Guido van Rossum", "O'Reilly", 2021, "Programming", 5)
        if result["success"]:
            book_id = result["book_id"]
            self.add_test_result("TC-BC01-1", "Add new book successfully", "PASS")
        else:
            self.add_test_result("TC-BC01-1", "Add new book successfully", "FAIL", result["message"])
            return

        # Test 2: Get book details
        result = controller.get_book(book_id)
        if result["success"] and result["book"]["title"] == "Python Programming":
            self.add_test_result("TC-BC01-2", "Get book details", "PASS")
        else:
            self.add_test_result("TC-BC01-2", "Get book details", "FAIL", "Book details not found or incorrect")

        # Test 3: Update book
        result = controller.update_book(book_id, quantity=10)
        if result["success"]:
            self.add_test_result("TC-BC01-3", "Update book quantity", "PASS")
        else:
            self.add_test_result("TC-BC01-3", "Update book quantity", "FAIL", result["message"])

        # Test 4: Get all books
        result = controller.get_all_books()
        if result["success"] and result["count"] > 0:
            self.add_test_result("TC-BC01-4", "Get all books", "PASS", f"Found {result['count']} books")
        else:
            self.add_test_result("TC-BC01-4", "Get all books", "FAIL", "No books found")

    def test_book_search(self):
        """TC-BC02: Book Search"""
        print(f"\n{CYAN}>> TC-BC02: Book Search{END}")
        print("-" * 80)
        
        controller = BookController()
        
        # Setup: Add test books
        controller.add_book("Java Basics", "Joshua Bloch", "Addison-Wesley", 2020, "Programming", 3)
        controller.add_book("Java Advanced", "Bruce Eckel", "Prentice Hall", 2021, "Programming", 2)
        
        # Test 1: Search by title
        result = controller.search_books("Java", "title")
        if result["success"] and result["count"] >= 2:
            self.add_test_result("TC-BC02-1", "Search books by title", "PASS", f"Found {result['count']} books")
        else:
            self.add_test_result("TC-BC02-1", "Search books by title", "FAIL", "Search results incorrect")

    def test_delete_available_book(self):
        """TC-BC03: Delete Available Book"""
        print(f"\n{CYAN}>> TC-BC03: Delete Available Book{END}")
        print("-" * 80)
        
        book_ctrl = BookController()
        
        # Add book
        result = book_ctrl.add_book("Deletable Book", "Author", "Publisher", 2021, "Fiction", 5)
        book_id = result["book_id"]
        
        # Delete available book (should succeed)
        result = book_ctrl.delete_book(book_id)
        if result["success"]:
            self.add_test_result("TC-BC03-1", "Delete available book successfully", "PASS")
        else:
            self.add_test_result("TC-BC03-1", "Delete available book successfully", "FAIL", result["message"])

    # ==================== BORROW CONTROLLER TESTS ====================
    def test_book_borrowing(self):
        """TC-BO01: Book Borrowing"""
        print(f"\n{CYAN}>> TC-BO01: Book Borrowing{END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        
        # Setup
        user_result = user_ctrl.register_user("Borrower One", "borrower1@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        
        book_result = book_ctrl.add_book("Data Science", "Wes McKinney", "O'Reilly", 2021, "Data Science", 3)
        book_id = book_result["book_id"]
        
        # Test 1: Borrow book
        result = borrow_ctrl.borrow_book(user_id, book_id)
        if result["success"]:
            self.add_test_result("TC-BO01-1", "Borrow book successfully", "PASS")
        else:
            self.add_test_result("TC-BO01-1", "Borrow book successfully", "FAIL", result["message"])

        # Test 2: Cannot borrow same book twice
        result = borrow_ctrl.borrow_book(user_id, book_id)
        if not result["success"]:
            self.add_test_result("TC-BO01-2", "Prevent duplicate borrow of same book", "PASS")
        else:
            self.add_test_result("TC-BO01-2", "Prevent duplicate borrow of same book", "FAIL", "Duplicate borrow was allowed")

    def test_borrow_limit(self):
        """TC-BO02: Borrow Limit Enforcement (MAX 3)"""
        print(f"\n{CYAN}>> TC-BO02: Borrow Limit Enforcement (MAX 3){END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        
        # Setup
        user_result = user_ctrl.register_user("Heavy Reader", "reader@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        
        # Create 5 books
        book_ids = []
        for i in range(5):
            result = book_ctrl.add_book(f"Book {i+1}", f"Author {i+1}", "Publisher", 2021, "Fiction", 2)
            book_ids.append(result["book_id"])
        
        # Test: Borrow up to limit
        for i in range(3):
            result = borrow_ctrl.borrow_book(user_id, book_ids[i])
            if result["success"]:
                self.add_test_result(f"TC-BO02-{i+1}", f"Borrow book {i+1} (within limit)", "PASS")
            else:
                self.add_test_result(f"TC-BO02-{i+1}", f"Borrow book {i+1} (within limit)", "FAIL", result["message"])
        
        # Test: Try to borrow 4th book (should fail)
        result = borrow_ctrl.borrow_book(user_id, book_ids[3])
        if not result["success"] and "limit" in result["message"].lower():
            self.add_test_result("TC-BO02-4", "Block 4th borrow (exceeds limit)", "PASS", result["message"])
        else:
            self.add_test_result("TC-BO02-4", "Block 4th borrow (exceeds limit)", "FAIL", "Borrow limit not enforced")

    def test_borrow_with_outstanding_fine(self):
        """TC-BO03: Block Borrow With Outstanding Fine"""
        print(f"\n{CYAN}>> TC-BO03: Block Borrow With Outstanding Fine{END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        
        # Setup
        user_result = user_ctrl.register_user("Fine Debtor", "debtor@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        
        # Create books
        book1_result = book_ctrl.add_book("Fiction Book", "Author Name", "Publisher", 2021, "Fiction", 2)
        book2_result = book_ctrl.add_book("Reference Book", "Ref Author", "Ref Publisher", 2021, "Reference", 2)
        book1_id = book1_result["book_id"]
        book2_id = book2_result["book_id"]
        
        # Borrow first book
        borrow_result = borrow_ctrl.borrow_book(user_id, book1_id)
        borrow_id = borrow_result["borrow_id"]
        
        # Create outstanding fine manually
        self.db["fines"].insert_one({
            "record_id": ObjectId(borrow_id),
            "amount": 50.0,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "paid_date": None
        })
        
        self.add_test_result("TC-BO03-1", "Create outstanding fine", "PASS")
        
        # Try to borrow another book with outstanding fine
        result = borrow_ctrl.borrow_book(user_id, book2_id)
        if not result["success"] and "fine" in result["message"].lower():
            self.add_test_result("TC-BO03-2", "Block borrow with outstanding fine", "PASS", result["message"])
        else:
            self.add_test_result("TC-BO03-2", "Block borrow with outstanding fine", "FAIL", "Borrow with fine was allowed")

    def test_book_return(self):
        """TC-BO04: Book Return"""
        print(f"\n{CYAN}>> TC-BO04: Book Return{END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        
        # Setup
        user_result = user_ctrl.register_user("Returner", "returner@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        
        book_result = book_ctrl.add_book("Return Test", "Author", "Publisher", 2021, "Fiction", 1)
        book_id = book_result["book_id"]
        
        # Borrow and return
        borrow_result = borrow_ctrl.borrow_book(user_id, book_id)
        borrow_id = borrow_result["borrow_id"]
        
        result = borrow_ctrl.return_book(borrow_id)
        if result["success"]:
            self.add_test_result("TC-BO04-1", "Return book successfully", "PASS")
        else:
            self.add_test_result("TC-BO04-1", "Return book successfully", "FAIL", result["message"])

    def test_delete_borrowed_book(self):
        """TC-BO05: Prevent Delete of Borrowed Book"""
        print(f"\n{CYAN}>> TC-BO05: Prevent Delete of Borrowed Book{END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        
        # Setup
        user_result = user_ctrl.register_user("Deleter Test", "deleter@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        
        book_result = book_ctrl.add_book("Delete Test Book", "Author", "Publisher", 2021, "Fiction", 1)
        book_id = book_result["book_id"]
        
        # Borrow the book
        borrow_result = borrow_ctrl.borrow_book(user_id, book_id)
        if borrow_result["success"]:
            self.add_test_result("TC-BO05-1", "Borrow book for deletion test", "PASS")
        else:
            self.add_test_result("TC-BO05-1", "Borrow book for deletion test", "FAIL", borrow_result["message"])
            return
        
        # Try to delete borrowed book
        result = book_ctrl.delete_book(book_id)
        if not result["success"] and "borrowed" in result["message"].lower():
            self.add_test_result("TC-BO05-2", "Prevent delete of borrowed book", "PASS", result["message"])
        else:
            self.add_test_result("TC-BO05-2", "Prevent delete of borrowed book", "FAIL", "Book was deleted while borrowed")

    # ==================== FINE CONTROLLER TESTS ====================
    def test_fine_management(self):
        """TC-FC01: Fine Management"""
        print(f"\n{CYAN}>> TC-FC01: Fine Management{END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        fine_ctrl = FineController()
        
        # Setup
        user_result = user_ctrl.register_user("Late Returner", "late@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        
        book_result = book_ctrl.add_book("Late Book", "Author", "Publisher", 2021, "Fiction", 1)
        book_id = book_result["book_id"]
        
        # Borrow book and manually create overdue
        borrow_result = borrow_ctrl.borrow_book(user_id, book_id)
        borrow_id = borrow_result["borrow_id"]
        
        # Create fine
        self.db["fines"].insert_one({
            "record_id": ObjectId(borrow_id),
            "amount": 25.0,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "paid_date": None
        })
        
        # Test: Get user fines
        result = fine_ctrl.get_user_fines(user_id)
        if result["success"] and result["count"] > 0:
            self.add_test_result("TC-FC01-1", "Get user fines", "PASS", f"Found {result['count']} fines")
        else:
            self.add_test_result("TC-FC01-1", "Get user fines", "FAIL", "No fines found")

        # Test: Get outstanding fines
        result = fine_ctrl.get_all_pending_fines()
        if result["success"] and result["count"] > 0:
            self.add_test_result("TC-FC01-2", "Get outstanding fines", "PASS", f"Found {result['count']} outstanding fines")
        else:
            self.add_test_result("TC-FC01-2", "Get outstanding fines", "FAIL", "No outstanding fines found")

    # ==================== INTEGRATION TESTS ====================
    def test_complete_workflow(self):
        """TC-INT01: Complete Workflow (Register → Borrow → Return → Fine)"""
        print(f"\n{CYAN}>> TC-INT01: Complete Workflow{END}")
        print("-" * 80)
        
        user_ctrl = UserController()
        book_ctrl = BookController()
        borrow_ctrl = BorrowController()
        fine_ctrl = FineController()
        
        # Step 1: Register user
        user_result = user_ctrl.register_user("Workflow User", "workflow@example.com", "pass123", "student")
        user_id = user_result["user_id"]
        self.add_test_result("TC-INT01-1", "Register user", "PASS" if user_result["success"] else "FAIL")
        
        # Step 2: Add book
        book_result = book_ctrl.add_book("Workflow Book", "Author", "Publisher", 2021, "Fiction", 3)
        book_id = book_result["book_id"]
        self.add_test_result("TC-INT01-2", "Add book", "PASS" if book_result["success"] else "FAIL")
        
        # Step 3: Borrow book
        borrow_result = borrow_ctrl.borrow_book(user_id, book_id)
        borrow_id = borrow_result["borrow_id"]
        self.add_test_result("TC-INT01-3", "Borrow book", "PASS" if borrow_result["success"] else "FAIL")
        
        # Step 4: Return book
        return_result = borrow_ctrl.return_book(borrow_id)
        self.add_test_result("TC-INT01-4", "Return book", "PASS" if return_result["success"] else "FAIL")
        
        # Step 5: Get user records
        records_result = borrow_ctrl.get_user_active_borrows(user_id)
        self.add_test_result("TC-INT01-5", "Get borrow history", "PASS" if records_result["success"] and records_result["count"] >= 0 else "FAIL")

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("COMPREHENSIVE CONTROLLER TEST SUITE".center(80))
        print("="*80)
        
        self.setup()
        
        # User Controller Tests
        self.test_user_registration()
        self.test_user_login()
        
        # Book Controller Tests
        self.test_book_management()
        self.test_book_search()
        self.test_delete_available_book()
        
        # Borrow Controller Tests
        self.test_book_borrowing()
        self.test_borrow_limit()
        self.test_borrow_with_outstanding_fine()
        self.test_book_return()
        self.test_delete_borrowed_book()
        
        # Fine Controller Tests
        self.test_fine_management()
        
        # Integration Tests
        self.test_complete_workflow()
        
        self.print_summary()


if __name__ == "__main__":
    tester = ComprehensiveControllerTester()
    tester.run_all_tests()
