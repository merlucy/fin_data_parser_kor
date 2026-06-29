"""CLI: rebuild the KIND-industry <-> DART corp_code mapping in the companies table.

Usage: python -m jobs.refresh_universe
"""

import logging

from universe.mapping_builder import build_universe


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    count = build_universe()
    print(f"Upserted {count} companies into the companies table.")


if __name__ == "__main__":
    main()
