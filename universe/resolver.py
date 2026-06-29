"""Resolve a sector/industry name to the list of corp_codes belonging to it."""

from __future__ import annotations

from sqlalchemy import select

from db.connection import get_session
from db.models import Company


def resolve_companies(industry: str) -> list[Company]:
    """Return active companies whose `industry` exactly matches the given name."""
    session = get_session()
    try:
        stmt = select(Company).where(Company.industry == industry, Company.is_active.is_(True))
        return list(session.execute(stmt).scalars().all())
    finally:
        session.close()


def search_industries(query: str) -> list[str]:
    """Return distinct industry names containing the given substring (case-insensitive)."""
    session = get_session()
    try:
        stmt = (
            select(Company.industry)
            .where(Company.industry.ilike(f"%{query}%"))
            .distinct()
            .order_by(Company.industry)
        )
        return [row[0] for row in session.execute(stmt).all() if row[0]]
    finally:
        session.close()


def list_industries() -> list[str]:
    session = get_session()
    try:
        stmt = select(Company.industry).distinct().order_by(Company.industry)
        return [row[0] for row in session.execute(stmt).all() if row[0]]
    finally:
        session.close()


def search_companies(name_query: str | None = None, industry: str | None = None) -> list[Company]:
    """Look up companies in the universe by name/ticker substring and/or exact industry match.

    Backs the company encyclopedia page: either filter narrows the result, both can be combined.
    """
    session = get_session()
    try:
        stmt = select(Company)
        if name_query:
            pattern = f"%{name_query}%"
            stmt = stmt.where(Company.corp_name.ilike(pattern) | Company.stock_code.ilike(pattern))
        if industry:
            stmt = stmt.where(Company.industry == industry)
        stmt = stmt.order_by(Company.corp_name)
        return list(session.execute(stmt).scalars().all())
    finally:
        session.close()
