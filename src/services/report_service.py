from ..models.report import ReportModel

class ReportService:
    def __init__(self, db):
        self.db = db

    def summary(self, date_filter=None, date_value=None):
        """Return combined report summary normalized for frontend.
        date_filter: 'daily'|'monthly'|None
        date_value: ISO date string optionally provided
        """
        books = ReportModel.books_summary(self.db, date_filter, date_value)
        borrows = ReportModel.borrows_summary(self.db, date_filter, date_value)
        fines = ReportModel.fines_summary(self.db, date_filter, date_value)

        # Derived values
        total_books = books.get('total_books', 0)
        total_available = books.get('total_available', 0)
        total_borrowed = borrows.get('total_borrowed', 0)
        active_borrows = borrows.get('active_borrows', 0)
        overdue_borrows = borrows.get('overdue_borrows', 0)

        total_fines_issued = fines.get('total_fines_issued', 0.0)
        total_unpaid_fines = fines.get('total_unpaid_fines', 0.0)

        return {
            'books': {
                'total_books': total_books,
                'total_available': total_available,
                'total_borrowed': total_borrowed,
            },
            'borrows': {
                'active_borrows': active_borrows,
                'overdue_borrows': overdue_borrows,
            },
            'fines': {
                'total_fines_issued': total_fines_issued,
                'total_unpaid_fines': total_unpaid_fines,
            }
        }
    def monthly_series(self, months=6):
        from ..models.report import monthly_series as _monthly_series
        return _monthly_series(self.db, months)