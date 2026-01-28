from ..models.database import get_db
from ..models.borrow_record import BorrowRecord
from ..models.fine import Fine
from ..models.payment import Payment
from ..models.user import User
from ..models.book import Book
from datetime import datetime, timedelta
from ..models.report import ReportModel
from ..services.report_service import ReportService
from ..models.database import get_db


class ReportController:
    """Controller for generating reports"""

    def __init__(self):
        self.db = get_db()
        self.report_service = ReportService(self.db)

    def get_borrow_statistics(self):
        """Get borrowing statistics"""
        try:
            total_borrows = self.db["borrow_records"].count_documents({})
            active_borrows = self.db["borrow_records"].count_documents(
                {"return_date": None}
            )
            completed_borrows = self.db["borrow_records"].count_documents(
                {"return_date": {"$ne": None}}
            )
            overdue_borrows = self.db["borrow_records"].count_documents({
                "due_date": {"$lt": datetime.utcnow()},
                "return_date": None,
            })

            return {
                "success": True,
                "statistics": {
                    "total_borrows": total_borrows,
                    "active_borrows": active_borrows,
                    "completed_borrows": completed_borrows,
                    "overdue_borrows": overdue_borrows,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_fine_statistics(self):
        """Get fine statistics"""
        try:
            total_fines = self.db["fines"].count_documents({})
            pending_fines = self.db["fines"].count_documents({"status": "pending"})
            paid_fines = self.db["fines"].count_documents({"status": "paid"})

            # Total amount
            pending_amount = sum(
                [f["amount"] for f in self.db["fines"].find({"status": "pending"})]
            )
            paid_amount = sum(
                [f["amount"] for f in self.db["fines"].find({"status": "paid"})]
            )

            return {
                "success": True,
                "statistics": {
                    "total_fines": total_fines,
                    "pending_fines": pending_fines,
                    "paid_fines": paid_fines,
                    "pending_amount": pending_amount,
                    "paid_amount": paid_amount,
                    "total_amount": pending_amount + paid_amount,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user_statistics(self):
        """Get user statistics"""
        try:
            total_users = self.db["users"].count_documents({"is_active": True})
            admins = self.db["users"].count_documents(
                {"role": "admin", "is_active": True}
            )
            librarians = self.db["users"].count_documents(
                {"role": "librarian", "is_active": True}
            )
            members = self.db["users"].count_documents(
                {"role": "member", "is_active": True}
            )

            return {
                "success": True,
                "statistics": {
                    "total_users": total_users,
                    "admins": admins,
                    "librarians": librarians,
                    "members": members,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_book_statistics(self):
        """Get book statistics"""
        try:
            total_books = self.db["books"].count_documents({"is_active": True})
            total_copies = sum(
                [
                    b["quantity"]
                    for b in self.db["books"].find({"is_active": True})
                ]
            )
            available_copies = sum(
                [
                    b["available"]
                    for b in self.db["books"].find({"is_active": True})
                ]
            )
            borrowed_copies = total_copies - available_copies

            return {
                "success": True,
                "statistics": {
                    "total_books": total_books,
                    "total_copies": total_copies,
                    "available_copies": available_copies,
                    "borrowed_copies": borrowed_copies,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_top_borrowed_books(self, limit=10):
        """Get top borrowed books"""
        try:
            pipeline = [
                {"$group": {"_id": "$book_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit},
            ]
            results = list(self.db["borrow_records"].aggregate(pipeline))

            books_data = []
            for result in results:
                book = Book.get_by_id(self.db, str(result["_id"]))
                if book:
                    books_data.append({
                        "book_id": str(book._id),
                        "title": book.title,
                        "author": book.author,
                        "borrow_count": result["count"],
                    })

            return {
                "success": True,
                "books": books_data,
                "count": len(books_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "books": [], "count": 0}

    def get_top_members(self, limit=10):
        """Get top borrowing members"""
        try:
            pipeline = [
                {"$match": {"return_date": None}},
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit},
            ]
            results = list(self.db["borrow_records"].aggregate(pipeline))

            members_data = []
            for result in results:
                user = User.get_by_id(self.db, str(result["_id"]))
                if user:
                    members_data.append({
                        "user_id": str(user._id),
                        "name": user.name,
                        "email": user.email,
                        "active_borrows": result["count"],
                    })

            return {
                "success": True,
                "members": members_data,
                "count": len(members_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "members": [], "count": 0}

    def get_monthly_revenue(self, year, month):
        """Get monthly fine revenue"""
        try:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            payments = Payment.get_by_date_range(self.db, start_date, end_date)
            total_revenue = sum([p.amount for p in payments])

            return {
                "success": True,
                "year": year,
                "month": month,
                "total_revenue": total_revenue,
                "payment_count": len(payments),
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_overall_report(self):
        """Get overall system report"""
        try:
            borrow_stats = self.get_borrow_statistics()["statistics"]
            fine_stats = self.get_fine_statistics()["statistics"]
            user_stats = self.get_user_statistics()["statistics"]
            book_stats = self.get_book_statistics()["statistics"]

            return {
                "success": True,
                "report": {
                    "borrow_statistics": borrow_stats,
                    "fine_statistics": fine_stats,
                    "user_statistics": user_stats,
                    "book_statistics": book_stats,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_summary(self, date_filter=None, date_value=None):
        """Return normalized summary for dashboards. Supports date_filter: daily|monthly"""
        try:
            data = self.report_service.summary(date_filter, date_value)
            # include monthly series for charts
            series = self.report_service.monthly_series(6)
            data['series'] = series
            return {"success": True, "report": data}
        except Exception as e:
            return {"success": False, "message": str(e)}
