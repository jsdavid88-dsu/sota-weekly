# SOTA Researcher - Simple Usage Guide

URL에서 텍스트를 추출하고 Notion에 저장하는 간단한 도구 (LLM 없음)

## 구조

```
D:\clawdbot_scripts\SOTA_Researcher\
├── extractors.py      # URL → Text 추출기
├── notion_api.py      # Notion 저장 함수
├── parse_url.py       # 메인 CLI
├── requirements.txt   # 의존성
└── config\.env        # API 키 설정
```

## 설치

```bash
cd D:\clawdbot_scripts\SOTA_Researcher
pip install -r requirements.txt
```

## 환경변수 설정

`config/.env` 파일 생성:

```env
NOTION_API_TOKEN=secret_xxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxx
```

## 사용법

### 1. URL에서 텍스트 추출만

```bash
python parse_url.py "https://arxiv.org/abs/2511.06953"
```

출력:
```
============================================================
제목: Paper Title Here
출처: arXiv
URL: https://arxiv.org/abs/2511.06953
작성자: Author Name...
태그: cs.AI, cs.CL
추출시간: 2026-01-30 14:32:10
============================================================

[본문 내용]
------------------------------------------------------------
# Paper Title Here

## Authors
Author Name, Author Two

## Abstract
This is the abstract text...
...
------------------------------------------------------------
```

### 2. JSON 형식 출력

```bash
python parse_url.py "https://arxiv.org/abs/2511.06953" --json
```

### 3. Notion에 저장

```bash
python parse_url.py "https://arxiv.org/abs/2511.06953" --save
```

## 지원 URL 타입

| 타입 | 예시 URL | 설명 |
|------|----------|------|
| arXiv | `arxiv.org/abs/2511.06953` | 논문 Abstract |
| YouTube | `youtube.com/watch?v=...` | 자막 (한국어→영어) |
| GitHub | `github.com/user/repo` | README.md |
| Article | 일반 웹페이지 | 본문 추출 |

## Python 코드에서 사용

### URL 추출만

```python
from extractors import extract_from_url

content = extract_from_url("https://arxiv.org/abs/2511.06953")
print(content.title)
print(content.content)
```

### Notion 저장

```python
from notion_api import save_to_notion

save_to_notion(
    title="My Title",
    url="https://example.com",
    content="Full content here...",
    tags=["AI", "개발"],
    source_type="Article"
)
```

## Arca에서 사용하는 방법

```python
import subprocess
import json

# 1. URL 추출
result = subprocess.run(
    ["python", "D:\\clawdbot_scripts\\SOTA_Researcher\\parse_url.py", 
     url, "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)

# 2. Arca에서 LLM 분석 수행 (요약, 아이디어 생성 등)
# ... Arca LLM 호출 ...

# 3. Notion 저장
from notion_api import save_to_notion
save_to_notion(
    title=data['title'],
    url=data['url'],
    content=llm_summary,  # Arca가 생성한 요약
    tags=data['tags'],
    source_type=data['source_type']
)
```

## 제거된 기능

- LLM 분석 (요약, 아이디어 생성)
- Arca 클라이언트
- Ollama 통합
- Telegram 봇

이제 이 도구는 **순수한 URL 파서** 역할만 합니다.
