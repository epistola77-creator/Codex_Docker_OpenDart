import os
from datetime import datetime
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = "https://opendart.fss.or.kr/api"
TIMEOUT = 20.0

APP_NAME = "OpenDartMCP"
HTTP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("MCP_PORT", "8000"))
HTTP_PATH = os.getenv("MCP_PATH", "/mcp")

mcp = FastMCP(APP_NAME)


class DartAPIError(RuntimeError):
    """Raised when OpenDART API returns an error payload."""


def _api_key() -> str:
    api_key = os.getenv("DART_API_KEY")
    if not api_key:
        raise DartAPIError(
            "DART_API_KEY 환경 변수가 비어 있습니다. Synology Docker 환경 변수에 발급받은 키를 설정해주세요."
        )
    return api_key


def _request(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    request_params = {"crtfc_key": _api_key(), **params}

    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.get(f"{BASE_URL}/{endpoint}", params=request_params)
        response.raise_for_status()
        payload = response.json()

    status = payload.get("status")
    if status and status != "000":
        message = payload.get("message", "원인을 알 수 없는 오류")
        raise DartAPIError(f"OpenDART 오류(status={status}): {message}")

    return payload


def _normalize_date(value: str | None, fallback: str) -> str:
    if not value:
        return fallback
    stripped = value.replace("-", "")
    if len(stripped) != 8 or not stripped.isdigit():
        raise ValueError("날짜는 YYYYMMDD 또는 YYYY-MM-DD 형식이어야 합니다.")
    return stripped


@mcp.tool(description="회사명 또는 공시번호 기준으로 전자공시 목록을 조회합니다.")
def search_disclosures(
    corp_name: str | None = None,
    corp_code: str | None = None,
    bgn_de: str | None = None,
    end_de: str | None = None,
    page_no: int = 1,
    page_count: int = 10,
    last_reprt_at: str = "N",
) -> dict[str, Any]:
    """OpenDART list.json API를 사용해 공시 목록을 조회합니다."""
    today = datetime.now().strftime("%Y%m%d")
    start_of_year = datetime.now().strftime("%Y0101")

    params: dict[str, Any] = {
        "page_no": page_no,
        "page_count": max(1, min(page_count, 100)),
        "last_reprt_at": last_reprt_at,
        "bgn_de": _normalize_date(bgn_de, start_of_year),
        "end_de": _normalize_date(end_de, today),
    }

    if corp_name:
        params["corp_name"] = corp_name
    if corp_code:
        params["corp_code"] = corp_code

    if not corp_name and not corp_code:
        raise ValueError("corp_name 또는 corp_code 중 하나는 반드시 입력해야 합니다.")

    return _request("list.json", params)


@mcp.tool(description="회사 고유코드(corp_code)로 기업 개황 정보를 조회합니다.")
def get_company_overview(corp_code: str) -> dict[str, Any]:
    """OpenDART company.json API를 통해 회사 개황을 가져옵니다."""
    if not corp_code or len(corp_code) != 8 or not corp_code.isdigit():
        raise ValueError("corp_code는 숫자 8자리여야 합니다.")

    return _request("company.json", {"corp_code": corp_code})


@mcp.tool(description="단일회사 주요 재무제표를 조회합니다.")
def get_financial_statement(
    corp_code: str,
    bsns_year: str,
    reprt_code: str = "11011",
) -> dict[str, Any]:
    """OpenDART fnlttSinglAcnt.json API를 호출합니다."""
    if not corp_code or len(corp_code) != 8 or not corp_code.isdigit():
        raise ValueError("corp_code는 숫자 8자리여야 합니다.")
    if len(bsns_year) != 4 or not bsns_year.isdigit():
        raise ValueError("bsns_year는 YYYY 형식이어야 합니다.")

    return _request(
        "fnlttSinglAcnt.json",
        {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        },
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=HTTP_HOST,
        port=HTTP_PORT,
        path=HTTP_PATH,
    )
