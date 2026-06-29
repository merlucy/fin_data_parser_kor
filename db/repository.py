from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select

from db.connection import get_session
from db.models import (
    Company,
    CompanyFinancialsCalculated,
    DartApiCallLog,
    ScreeningRun,
    ScreeningRunCompany,
)


def get_today_call_count(today: date | None = None) -> int:
    today = today or datetime.now(timezone.utc).date()
    session = get_session()
    try:
        row = session.get(DartApiCallLog, today)
        return row.call_count if row else 0
    finally:
        session.close()


def increment_call_count(today: date | None = None) -> int:
    """Increment and return today's live-call counter. Uses a fresh row-level transaction."""
    today = today or datetime.now(timezone.utc).date()
    session = get_session()
    try:
        row = session.get(DartApiCallLog, today)
        if row is None:
            row = DartApiCallLog(call_date=today, call_count=0)
            session.add(row)
            session.flush()
        row.call_count += 1
        session.commit()
        return row.call_count
    finally:
        session.close()


def create_screening_run(
    sector: str | None,
    industry: str | None,
    fiscal_year_end: int,
    history_years: int = 5,
    fs_div_preference: str = "CFS",
) -> int:
    session = get_session()
    try:
        run = ScreeningRun(
            sector=sector,
            industry=industry,
            fiscal_year_end=fiscal_year_end,
            history_years=history_years,
            fs_div_preference=fs_div_preference,
            status="running",
        )
        session.add(run)
        session.commit()
        return run.id
    finally:
        session.close()


def add_companies_to_run(run_id: int, corp_codes: list[str]) -> None:
    session = get_session()
    try:
        for corp_code in corp_codes:
            session.merge(ScreeningRunCompany(screening_run_id=run_id, corp_code=corp_code))
        session.commit()
    finally:
        session.close()


def write_company_financials(run_id: int, rows: list[dict]) -> None:
    session = get_session()
    try:
        for row in rows:
            session.add(CompanyFinancialsCalculated(screening_run_id=run_id, **row))
        session.commit()
    finally:
        session.close()


def complete_screening_run(run_id: int, company_count: int, status: str = "completed", notes: str | None = None) -> None:
    session = get_session()
    try:
        run = session.get(ScreeningRun, run_id)
        run.status = status
        run.company_count = company_count
        run.completed_at = datetime.now(timezone.utc)
        if notes:
            run.notes = notes
        session.commit()
    finally:
        session.close()


def get_recent_runs(limit: int = 20) -> list[ScreeningRun]:
    session = get_session()
    try:
        stmt = select(ScreeningRun).order_by(ScreeningRun.requested_at.desc()).limit(limit)
        return list(session.execute(stmt).scalars().all())
    finally:
        session.close()


def get_run_financials(run_id: int) -> list[tuple[CompanyFinancialsCalculated, Company]]:
    session = get_session()
    try:
        stmt = (
            select(CompanyFinancialsCalculated, Company)
            .join(Company, Company.corp_code == CompanyFinancialsCalculated.corp_code)
            .where(CompanyFinancialsCalculated.screening_run_id == run_id)
        )
        return [(row[0], row[1]) for row in session.execute(stmt).all()]
    finally:
        session.close()
