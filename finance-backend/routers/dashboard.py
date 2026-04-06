from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from middleware.access_control import require_role
from models.user import User, UserRole
from services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

analyst_or_admin = require_role(UserRole.analyst, UserRole.admin)


@router.get(
    "/summary",
    summary="Financial summary",
    description="Returns total income, total expenses, and net balance. Analyst and Admin only.",
)
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_admin),
):
    return dashboard_service.get_summary(db)


@router.get(
    "/categories",
    summary="Category breakdown",
    description="Returns totals and counts grouped by category and type. Analyst and Admin only.",
)
def categories(
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_admin),
):
    return dashboard_service.get_category_totals(db)


@router.get(
    "/recent",
    summary="Recent activity",
    description="Returns the most recent transactions. Limit between 1 and 50. Analyst and Admin only.",
)
def recent(
    limit: int = Query(10, ge=1, le=50, description="Number of recent transactions to return"),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_admin),
):
    return dashboard_service.get_recent_activity(db, limit)


@router.get(
    "/trends/monthly",
    summary="Monthly trends",
    description="Returns income, expense, and net per month for a given year. Defaults to current year.",
)
def monthly_trends(
    year: int | None = Query(None, description="Year to fetch trends for (defaults to current year)"),
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_admin),
):
    return dashboard_service.get_monthly_trends(db, year)


@router.get(
    "/trends/weekly",
    summary="Weekly trends",
    description="Returns income, expense, and net grouped by ISO week. Analyst and Admin only.",
)
def weekly_trends(
    db: Session = Depends(get_db),
    _: User = Depends(analyst_or_admin),
):
    return dashboard_service.get_weekly_trends(db)
