# OpenDART MCP Server (HTTP + Docker)

Dart(전자공시시스템) Open API를 MCP(Model Context Protocol) 서버 형태로 제공하는 경량 Docker 프로젝트입니다.
OpenAI Agent Builder에서 **HTTP Endpoint 기반 MCP 서버**로 연결해 사용할 수 있습니다.

## 제공 도구

- `search_disclosures`: 회사명/고유코드 기반 공시 목록 조회
- `get_company_overview`: 회사 개황 정보 조회
- `get_financial_statement`: 단일회사 주요 재무제표 조회

## 동작 방식

- MCP Transport: `streamable-http`
- 기본 엔드포인트: `http://<HOST>:8000/mcp`
- 환경 변수로 경로/포트 변경 가능
  - `MCP_HOST` (기본 `0.0.0.0`)
  - `MCP_PORT` (기본 `8000`)
  - `MCP_PATH` (기본 `/mcp`)

## 1) OpenDART API 키 발급

1. https://opendart.fss.or.kr 접속
2. Open API 인증키 발급
3. 발급 키를 `DART_API_KEY` 환경 변수로 지정

## 2) Docker로 실행 (Synology NAS DS718+)

### 이미지 빌드

```bash
docker build -t opendart-mcp:latest .
```

### 컨테이너 실행

```bash
docker run -d \
  --name opendart-mcp \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DART_API_KEY="YOUR_DART_API_KEY" \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  -e MCP_PATH=/mcp \
  opendart-mcp:latest
```

### DS718+ 운영 팁

- DS718+는 x86_64(Intel Celeron) 아키텍처이므로 기본 빌드 이미지로 실행 가능합니다.
- NAS 방화벽/공유기에서 `8000` 포트 접근 정책을 확인하세요.
- 외부 공개 시 리버스 프록시(Nginx/DSM Reverse Proxy) + HTTPS 구성을 권장합니다.

## 3) docker-compose 사용

```bash
export DART_API_KEY="YOUR_DART_API_KEY"
docker compose up -d --build
```

## 4) OpenAI Agent Builder 연동

Agent Builder에서 MCP 서버 URL을 아래처럼 설정하세요.

- MCP URL: `http://<synology-ip>:8000/mcp`

동일 네트워크/보안 그룹에서 Agent Builder가 접근 가능해야 합니다.

## 5) 로컬 직접 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DART_API_KEY="YOUR_DART_API_KEY"
export MCP_HOST=0.0.0.0
export MCP_PORT=8000
export MCP_PATH=/mcp
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
