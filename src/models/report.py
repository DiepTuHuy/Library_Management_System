from datetime import datetime
from bson.objectid import ObjectId

"""Report model: implements aggregation pipelines for books, borrows, and fines.
All methods are read-only and return aggregated dictionaries.
"""


def _parse_date_filter(date_filter, date_value=None):
    """Return start and end datetimes for filters.
    date_filter: 'daily' or 'monthly' or None
    date_value: ISO date string or None (defaults to today)
    """
    now = datetime.utcnow()
    if date_value:
        try:
            date = datetime.fromisoformat(date_value)
        except Exception:
            date = now
    else:
        date = now

    if date_filter == 'daily':
        start = datetime(date.year, date.month, date.day)
        end = start.replace(hour=23, minute=59, second=59)
    elif date_filter == 'monthly':
        start = datetime(date.year, date.month, 1)
        # naive month end: next month start - 1s
        if date.month == 12:
            next_month = datetime(date.year + 1, 1, 1)
        else:
            next_month = datetime(date.year, date.month + 1, 1)
        end = next_month
    else:
        start, end = None, None

    return start, end


class ReportModel:
    @staticmethod
    def books_summary(db, date_filter=None, date_value=None):
        """Return counts: total_books, total_available (sum of available_quantity)
        Optionally can filter by date when books were added if provided (not required).
        """
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_books": {"$sum": "$quantity"},
                    "total_available": {"$sum": "$available_quantity"},
                    "distinct_titles": {"$sum": 1}
                }
            }
        ]
        res = list(db["books"].aggregate(pipeline))
        if res:
            r = res[0]
            return {
                "total_books": int(r.get("total_books", 0)),
                "total_available": int(r.get("total_available", 0)),
                "distinct_titles": int(r.get("distinct_titles", 0)),
            }
        return {"total_books": 0, "total_available": 0, "distinct_titles": 0}

    @staticmethod
    def borrows_summary(db, date_filter=None, date_value=None):
        """Return counts: total_borrowed (historical), active_borrows, overdue_borrows
        Supports date filters (daily/monthly) applying to borrow_date
        """
        start, end = _parse_date_filter(date_filter, date_value)

        match_date = {}
        if start and end:
            match_date = {"borrow_date": {"$gte": start, "$lt": end}}

        # total borrowed in range or overall
        total_pipeline = []
        if match_date:
            total_pipeline.append({"$match": match_date})
        total_pipeline.append({"$count": "total_borrowed"})
        total_res = list(db["borrow_records"].aggregate(total_pipeline))
        total_borrowed = int(total_res[0].get("total_borrowed", 0)) if total_res else 0

        # active borrows (return_date == None)
        active_match = {"return_date": None, "is_active": True}
        if match_date:
            # if filtering by date, consider borrows created in range that are still active
            active_match.update(match_date)
        active_count = db["borrow_records"].count_documents(active_match)

        # overdue: due_date < now and return_date == None
        now = datetime.utcnow()
        overdue_match = {"due_date": {"$lt": now}, "return_date": None, "is_active": True}
        overdue_count = db["borrow_records"].count_documents(overdue_match)

        return {
            "total_borrowed": int(total_borrowed),
            "active_borrows": int(active_count),
            "overdue_borrows": int(overdue_count),
        }

    @staticmethod
    def fines_summary(db, date_filter=None, date_value=None):
        """Return totals: total_fines_issued, total_unpaid_fines
        Date filters apply to fine.created_at
        """
        start, end = _parse_date_filter(date_filter, date_value)
        match = {}
        if start and end:
            match["created_at"] = {"$gte": start, "$lt": end}

        pipeline = []
        if match:
            pipeline.append({"$match": match})

        pipeline.append({
            "$group": {
                "_id": None,
                "total_fines_issued": {"$sum": "$amount"},
                "total_unpaid_fines": {
                    "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, "$amount", 0]}
                }
            }
        })

        res = list(db["fines"].aggregate(pipeline))
        if res:
            r = res[0]
            return {
                "total_fines_issued": float(r.get("total_fines_issued", 0)),
                "total_unpaid_fines": float(r.get("total_unpaid_fines", 0)),
            }
        return {"total_fines_issued": 0.0, "total_unpaid_fines": 0.0}


    def monthly_series(db, months=6):
        """Return last `months` months of borrow and return counts.
        Returns list of dicts: {month: 'YYYY-MM', borrows: int, returns: int}
        """
        from datetime import datetime
        series = []
        now = datetime.utcnow()
        # Build months from oldest to newest
        for i in range(months-1, -1, -1):
            # compute first day of target month
            year = now.year
            month = now.month - i
            while month <= 0:
                month += 12
                year -= 1

            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year+1, 1, 1)
            else:
                end = datetime(year, month+1, 1)

            borrows_count = db["borrow_records"].count_documents({ # type: ignore
                "borrow_date": {"$gte": start, "$lt": end}
            })
            returns_count = db["borrow_records"].count_documents({ # type: ignore
                "return_date": {"$gte": start, "$lt": end}
            })

            series.append({
                "month": f"{year}-{str(month).zfill(2)}",
                "borrows": int(borrows_count),
                "returns": int(returns_count),
            })

        return series