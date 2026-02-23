# OpenDART MCP Server (Docker)

Dart(전자공시시스템) Open API를 MCP(Model Context Protocol) 서버 형태로 제공하는 경량 Docker 프로젝트입니다.
OpenAI Agent Builder에서 MCP 서버로 연결해 공시 조회 도구로 사용할 수 있습니다.

## 제공 도구

- `search_disclosures`: 회사명/고유코드 기반 공시 목록 조회
- `get_company_overview`: 회사 개황 정보 조회
- `get_financial_statement`: 단일회사 주요 재무제표 조회

## 1) OpenDART API 키 발급

1. https://opendart.fss.or.kr 접속
2. Open API 인증키 발급
3. 발급 키를 `DART_API_KEY` 환경 변수로 지정

## 2) Docker로 실행 (Synology NAS 권장)

### 이미지 빌드

```bash
docker build -t opendart-mcp:latest .
```

### 컨테이너 실행

```bash
docker run -d \
  --name opendart-mcp \
  --restart unless-stopped \
  -e DART_API_KEY="YOUR_DART_API_KEY" \
  -i -t \
  opendart-mcp:latest
```

> MCP stdio 서버이므로 `-i -t` 옵션을 유지해주는 편이 안정적입니다.

## 3) docker-compose 사용

```bash
export DART_API_KEY="YOUR_DART_API_KEY"
docker compose up -d --build
```

## 4) OpenAI Agent Builder 연동 팁

Agent Builder에서 MCP 서버를 도커 기반 커스텀 서버로 연결할 때, 아래 명령 패턴으로 지정하면 됩니다.

```bash
docker run --rm -i \
  -e DART_API_KEY=YOUR_DART_API_KEY \
  opendart-mcp:latest
```

서버는 `stdio` transport로 동작합니다.

## 5) 로컬 직접 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DART_API_KEY="YOUR_DART_API_KEY"
python server.py
```

## 프로젝트 구조

```text
.
├─ server.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```
