"""
Library Management System - Flask Backend Server
Main application entry point with session-based authentication and book management
"""

from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime, timedelta
from bson import ObjectId

from src.controllers.auth_controller import AuthController
from src.controllers.book_controller import BookController
from src.controllers.borrow_controller import BorrowController
from src.controllers.fine_controller import FineController
from src.controllers.report_controller import ReportController
from src.models.database import get_db, init_database_with_seed

# Initialize Flask app
app = Flask(__name__, template_folder='src/templates')
CORS(app, supports_credentials=True)  # Enable CORS with credentials for sessions

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production (HTTPS only)
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
# Initialize database with seeding
print("\n" + "="*80)
print("INITIALIZING LIBRARY MANAGEMENT SYSTEM")
print("="*80)
init_database_with_seed()

# Initialize controllers
auth_controller = AuthController()
book_controller = BookController()
borrow_controller = BorrowController()
fine_controller = FineController()
report_controller = ReportController()
db = get_db()

print("\n[OK] Backend system ready!\n")


# ============================================================================
# SESSION & AUTHENTICATION HELPERS
# ============================================================================

def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({"success": False, "message": "Not authenticated"}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({"success": False, "message": "Not authenticated"}), 401
            
            user_role = session['user'].get('role', 'guest')
            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": f"Permission denied. Required role: {', '.join(allowed_roles)}"
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    return jsonify({
        "status": "ok",
        "message": "Library Management System API is running",
        "timestamp": datetime.now().isoformat(),
        "database": "MongoDB connected"
    })


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login endpoint - Authenticate user from MongoDB
    All users (admin, librarian, member) stored in database
    
    Request body:
    {
        "email": "admin@library.system|librarian@library.system|user@example.com",
        "password": "password"
    }
    
    Response on success:
    {
        "success": true,
        "user": {
            "_id": "user_id",
            "name": "User Name",
            "email": "email@example.com",
            "role": "admin|librarian|member"
        },
        "message": "Admin authenticated successfully"
    }
    
    Response on error:
    {
        "success": false,
        "message": "Invalid email or password"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required"}), 400
        
        # Authenticate from MongoDB (all users)
        result = auth_controller.login(email, password)
        
        if result['success']:
            # Store user in session
            session.permanent = True
            session['user'] = result['user']
            session['email'] = email
            session['role'] = result['user']['role']
            
            return jsonify({
                "success": True,
                "user": result['user'],
                "message": result['message']
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": result['message']
            }), 401
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout endpoint - Clear user session"""
    try:
        session.clear()
        return jsonify({
            "success": True,
            "message": "Logged out successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Logout error: {str(e)}"
        }), 500


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user info"""
    try:
        if 'user' in session:
            return jsonify({
                "success": True,
                "user": session['user']
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Not authenticated"
            }), 401
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register endpoint for new members
    Creates user in MongoDB with role 'member'
    
    Request body:
    {
        "name": "Full Name",
        "email": "email@example.com",
        "password": "password"
    }
    
    Response:
    {
        "success": true/false,
        "message": "Success/error message",
        "user_id": "id" (if successful)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({"success": False, "message": "Name, email, and password are required"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
        
        # Register user in MongoDB
        result = auth_controller.register(name, email, password)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result['message'],
                "user_id": result.get('user_id')
            }), 201
        else:
            return jsonify({
                "success": False,
                "message": result['message']
            }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


# ============================================================================
# USER MANAGEMENT ENDPOINTS (Admin Only)
# ============================================================================

@app.route('/api/users', methods=['GET'])
@login_required
@role_required(['admin'])
def get_all_users():
    """Get all registered users (Admin only)"""
    try:
        result = auth_controller.get_all_users()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/users/<user_id>', methods=['DELETE'])
@login_required
@role_required(['admin'])
def delete_user(user_id):
    """Delete a user (Admin only)"""
    try:
        result = auth_controller.delete_user(user_id)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


# ============================================================================
# BOOK ENDPOINTS - READ (All Users)
# ============================================================================

@app.route('/api/books', methods=['GET'])
def get_all_books():
    """Get all books"""
    try:
        result = book_controller.get_all_books()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/books/available', methods=['GET'])
def get_available_books():
    """Get all available books"""
    try:
        result = book_controller.get_available_books()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """Get single book by ID"""
    try:
        result = book_controller.get_book(book_id)
        return jsonify(result), 200 if result['success'] else 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/books/search', methods=['GET'])
def search_books():
    """Search books by title, author, category, or ISBN"""
    try:
        query = request.args.get('q', '').strip()
        search_by = request.args.get('by', 'title')
        
        if not query:
            return jsonify({
                "success": False,
                "message": "Search query is required"
            }), 400
        
        result = book_controller.search_books(query, search_by)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


# ============================================================================
# BOOK ENDPOINTS - WRITE (Admin/Librarian Only)
# ============================================================================

@app.route('/api/books', methods=['POST'])
@login_required
@role_required(['admin', 'librarian'])
def add_book():
    """Add new book (Admin/Librarian only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Required fields
        required = ['title', 'author', 'publisher', 'year', 'category', 'isbn', 'quantity']
        if not all(k in data for k in required):
            return jsonify({
                "success": False,
                "message": f"Missing required fields: {', '.join(required)}"
            }), 400
        
        user_role = session['user'].get('role')
        result = book_controller.add_book(
            user_role=user_role,
            title=data['title'],
            author=data['author'],
            publisher=data['publisher'],
            year=data['year'],
            category=data['category'],
            isbn=data['isbn'],
            quantity=int(data['quantity']),
            book_id=data.get('book_id')
        )
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Invalid data format: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/books/<book_id>', methods=['PUT'])
@login_required
@role_required(['admin', 'librarian'])
def update_book(book_id):
    """Update book (Admin/Librarian only)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        user_role = session['user'].get('role')
        result = book_controller.update_book(user_role, book_id, **data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/books/<book_id>', methods=['DELETE'])
@login_required
@role_required(['admin', 'librarian'])
def delete_book(book_id):
    """Delete book (Admin/Librarian only, cannot delete if borrowed)"""
    try:
        user_role = session['user'].get('role')
        result = book_controller.delete_book(user_role, book_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


# ============================================================================
# BORROW ENDPOINTS - Book Borrowing
# ============================================================================

@app.route('/api/borrows', methods=['POST'])
@login_required
def create_borrow():
    """Member borrows a book"""
    try:
        data = request.get_json()
        
        if not data or 'book_id' not in data:
            return jsonify({
                "success": False,
                "message": "book_id is required"
            }), 400
        
        user_role = session['user'].get('role')
        member_id = session['user'].get('_id')
        book_id = data['book_id']
        
        result = borrow_controller.borrow_book(user_role, member_id, book_id)
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/borrows/<borrow_id>/return', methods=['POST'])
@login_required
@role_required(['librarian', 'admin'])
def process_return(borrow_id):
    """Process book return (Librarian/Admin only)"""
    try:
        user_role = session['user'].get('role')
        result = borrow_controller.return_book(user_role, borrow_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/borrows/member/<member_id>', methods=['GET'])
@login_required
def get_member_borrows(member_id):
    """Get all borrow records for a member"""
    try:
        # Support "current" to get logged-in user's borrows
        if member_id == 'current':
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({"success": False, "message": "User not authenticated"}), 401
            member_id = user_id
        
        include_returned = request.args.get('include_returned', 'false').lower() == 'true'
        
        result = borrow_controller.get_member_borrows(member_id, include_returned)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/borrows', methods=['GET'])
@login_required
def get_all_borrows():
    """Get all borrow records (Librarian/Admin only)"""
    try:
        user_role = session['user'].get('role')
        include_returned = request.args.get('include_returned', 'false').lower() == 'true'
        
        result = borrow_controller.get_all_borrows(user_role, include_returned)
        
        status_code = 200 if result['success'] else 403
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/borrows/overdue', methods=['GET'])
@login_required
def get_overdue():
    """Get all overdue borrow records (Librarian/Admin only)"""
    try:
        user_role = session['user'].get('role')
        
        result = borrow_controller.get_overdue_borrows(user_role)
        
        status_code = 200 if result['success'] else 403
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/borrows/<borrow_id>', methods=['GET'])
@login_required
def get_borrow(borrow_id):
    """Get detailed information about a borrow record"""
    try:
        result = borrow_controller.get_borrow_details(borrow_id)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/fines/<fine_id>', methods=['GET'])
@login_required
def get_fine(fine_id):
    """Get fine details (member can view own, librarians/admins can view any)"""
    try:
        result = fine_controller.get_fine(fine_id)
        if not result.get('success'):
            return jsonify(result), 404

        # If member, ensure they own the fine via borrow record
        user_role = session['user'].get('role')
        if user_role == 'member':
            borrow_id = result['fine'].get('record_id')
            borrow_res = borrow_controller.get_borrow_details(borrow_id)
            if not borrow_res.get('success'):
                return jsonify({"success": False, "message": "Borrow record not found"}), 404
            borrower_id = borrow_res['borrow'].get('user_id')
            if borrower_id != session['user'].get('_id'):
                return jsonify({"success": False, "message": "Permission denied"}), 403

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/fines/member/<member_id>', methods=['GET'])
@login_required
def get_member_fines(member_id):
    """Get fines for a member (member sees own; librarian/admin can view any)"""
    try:
        user_role = session['user'].get('role')
        if user_role == 'member' and member_id != session['user'].get('_id'):
            return jsonify({"success": False, "message": "Permission denied"}), 403

        result = fine_controller.get_user_fines(member_id)
        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/fines/record/<record_id>', methods=['GET'])
@login_required
def get_fine_by_record(record_id):
    """Get fine by borrow record id (member can view own)"""
    try:
        result = fine_controller.get_fine_by_record(record_id)
        if not result.get('success'):
            return jsonify(result), 404

        user_role = session['user'].get('role')
        if user_role == 'member':
            borrow_res = borrow_controller.get_borrow_details(record_id)
            if not borrow_res.get('success'):
                return jsonify({"success": False, "message": "Borrow record not found"}), 404
            if borrow_res['borrow'].get('member_id') != session['user'].get('_id'):
                return jsonify({"success": False, "message": "Permission denied"}), 403

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/fines', methods=['GET'])
@login_required
@role_required(['librarian', 'admin'])
def get_all_fines():
    """Get all fines (librarian/admin)"""
    try:
        result = fine_controller.get_all_fines()
        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/fines/pending', methods=['GET'])
@login_required
@role_required(['librarian', 'admin'])
def get_pending_fines():
    """Get all pending fines (librarian/admin)"""
    try:
        result = fine_controller.get_all_pending_fines()
        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/fines/<fine_id>/pay', methods=['POST'])
@login_required
@role_required(['librarian', 'admin'])
def pay_fine(fine_id):
    """Pay a fine (librarian/admin records payment)"""
    try:
        data = request.get_json() or {}
        amount = data.get('amount')
        method = data.get('method', 'cash')

        if amount is None:
            return jsonify({"success": False, "message": "Amount is required"}), 400

        result = fine_controller.pay_fine(fine_id, amount, method)
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/reports/summary', methods=['GET'])
@login_required
@role_required(['librarian', 'admin'])
def get_report_summary():
    """Get aggregated report summary for dashboards"""
    try:
        date_filter = request.args.get('date_filter')
        date_value = request.args.get('date')
        result = report_controller.get_summary(date_filter, date_value)
        status = 200 if result.get('success') else 400
        return jsonify(result), status
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


# ============================================================================
# DASHBOARD STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/dashboard/admin-stats', methods=['GET'])
@login_required
@role_required(['admin'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        result = book_controller.get_dashboard_stats()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/api/reports/category', methods=['GET'])
@login_required
@role_required(['admin', 'librarian'])
def get_category_report():
    """Get category report with book counts from database"""
    try:
        result = book_controller.get_category_report()
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500


@app.route('/', methods=['GET'])
def index():
    """Redirect to login page"""
    return render_template('Login.html')


# ============================================================================
# AUTHENTICATION PAGE ROUTES
# ============================================================================

@app.route('/login', methods=['GET'])
def page_login():
    """Login page"""
    return render_template('Login.html')


@app.route('/Login.html', methods=['GET'])
def page_login_alias():
    """Login page alias (handle case-insensitive redirect)"""
    return render_template('Login.html')


@app.route('/register', methods=['GET'])
def page_register():
    """Register page"""
    return render_template('Register.html')


@app.route('/Register.html', methods=['GET'])
def page_register_alias():
    """Register page alias (handle case-insensitive redirect)"""
    return render_template('Register.html')


@app.route('/forgot-password', methods=['GET'])
def page_forgot_password():
    """Forgot password page"""
    return render_template('ForgotPassword.html')


@app.route('/ForgotPassword.html', methods=['GET'])
def page_forgot_password_alias():
    """Forgot password page alias (handle case-insensitive redirect)"""
    return render_template('ForgotPassword.html')@app.route('/guest', methods=['GET'])
def page_guest():
    """Guest page with all available books"""
    try:
        available_books = book_controller.get_available_books()
        if available_books['success']:
            books = available_books['books']
        else:
            books = []
    except:
        books = []
    
    return render_template('Guest/Guest.html', books=books)


# ============================================================================
# LOGOUT & DASHBOARD ROUTES
# ============================================================================

@app.route('/logout', methods=['GET', 'POST'])
def logout_page():
    """Logout page - Clear session and redirect to login"""
    session.clear()
    return render_template('Login.html')


# ============================================================================
# ROLE-BASED DASHBOARD ROUTES
# ============================================================================

@app.route('/admin/dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    """Admin dashboard - Main overview page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    return render_template('Admin/AdminOverview.html', user=session['user'])


@app.route('/librarian/dashboard', methods=['GET'])
@login_required
def librarian_dashboard():
    """Librarian dashboard - Main overview page with statistics"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    try:
        from datetime import date
        
        # Get today's statistics
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        # Count borrowing books today (newly borrowed)
        borrowing_today = db['borrow_records'].count_documents({
            'borrow_date': {
                '$gte': today,
                '$lt': tomorrow
            },
            'is_active': True
        })
        
        # Count returning books today (returned today)
        returning_today = db['borrow_records'].count_documents({
            'return_date': {
                '$gte': today,
                '$lt': tomorrow
            },
            'is_active': True
        })
        
        # Count overdue books (not returned and due date has passed)
        overdue_books = db['borrow_records'].count_documents({
            'return_date': None,
            'due_date': {'$lt': today},
            'is_active': True
        })
        
        dashboard_stats = {
            'borrowing_today': borrowing_today,
            'returning_today': returning_today,
            'overdue_books': overdue_books
        }
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        dashboard_stats = {
            'borrowing_today': 0,
            'returning_today': 0,
            'overdue_books': 0
        }
    
    return render_template('Librarian/LibrarianOverview.html', 
                         user=session['user'],
                         stats=dashboard_stats)


@app.route('/member/dashboard', methods=['GET'])
@login_required
def member_dashboard():
    """Member dashboard - Main overview page with recommended books"""
    if session['user'].get('role') != 'member':
        return "Access Denied", 403
    
    # Fetch random/recommended books for the dashboard
    try:
        all_books = book_controller.get_all_books()
        if all_books['success']:
            # Get first 4 books as recommendations (or implement recommendation logic)
            recommended_books = all_books['books'][:4]
        else:
            recommended_books = []
    except:
        recommended_books = []
    
    return render_template('Member/MemberOverview.html', 
                         user=session['user'],
                         recommended_books=recommended_books)


# ============================================================================
# ADMIN PAGES
# ============================================================================

@app.route('/admin/manage-books', methods=['GET'])
@login_required
def admin_manage_books():
    """Admin book management page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    # Fetch all books for initial display
    try:
        all_books = book_controller.get_all_books()
        books = all_books['books'] if all_books['success'] else []
    except:
        books = []
    
    return render_template('Admin/AdminManageBook.html', user=session['user'], books=books)


@app.route('/admin/manage-users', methods=['GET'])
@login_required
def admin_manage_users():
    """Admin user management page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    return render_template('Admin/AdminManageUser.html', user=session['user'])


@app.route('/admin/reports/borrow-return', methods=['GET'])
@login_required
def admin_reports_borrow_return():
    """Admin borrow/return report page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    return render_template('Admin/AdminReportBorrowandReturn.html', user=session['user'])


@app.route('/admin/reports/category', methods=['GET'])
@login_required
def admin_reports_category():
    """Admin category report page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    return render_template('Admin/AdminReportCategory.html', user=session['user'])


@app.route('/admin/reports/top-books', methods=['GET'])
@login_required
def admin_reports_top_books():
    """Admin top books report page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    return render_template('Admin/AdminReportTopBook.html', user=session['user'])


@app.route('/admin/reports/late', methods=['GET'])
@login_required
def admin_reports_late():
    """Admin late books report page"""
    if session['user'].get('role') != 'admin':
        return "Access Denied", 403
    
    return render_template('Admin/AdminReportLate.html', user=session['user'])


# ============================================================================
# LIBRARIAN PAGES
# ============================================================================

@app.route('/librarian/borrowing-books', methods=['GET'])
@login_required
def librarian_borrowing_books():
    """Librarian borrowing books management page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    return render_template('Librarian/LibrarianBorrowingBooks.html', user=session['user'])


@app.route('/librarian/returning-books', methods=['GET'])
@login_required
def librarian_returning_books():
    """Librarian returning books management page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    return render_template('Librarian/LibrarianReturningBooks.html', user=session['user'])


@app.route('/librarian/manage-books', methods=['GET'])
@login_required
def librarian_manage_books():
    """Librarian book management page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    # Fetch all books for initial display
    try:
        all_books = book_controller.get_all_books()
        books = all_books['books'] if all_books['success'] else []
    except:
        books = []
    
    return render_template('Librarian/LibrarianManageBooks.html', user=session['user'], books=books)


@app.route('/librarian/reports/borrow-return', methods=['GET'])
@login_required
def librarian_reports_borrow_return():
    """Librarian borrow/return report page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    return render_template('Librarian/LibrarianReportBorrowandReturn.html', user=session['user'])


@app.route('/librarian/reports/category', methods=['GET'])
@login_required
def librarian_reports_category():
    """Librarian category report page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    return render_template('Librarian/LibrarianReportCategory.html', user=session['user'])


@app.route('/librarian/reports/top-books', methods=['GET'])
@login_required
def librarian_reports_top_books():
    """Librarian top books report page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    return render_template('Librarian/LibrarianReportTopBooks.html', user=session['user'])


@app.route('/librarian/reports/late', methods=['GET'])
@login_required
def librarian_reports_late():
    """Librarian late books report page"""
    if session['user'].get('role') != 'librarian':
        return "Access Denied", 403
    
    return render_template('Librarian/LibrarianReportLate.html', user=session['user'])


# ============================================================================
# MEMBER PAGES
# ============================================================================

@app.route('/member/browse-library', methods=['GET'])
@login_required
def member_browse_library():
    """Member browse library page with all available books"""
    if session['user'].get('role') != 'member':
        return "Access Denied", 403
    
    # Fetch all available books
    try:
        available_books = book_controller.get_available_books()
        if available_books['success']:
            books = available_books['books']
        else:
            books = []
    except:
        books = []
    
    return render_template('Member/MemberBrowseLibrary.html', 
                         user=session['user'],
                         books=books)


@app.route('/member/my-books', methods=['GET'])
@login_required
def member_my_books():
    """Member my books page with borrowed and history books"""
    if session['user'].get('role') != 'member':
        return "Access Denied", 403
    
    # Fetch user's borrow records
    try:
        user_id = session['user'].get('_id')
        # Get active (not returned) borrow records
        active_borrows = borrow_controller.get_member_borrows(user_id, include_returned=False)
        if active_borrows['success']:
            borrowing_books = active_borrows['borrows']
        else:
            borrowing_books = []
        
        # Get all borrow history (including returned)
        all_borrows = borrow_controller.get_member_borrows(user_id, include_returned=True)
        if all_borrows['success']:
            borrow_history = all_borrows['borrows']
        else:
            borrow_history = []
    except:
        borrowing_books = []
        borrow_history = []
    
    return render_template('Member/MemberMyBook.html', 
                         user=session['user'],
                         borrowing_books=borrowing_books,
                         borrow_history=borrow_history)


@app.route('/member/profile', methods=['GET'])
@login_required
def member_profile():
    """Member profile page with user details and most viewed books"""
    if session['user'].get('role') != 'member':
        return "Access Denied", 403
    
    # Fetch user's most viewed books (from borrow history)
    try:
        user_id = session['user'].get('_id')
        all_borrows = borrow_controller.get_member_borrows(user_id, include_returned=True)
        if all_borrows['success']:
            borrow_history = all_borrows['borrows']
            # Extract unique books from history (most recent first)
            seen_books = set()
            viewed_books = []
            for borrow in borrow_history:
                book_id = borrow.get('book_id')
                if book_id and book_id not in seen_books:
                    seen_books.add(book_id)
                    viewed_books.append(borrow)
                    if len(viewed_books) >= 4:
                        break
        else:
            viewed_books = []
    except:
        viewed_books = []
    
    return render_template('Member/MemberProfile.html', 
                         user=session['user'],
                         viewed_books=viewed_books)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

# ============================================================================
# PROFILE API ENDPOINTS
# ============================================================================

@app.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    """Get current user's profile data (API endpoint for frontend)"""
    try:
        user = session.get('user')
        if not user:
            return jsonify({"success": False, "message": "User not authenticated"}), 401
        
        return jsonify({
            "success": True,
            "profile": {
                "_id": user.get('_id'),
                "name": user.get('name', 'User Name'),
                "email": user.get('email', ''),
                "role": user.get('role', ''),
                "phone": user.get('phone', ''),
                "address": user.get('address', ''),
                "gender": user.get('gender', ''),
                "dob": user.get('dob', '')
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    """Update current user's profile (API endpoint for frontend)"""
    try:
        user_id = session['user'].get('_id')
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Update user in database
        from src.models.database import get_db
        db = get_db()
        
        # Build update data - only allow certain fields
        update_data = {}
        allowed_fields = ['name', 'phone', 'address', 'gender', 'dob']
        
        for field in allowed_fields:
            if field in data and data[field]:
                # Validate gender field
                if field == 'gender':
                    if data[field] not in ['Male', 'Female']:
                        return jsonify({
                            "success": False,
                            "message": "Gender must be either 'Male' or 'Female'"
                        }), 400
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({"success": False, "message": "No valid fields to update"}), 400
        
        result = db['users'].update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Update session with new data
        for field, value in update_data.items():
            session['user'][field] = value
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "profile": {
                "_id": user_id,
                "name": session['user'].get('name'),
                "email": session['user'].get('email'),
                "phone": session['user'].get('phone', ''),
                "address": session['user'].get('address', ''),
                "gender": session['user'].get('gender', ''),
                "dob": session['user'].get('dob', '')
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "message": "Internal server error"
    }), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("""
================================================================================
LIBRARY MANAGEMENT SYSTEM - BACKEND SERVER
================================================================================

[*] Server starting on: http://localhost:5000
[*] API Base URL: http://localhost:5000/api

Available Endpoints:
  [+] GET  /api/health                Health check
  [+] POST /api/auth/login            User login
  [+] POST /api/auth/register         User registration
  
  BOOKS:
  [+] GET  /api/books                 Get all books
  [+] GET  /api/books/available       Get available books
  [+] GET  /api/books/<id>            Get book details
  [+] GET  /api/books/search          Search books
  [+] POST /api/books                 Add book (Admin/Librarian)
  [+] PUT  /api/books/<id>            Update book (Admin/Librarian)
  [+] DELETE /api/books/<id>          Delete book (Admin/Librarian)
  
  BORROWS:
  [+] POST /api/borrows               Borrow book (Member)
  [+] POST /api/borrows/<id>/return   Return book (Librarian/Admin)
  [+] GET  /api/borrows               Get all borrows (Librarian/Admin)
  [+] GET  /api/borrows/member/<id>   Get member's borrows
  [+] GET  /api/borrows/overdue       Get overdue borrows (Librarian/Admin)
  [+] GET  /api/borrows/<id>          Get borrow details

Keep this terminal open while using the system!
    """)
    
    app.run(
        host='localhost',
        port=5000,
        debug=True,
        use_reloader=True
    )
