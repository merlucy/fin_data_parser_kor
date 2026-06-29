"""CLI: run a full screen for one industry -> fetch+calc+persist a screening run.

Usage: python -m jobs.run_screen --industry "반도체 제조업" [--years 5] [--fs-div-preference CFS]
"""

from __future__ import annotations

import argparse
import datetime
import logging

from calculations.pipeline import run_for_company
from dart_client.errors import DartDailyLimitReached
from db import repository
from universe.resolver import resolve_companies

logger = logging.getLogger(__name__)


def run_screen(industry: str, history_years: int = 5) -> int:
    companies = resolve_companies(industry)
    if not companies:
        raise ValueError(f"No companies found for industry '{industry}'. Did you run jobs.refresh_universe?")

    current_year = datetime.date.today().year
    # Most recent annual report likely filed is for the prior fiscal year.
    fiscal_year_end = current_year - 1
    years = list(range(fiscal_year_end - history_years + 1, fiscal_year_end + 1))

    run_id = repository.create_screening_run(
        sector=None, industry=industry, fiscal_year_end=fiscal_year_end, history_years=history_years
    )
    repository.add_companies_to_run(run_id, [c.corp_code for c in companies])

    completed = 0
    try:
        for company in companies:
            logger.info("Computing metrics for %s (%s)", company.corp_name, company.corp_code)
            rows = run_for_company(company.corp_code, years)
            repository.write_company_financials(run_id, rows)
            completed += 1
    except DartDailyLimitReached as e:
        logger.warning("Stopping early: %s", e)
        repository.complete_screening_run(run_id, completed, status="partial", notes=str(e))
        return run_id

    repository.complete_screening_run(run_id, completed, status="completed")
    return run_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--industry", required=True, help="Industry name, must match companies.industry exactly")
    parser.add_argument("--years", type=int, default=5)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run_id = run_screen(args.industry, history_years=args.years)
    print(f"Screening run {run_id} for industry '{args.industry}' finished.")


if __name__ == "__main__":
    main()
