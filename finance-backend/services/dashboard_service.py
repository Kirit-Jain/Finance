from datetime import datetime, timezone

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from models.transaction import Transaction, TransactionType

def get_summary(db: Session) -> dict:
    """Total income, total expenses, and net balance."""
    rows = (
        db.query(Transaction.type, func.sum(Transaction.amount).label("total"))
        .filter(Transaction.is_deleted == False)
        .group_by(Transaction.type)
        .all()
    )

    totals = {row.type: row.total for row in rows}
    income = totals.get(TransactionType.income, 0.0)
    expense = totals.get(TransactionType.expense, 0.0)

    return {
        "total_income": round(income, 2),
        "total_expenses": round(expense, 2),
        "net_balance": round(income - expense, 2),
    }

def get_category_totals(db: Session) -> list[dict]:
    """Amount totals grouped by category and transaction type."""
    rows = (
        db.query(Transaction.category, Transaction.type, func.sum(Transaction.amount).label("total"), func.count(Transaction.id).label("count"))
        .filter(Transaction.is_deleted == False)
        .group_by(Transaction.category, Transaction.type)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return [
        {
            "category": row.category,
            "type": row.type,
            "total": round(row.total, 2),
            "count": row.count,
        }
        for row in rows
    ]

def get_recent_activity(db: Session, limit: int = 10) -> list[dict]:
    """Most recent transactions"""
    rows =(
        db.query(Transaction)
        .filter(Transaction.is_deleted == False)
        .order_by(Transaction.date.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": row.id,
            "amount": row.amount,
            "type": row.type,
            "category": row.category,
            "date": row.date,
            "note": row.note,
        }
        for row in rows
    ]

def get_monthly_trends(db: Session, year: int | None = None) -> list[dict]:
    """
    Income and expense totals broken down by month.
    Defaults to the current year.
    """

    target_year = year or datetime.now(timezone.utc).year

    rows = (
        db.query(
            extract("month", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.is_deleted == False,
            extract("year", Transaction.date) == target_year,
        )
        .group_by("month", Transaction.type)
        .order_by("month")
        .all()
    )

    trends: dict[int, dict] = {}
    for row in rows:
        m = int(row.month)
        if m not in trends:
            trends[m] = {"month": m, "year": target_year, "income": 0.0, "expense": 0.0}
        trends[m][row.type.value] = round(row.total, 2)

    result = []
    for entry in sorted(trends.values(), key =lambda x: x["month"]):
        entry["net"] = round(entry["income"] - entry["expense"], 2)
        result.append(entry)

    return result

def get_weekly_trends(db: Session) -> list[dict]:
    """
    Income and expense totals for the last 8 weeks.
    Uses ISO week numbers.
    """
    rows = (
        db.query(
            extract("week", Transaction.date).label("week"),
            extract("year", Transaction.date).label("year"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(Transaction.is_deleted == False)
        .group_by("week", "year", Transaction.type)
        .order_by("year", "week")
        .limit(16)  # up to 8 weeks * 2 types
        .all()
    )

    trends: dict[tuple, dict] = {}
    for row in rows:
        key = (int(row.year), int(row.week))
        if key not in trends:
            trends[key] = {"year": int(row.year), "week": int(row.week), "income": 0.0, "expense": 0.0}
        trends[key][row.type.value] = round(row.total, 2)

    result = []
    for entry in sorted(trends.values(), key=lambda x: (x["year"], x["week"])):
        entry["net"] = round(entry["income"] - entry["expense"], 2)
        result.append(entry)

    return result
  