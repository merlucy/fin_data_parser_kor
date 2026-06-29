"""Build the companies table by joining KIND's industry listing with DART corp_codes by ticker."""

from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from dart_client.corp_code import get_listed_corp_codes
from db.connection import get_session
from db.models import Company
from krx.sector_fetcher import fetch_listed_companies

logger = logging.getLogger(__name__)


def build_universe() -> int:
    """Refresh the companies table. Returns the number of companies upserted."""
    corp_entries = get_listed_corp_codes()
    corp_by_stock_code = {e.stock_code: e for e in corp_entries if e.stock_code}

    listings = fetch_listed_companies()

    rows = []
    unmatched = 0
    for listing in listings:
        corp = corp_by_stock_code.get(listing.stock_code)
        if corp is None:
            unmatched += 1
            continue
        rows.append(
            {
                "corp_code": corp.corp_code,
                "stock_code": listing.stock_code,
                "corp_name": listing.corp_name,
                "market": listing.market,
                "sector": None,
                "industry": listing.industry,
                "dart_modify_date": corp.modify_date,
                "is_active": True,
            }
        )

    if unmatched:
        logger.warning("%d KIND listings had no matching DART corp_code by stock_code", unmatched)

    if not rows:
        return 0

    session = get_session()
    try:
        stmt = pg_insert(Company).values(rows)
        update_cols = {
            c: stmt.excluded[c]
            for c in ("stock_code", "corp_name", "market", "industry", "dart_modify_date", "is_active")
        }
        update_cols["updated_at"] = func.now()
        stmt = stmt.on_conflict_do_update(index_elements=[Company.corp_code], set_=update_cols)
        session.execute(stmt)
        session.commit()
    finally:
        session.close()

    return len(rows)
