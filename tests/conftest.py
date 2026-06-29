import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "sample_dart_responses"


def load_fixture(*parts: str) -> dict:
    return json.loads((FIXTURES_DIR / Path(*parts)).read_text(encoding="utf-8"))


@pytest.fixture
def samsung_2023():
    return load_fixture("samsung_electronics", "2023_CFS.json")


@pytest.fixture
def samsung_years():
    return {
        year: load_fixture("samsung_electronics", f"{year}_CFS.json")
        for year in (2019, 2020, 2021, 2022, 2023)
    }


@pytest.fixture
def sk_hynix_2023():
    return load_fixture("sk_hynix", "2023_CFS.json")


@pytest.fixture
def shinla_gen_2023():
    return load_fixture("shinla_gen", "2023_CFS.json")
