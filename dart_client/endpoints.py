BASE_URL = "https://opendart.fss.or.kr/api"
FNLTT_SINGL_ACNT_ALL_URL = f"{BASE_URL}/fnlttSinglAcntAll.json"
STOCK_TOTQY_STTUS_URL = f"{BASE_URL}/stockTotqySttus.json"  # 주식의 총수 현황 (total shares outstanding)

# Pseudo fs_div used to namespace the shares-outstanding responses in the shared
# filesystem cache (the shares endpoint has no consolidated/separate distinction).
FS_DIV_SHARES = "SHARES"

REPRT_CODE_ANNUAL = "11011"  # 사업보고서 (annual report)
REPRT_CODE_HALF = "11012"
REPRT_CODE_Q1 = "11013"
REPRT_CODE_Q3 = "11014"

FS_DIV_CONSOLIDATED = "CFS"  # 연결재무제표
FS_DIV_SEPARATE = "OFS"  # 별도/개별재무제표

SJ_DIV_BALANCE_SHEET = "BS"
SJ_DIV_INCOME_STATEMENT = "IS"
SJ_DIV_COMPREHENSIVE_INCOME = "CIS"
SJ_DIV_CASH_FLOW = "CF"
SJ_DIV_EQUITY_CHANGES = "SCE"

# DART status codes that should never be retried blindly
STATUS_OK = "000"
STATUS_NO_DATA = "013"
STATUS_RATE_LIMIT = "020"
STATUS_FIELD_ERROR = "100"
STATUS_AUTH_ERROR = "800"
STATUS_TRANSIENT = {"900", "901"}
