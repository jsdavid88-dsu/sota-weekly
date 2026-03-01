"""
bkit 페이지 업데이트 - 한글 요약 + 본문 추가
"""
import httpx
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(env_path)

token = os.getenv('NOTION_API_TOKEN')
page_id = "2f8f0270-7d88-8115-8acf-ff18b7d4eb11"

headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 한글 요약
summary_kr = """
bkit은 Claude Code와 Gemini CLI를 위한 PDCA 기반 개발 방법론 플러그인입니다.

**핵심 기능:**
- Context Engineering: 21개 스킬, 11개 에이전트, 39개 스크립트
- 9단계 개발 파이프라인 (Starter/Dynamic/Enterprise)
- PDCA 사이클 통합 (/pdca plan, design, do, analyze)
- 자동 문서화 및 반복 개선 (Evaluator-Optimizer Pattern)
- 8개 언어 지원 (EN, KO, JA, ZH, ES, FR, DE, IT)

**프로젝트 레벨:**
1. Starter: 정적 웹사이트 (HTML/CSS/JS)
2. Dynamic: 풀스택 앱 (Next.js + BaaS)
3. Enterprise: 마이크로서비스 (K8s + Terraform)

**설치:**
- Claude Code: `/plugin marketplace add popup-studio-ai/bkit-claude-code`
- Gemini CLI: `git clone ~/.gemini/extensions/bkit`

AI 네이티브 개발을 위한 구조화된 워크플로우를 제공합니다.
"""

# 본문 내용
content_kr = """
## Context Engineering이란?

Context Engineering은 단순한 프롬프트 작성을 넘어, LLM에 최적의 맥락(context)을 제공하는 시스템 설계 방법론입니다.

**전통적 Prompt Engineering:**
"좋은 프롬프트를 작성하는 기술"

**Context Engineering:**
"프롬프트, 도구, 상태를 통합하여 LLM에 최적의 맥락을 제공하는 시스템 설계"

### bkit의 Context Engineering 구조

**3개 계층:**
1. **Domain Knowledge** - 21개 스킬 (단계별, 레벨별, 전문 도메인)
2. **Behavioral Rules** - 11개 에이전트 (역할 기반 제약, 모델 선택)
3. **State Management** - 86+ 함수 (PDCA 상태, 의도 감지, 모호성 점수)

**5개 Hook 레이어:**
- Layer 1: hooks.json (Global)
- Layer 2: Skill Frontmatter (도메인별)
- Layer 3: Agent Frontmatter (작업별)
- Layer 4: Description Triggers (8개 언어 의미 매칭)
- Layer 5: Scripts (39개 Node.js 모듈)

---

## 주요 기능

### 1. PDCA 통합 (v1.4.7)

**통합 /pdca 스킬:**
```
/pdca plan {feature}     # 계획 문서 생성
/pdca design {feature}   # 설계 문서 생성
/pdca do {feature}       # 구현 가이드
/pdca analyze {feature}  # 갭 분석
/pdca iterate {feature}  # 자동 수정 (최대 5회 반복, 90% 기준)
/pdca report {feature}   # 완료 보고서
/pdca status             # 현재 상태 확인
/pdca next               # 다음 단계 안내
```

**Check↔Act 반복 루프:**
- 자동 갭 분석
- Evaluator-Optimizer Pattern (Anthropic 에이전트 아키텍처)
- 최대 5회 반복, 90% 달성 기준

### 2. Task 관리 (v1.4.7)

- Task Chain 자동 생성
- Task ID 영속성
- PDCA 사이클과 통합

### 3. 모듈화 (v1.4.7)

**lib/ 구조:**
- `lib/core/` - 핵심 유틸리티
- `lib/pdca/` - PDCA 로직
- `lib/intent/` - 의도 감지
- `lib/task/` - 작업 추적

### 4. 9단계 개발 파이프라인

1. **Schema** - 용어 및 데이터 구조 정의
2. **Convention** - 코딩 규칙 및 스타일
3. **Mockup** - UI/UX 프로토타입
4. **API** - 백엔드 API 설계/구현
5. **Design System** - 컴포넌트 라이브러리
6. **UI Integration** - 프론트엔드-백엔드 연동
7. **SEO & Security** - 검색 최적화 및 보안
8. **Review** - 코드 품질 검증
9. **Deployment** - 프로덕션 배포

---

## 프로젝트 레벨

### Starter (정적 웹)
- **대상:** 초보자, 포트폴리오
- **스택:** HTML, CSS, JavaScript
- **명령:** `/starter`

### Dynamic (풀스택)
- **대상:** 로그인/DB가 필요한 웹앱
- **스택:** Next.js + BaaS (bkend.ai)
- **명령:** `/dynamic`

### Enterprise (마이크로서비스)
- **대상:** 고트래픽, 고가용성 시스템
- **스택:** K8s, Terraform, MSA
- **명령:** `/enterprise`

---

## 커스터마이징

설치 후 `.claude/` 폴더에 복사하여 커스터마이징 가능:

```bash
# 1. 플러그인 위치 확인
ls ~/.claude/plugins/bkit/

# 2. 커스터마이징할 파일만 복사
mkdir -p .claude/skills/starter
cp ~/.claude/plugins/bkit/skills/starter/SKILL.md .claude/skills/starter/

# 3. 수정 후 커밋
git add .claude/
git commit -m "feat: customize bkit starter skill"
```

**우선순위:**
1. 프로젝트 `.claude/` (최우선)
2. 사용자 `~/.claude/`
3. 플러그인 설치 (기본값)

---

## 언어 지원

8개 언어 자동 감지:
- 영어, 한국어, 일본어, 중국어
- 스페인어, 프랑스어, 독일어, 이탈리아어

**응답 언어 설정:**
```json
// .claude/settings.json
{
  "language": "korean"
}
```

---

## 라이선스

Copyright 2024-2026 POPUP STUDIO PTE. LTD.

Apache License 2.0

재배포 시 NOTICE 파일 포함 필수.

---

**공식 링크:**
- GitHub: https://github.com/popup-studio-ai/bkit-claude-code
- 문서: https://docs.anthropic.com/en/docs/claude-code
- 홈페이지: https://popupstudio.ai
"""

# 1. 요약 업데이트
print("1. 요약 업데이트 중...")
httpx.patch(
    f"https://api.notion.com/v1/pages/{page_id}",
    headers=headers,
    json={
        "properties": {
            "요약": {
                "rich_text": [{"text": {"content": summary_kr}}]
            }
        }
    },
    timeout=30.0
)
print("   완료!")

# 2. 본문 추가
print("2. 본문 추가 중...")
chunks = [content_kr[i:i+2000] for i in range(0, len(content_kr), 2000)]
blocks = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"text": {"content": chunk}}]
        }
    }
    for chunk in chunks
]

httpx.patch(
    f"https://api.notion.com/v1/blocks/{page_id}/children",
    headers=headers,
    json={"children": blocks},
    timeout=30.0
)
print("   완료!")

print("\n✅ bkit 페이지 업데이트 완료!")
print(f"URL: https://www.notion.so/{page_id.replace('-', '')}")
