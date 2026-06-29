"""Fetch and parse DART's bulk corpCode.xml listing of all corp_codes."""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass
from datetime import date, datetime

import requests

from config import settings

CORP_CODE_URL = "https://opendart.fss.or.kr/api/corpCode.xml"


@dataclass(frozen=True)
class CorpCodeEntry:
    corp_code: str
    corp_name: str
    stock_code: str | None  # None if unlisted
    modify_date: date | None


def fetch_corp_code_xml() -> bytes:
    """Download corpCode.xml.zip from DART and return the raw XML bytes."""
    resp = requests.get(CORP_CODE_URL, params={"crtfc_key": settings.dart_api_key}, timeout=30)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        return zf.read("CORPCODE.xml")


def parse_corp_code_xml(xml_bytes: bytes) -> list[CorpCodeEntry]:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_bytes)
    entries: list[CorpCodeEntry] = []
    for node in root.findall("list"):
        stock_code = (node.findtext("stock_code") or "").strip()
        modify_date_raw = (node.findtext("modify_date") or "").strip()
        entries.append(
            CorpCodeEntry(
                corp_code=(node.findtext("corp_code") or "").strip(),
                corp_name=(node.findtext("corp_name") or "").strip(),
                stock_code=stock_code or None,
                modify_date=datetime.strptime(modify_date_raw, "%Y%m%d").date() if modify_date_raw else None,
            )
        )
    return entries


def get_listed_corp_codes() -> list[CorpCodeEntry]:
    """Return only entries with a non-empty stock_code (i.e. listed on KRX)."""
    entries = parse_corp_code_xml(fetch_corp_code_xml())
    return [e for e in entries if e.stock_code]
