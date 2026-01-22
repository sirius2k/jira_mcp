# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jira MCP (Model Context Protocol) Server - AI 모델이 Jira REST API v3에 접근할 수 있도록 표준화된 MCP 프로토콜을 제공하는 서버입니다.

**핵심 특징:**
- 완전 비동기 구현 (httpx + asyncio)
- 엄격한 타입 검사 (mypy strict mode)
- 높은 테스트 커버리지 (테스트:소스 비율 2.6:1)
- Atlassian Document Format (ADF) 완전 지원
- stdio 기반 MCP 통신

**기술 스택:**
- Python 3.10+
- MCP SDK (Model Context Protocol)
- httpx (비동기 HTTP)
- pydantic-settings (타입 안전 설정)
- pytest + pytest-asyncio (테스팅)

## Directory Structure

```
jira-mcp/
├── src/jira_mcp/           # 메인 소스 코드
│   ├── __init__.py         # 패키지 초기화 및 버전
│   ├── config.py           # 환경 설정 (Settings 클래스)
│   ├── client.py           # JiraClient - 비동기 API 클라이언트
│   └── server.py           # MCP 서버 구현 (8개 도구)
├── tests/                  # 테스트 코드
│   ├── conftest.py         # pytest 픽스처
│   ├── test_config.py      # 설정 테스트
│   ├── test_client.py      # 클라이언트 테스트 (506줄)
│   └── test_server.py      # 서버 도구 테스트
├── .claude/                # Claude Code 설정
│   ├── settings.json       # 권한 설정
│   └── commands/           # 커스텀 명령어 (한글)
├── pyproject.toml          # 프로젝트 설정
├── CLAUDE.md               # 이 파일
├── README.md               # 프로젝트 문서
└── .env.example            # 환경 변수 템플릿
```

## Build & Development Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run server
jira-mcp
# or
python -m jira_mcp.server

# Testing
python -m pytest                    # Run all tests
python -m pytest -v                 # Verbose output
python -m pytest -k "test_name"     # Run specific test
python -m pytest tests/test_client.py  # Run single file

# Code quality
python -m mypy src                  # Type checking (strict mode)
python -m ruff check src            # Linting
python -m ruff check src --fix      # Auto-fix lint issues
python -m ruff format src           # Code formatting
```

## Architecture

### Core Components

#### 1. config.py - 환경 설정 관리
```python
class Settings(BaseSettings):
    jira_url: str              # Jira 인스턴스 URL (필수)
    jira_username: str         # Jira 이메일 (필수)
    jira_api_token: str        # API 토큰 (필수)
    jira_timeout: int = 30     # 요청 타임아웃 (초)
```

- pydantic-settings 기반 타입 안전 설정
- .env 파일 자동 로드
- 싱글톤 패턴 (`get_settings()`)

#### 2. client.py - Jira REST API 클라이언트

**클래스:** `JiraClient`

**모든 메서드는 async이며 `dict[str, Any]` 또는 `list[dict[str, Any]]` 반환:**

| 메서드 | 설명 | 엔드포인트 |
|--------|------|-----------|
| `get_issue(issue_key)` | 이슈 조회 | GET /rest/api/3/issue/{key} |
| `search_issues(jql, max_results=50)` | JQL 검색 | GET /rest/api/3/search |
| `create_issue(project_key, summary, issue_type, description?)` | 이슈 생성 | POST /rest/api/3/issue |
| `update_issue(issue_key, fields)` | 이슈 필드 업데이트 | PUT /rest/api/3/issue/{key} |
| `add_comment(issue_key, comment)` | 댓글 추가 (ADF) | POST /rest/api/3/issue/{key}/comment |
| `get_comments(issue_key, start_at=0, max_results=50)` | 댓글 조회 (페이지네이션) | GET /rest/api/3/issue/{key}/comment |
| `get_projects()` | 프로젝트 목록 | GET /rest/api/3/project |
| `transition_issue(issue_key, transition_id)` | 상태 전환 | POST /rest/api/3/issue/{key}/transitions |
| `get_transitions(issue_key)` | 가능한 전환 조회 | GET /rest/api/3/issue/{key}/transitions |

**구현 특징:**
- httpx.AsyncClient 사용
- Basic Auth (username + API token)
- response.raise_for_status() 호출
- cast()로 타입 명시

#### 3. server.py - MCP 서버 구현

**제공하는 8개 MCP 도구:**

| Tool | Description | Required Args | Optional Args |
|------|-------------|---------------|---------------|
| `get_issue` | 이슈 조회 | issue_key | - |
| `search_issues` | JQL 검색 | jql | max_results (50) |
| `create_issue` | 이슈 생성 | project_key, summary, issue_type | description |
| `update_issue` | 필드 업데이트 | issue_key, fields | - |
| `add_comment` | 댓글 추가 | issue_key, comment | - |
| `get_projects` | 프로젝트 목록 | - | - |
| `transition_issue` | 상태 전환 | issue_key, transition_id | - |
| `get_transitions` | 가능한 전환 조회 | issue_key | - |

**구현 방식:**
- `@server.list_tools()`: 도구 목록 및 JSON Schema 정의
- `@server.call_tool()`: 도구 실행 및 에러 처리
- stdio 기반 통신
- 전역 JiraClient 인스턴스 (싱글톤)

### Jira API 상세

#### Atlassian Document Format (ADF)

Jira REST API v3는 description, comment 등의 rich text 필드에 ADF 포맷 사용:

```python
# add_comment 예시
{
    "body": {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Simple text"}
                ]
            }
        ]
    }
}

# 포맷팅 예시
{
    "type": "paragraph",
    "content": [
        {"type": "text", "text": "Bold text", "marks": [{"type": "strong"}]},
        {"type": "text", "text": " and "},
        {"type": "text", "text": "italic", "marks": [{"type": "em"}]}
    ]
}
```

**지원되는 ADF 구조:**
- paragraph (단락)
- bulletList / orderedList (리스트)
- text + marks (bold, italic, underline 등)
- 중첩 구조

#### 페이지네이션

`get_comments` 메서드는 페이지네이션 지원:

```python
response = {
    "startAt": 0,
    "maxResults": 50,
    "total": 120,
    "isLast": False,
    "values": [...]  # 댓글 배열
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JIRA_URL` | Yes | - | Jira 인스턴스 URL (예: https://your-domain.atlassian.net) |
| `JIRA_USERNAME` | Yes | - | Jira 계정 이메일 |
| `JIRA_API_TOKEN` | Yes | - | API 토큰 (https://id.atlassian.com/manage-profile/security/api-tokens에서 생성) |
| `JIRA_TIMEOUT` | No | 30 | HTTP 요청 타임아웃 (초) |

**설정 방법:**
1. `.env.example`을 `.env`로 복사
2. 실제 값으로 변경
3. `.env` 파일은 .gitignore에 포함됨 (보안)

## Testing

### 테스트 전략

- **프레임워크**: pytest + pytest-asyncio (auto mode)
- **Mock 사용**: httpx 응답을 Mock하여 실제 API 호출 없이 테스트
- **커버리지**: 테스트 코드가 소스 코드의 2.6배 (매우 높음)

### 테스트 구조

```python
# conftest.py - 공통 픽스처
@pytest.fixture
def mock_settings():
    return Settings(...)

@pytest.fixture
def jira_client(mock_settings):
    return JiraClient(mock_settings)

# test_client.py - 클라이언트 테스트 (506줄)
- 각 메서드마다 2~8개의 테스트
- get_comments는 8개 테스트 (페이지네이션 엣지 케이스)
- 복잡한 ADF 구조 테스트
- 에러 처리 테스트
```

### 테스트 실행

```bash
# 전체 테스트
python -m pytest

# 특정 테스트만
python -m pytest -k "test_get_comments"

# 상세 출력
python -m pytest -v

# 단일 파일
python -m pytest tests/test_client.py
```

## Code Quality Standards

### Type Checking (mypy)

**설정 (pyproject.toml):**
```ini
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true
```

**원칙:**
- 모든 함수에 타입 힌트 필수
- API 응답은 `cast()`로 타입 명시
- `dict[str, Any]` 명시적 사용

**예시:**
```python
async def get_issue(self, issue_key: str) -> dict[str, Any]:
    response = await client.get(...)
    return cast(dict[str, Any], response.json())
```

### Linting (ruff)

**설정:**
```ini
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]
```

**검사 항목:**
- E: 문법 에러
- F: Pyflakes (논리 에러)
- I: isort (import 정렬)
- W: 경고

### Error Handling

**클라이언트 레벨:**
```python
response = await client.get(...)
response.raise_for_status()  # HTTP 에러 자동 raise
```

**서버 레벨:**
```python
try:
    result = await jira.get_issue(issue_key)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
except Exception as e:
    return [TextContent(type="text", text=f"Error: {str(e)}")]
```

## Development Guidelines

### 코드 작성 시 주의사항

1. **비동기 패턴 유지**
   - 모든 API 호출은 `async/await` 사용
   - `httpx.AsyncClient` 사용
   - `pytest-asyncio`로 테스트

2. **타입 안전성**
   - 새 함수에 타입 힌트 필수
   - mypy strict 모드 통과 필수
   - `cast()` 적절히 사용

3. **테스트 작성**
   - 새 메서드마다 최소 2개 테스트 (정상 케이스 + 에러 케이스)
   - httpx 응답 Mock 사용
   - 페이지네이션이 있으면 엣지 케이스 테스트

4. **ADF 포맷**
   - description, comment는 ADF 구조 사용
   - 최소 구조: `{"type": "doc", "version": 1, "content": [...]}`
   - paragraph + text 조합이 기본

5. **에러 처리**
   - 클라이언트: `raise_for_status()` 호출
   - 서버: try-except로 감싸고 에러 메시지 반환

### 새로운 MCP 도구 추가하기

1. **client.py에 메서드 추가**
```python
async def new_method(self, param: str) -> dict[str, Any]:
    """Method description."""
    url = f"{self.base_url}/rest/api/3/endpoint"
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())
```

2. **server.py에 도구 정의 추가**
```python
# list_tools()에 추가
Tool(
    name="new_tool",
    description="Tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Param description"}
        },
        "required": ["param"]
    }
)

# call_tool()에 핸들러 추가
case "new_tool":
    result = await jira.new_method(arguments["param"])
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
```

3. **테스트 작성**
```python
# test_client.py
async def test_new_method(jira_client):
    # Mock httpx 응답 설정
    # 메서드 호출 및 검증
    pass

# test_server.py
async def test_new_tool():
    # MCP 도구 호출 테스트
    pass
```

## Claude Code Integration

이 프로젝트는 Claude Code와 깊이 통합되어 있습니다.

### 커스텀 명령어

`.claude/commands/` 디렉토리에 한글 기반 커스텀 명령어 포함:

1. **resolve-issue.md** - GitHub 이슈 자동 해결
   - 이슈 분석, 브랜치 생성, 코드 작성, 테스트, PR 생성

2. **decompose-issue.md** - 작업 세분화
   - 큰 작업을 작은 이슈로 분해

3. **commit-and-push.md** - 커밋 및 푸시
   - 변경사항 자동 커밋 및 Co-Authored-By 추가

4. **pull-main-and-prune.md** - 브랜치 최신화
   - main 브랜치 업데이트 및 정리

### 권한 설정

`.claude/settings.json`:
```json
{
    "allowedCommands": [
        {
            "command": "python3",
            "type": "startsWith"
        }
    ]
}
```

## Common Tasks

### 새 이슈 타입 지원 추가

Jira는 프로젝트마다 다른 이슈 타입을 가질 수 있습니다. 새 이슈 타입 추가 시:

1. `create_issue` 메서드는 이미 모든 타입 지원 (파라미터로 받음)
2. 문서만 업데이트하면 됨
3. 테스트에 새 타입 추가 (선택사항)

### 커스텀 필드 처리

Jira 커스텀 필드는 `customfield_XXXXX` 형식:

```python
# update_issue 사용
await jira.update_issue("PROJ-123", {
    "customfield_10001": "value",
    "customfield_10002": {"id": "10000"}
})
```

### 에러 디버깅

1. **인증 에러**: JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN 확인
2. **타임아웃**: JIRA_TIMEOUT 증가
3. **404 에러**: 이슈 키 또는 프로젝트 키 확인
4. **ADF 포맷 에러**: body 구조 확인 (type: "doc" 필수)

## Resources

- [Jira REST API v3 문서](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Atlassian Document Format (ADF)](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [MCP Protocol 사양](https://modelcontextprotocol.io/)
- [API 토큰 생성](https://id.atlassian.com/manage-profile/security/api-tokens)
