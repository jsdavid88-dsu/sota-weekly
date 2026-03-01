# Notion 세컨드 브레인 (Second Brain) 구조

> AI4PKM 개념을 Notion에 적용한 DSUComfyCG 특화 지식 관리 시스템

---

## 📊 Database 구조

### 1. Research Database (메인)

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| 📄 Title | Title | 논문/영상/아티클 제목 |
| 🔗 URL | URL | 원본 링크 |
| 📝 Summary | Text | AI 요약 (아르카가 작성) |
| 🏷️ Tags | Multi-select | LoRA, ComfyUI, UE5, Gaussian Splatting, etc. |
| 📅 Added | Date | 수집 날짜 (자동) |
| 🎯 Relevance | Select | High / Medium / Low (DSUComfyCG 관련도) |
| 💡 Ideas | Text | 연계 아이디어 (바로 적용 가능한 것) |
| 🔗 Projects | Relation | → Projects DB 연결 |
| 📊 Status | Select | Inbox / Processing / Done |
| 📚 Source Type | Select | arXiv / YouTube / GitHub / Article |

**View 구성:**
- 🎯 **High Priority** - Relevance = High
- 📅 **This Week** - Added date = This week
- 🏷️ **By Tag** - Group by Tags
- 📊 **By Status** - Kanban board

---

### 2. Projects Database

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| 📁 Project Name | Title | DSUComfyCG Pipeline, 부산마법소녀, etc. |
| 📝 Description | Text | 프로젝트 설명 |
| 🔗 Related Research | Relation | ← Research DB 역참조 |
| 📊 Stage | Select | Stage 1~6 (DSUComfyCG 파이프라인) |
| 🎯 Status | Select | Planning / Active / Done |
| 📅 Deadline | Date | 마감일 (KOCCA 사업 등) |

**초기 프로젝트:**
- DSUComfyCG - Stage 1: LoRA 학습기
- DSUComfyCG - Stage 2: Storyboard
- DSUComfyCG - Stage 3: DCC Bridge
- DSUComfyCG - Stage 4: AI Rendering
- DSUComfyCG - Stage 5-6: Final Output
- 부산마법소녀 IP 개발
- KOCCA 사업 (21개월)

---

### 3. Weekly Review Database

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| 📅 Week of | Date | 주차 시작일 (월요일) |
| 📝 Summary | Text | 주간 리서치 요약 |
| 🎯 Top Findings | Text | 핵심 발견 3가지 |
| 💡 Action Items | Text | 다음 주 할 일 |
| 📊 Research Count | Number | 이번 주 수집한 리서치 개수 |
| 🔗 Related Research | Relation | → Research DB (필터: This week) |

---

## 🔄 워크플로우

### Phase 1: Ingest (수집)

```
준석 (Telegram): https://arxiv.org/abs/2511.06953

↓

아르카:
1. URL 파싱 (extractors.py)
   → 텍스트 추출 (논문 abstract, YouTube 자막 등)

2. AI 분석 (아르카가 직접)
   - Summary 생성 (DSUComfyCG 관점)
   - Relevance 판단 (High/Medium/Low)
   - Ideas 추출 (어느 Stage에 적용 가능?)
   - Tags 추출 (LoRA, Gaussian Splatting 등)

3. Notion 저장 (notion_api.py)
   → Research DB에 새 페이지 생성

4. 텔레그램 응답
   "📄 GFix 논문 저장 완료!
    🎯 Relevance: High
    💡 Stage 2-4 적용 가능
    🔗 https://notion.so/..."
```

### Phase 2: Organize (정리)

**Daily Roundup (매일 오전 9시)**
```
1. 어제 수집된 Research 확인
2. 간단 브리핑 텔레그램 전송
   "어제 3개 논문 수집:
    - GFix (High): LoRA 압축
    - ... "
```

**Weekly Review (금요일 오후 6시)**
```
1. 이번 주 Research 전체 분석
2. 패턴/트렌드 파악
3. Weekly Review DB에 요약 저장
4. 텔레그램 리포트 전송
```

### Phase 3: Create (생성)

**슬라이드 생성**
```
준석: "이번 주 리서치로 발표 자료 만들어줘"

아르카:
1. Weekly Review 읽기
2. Markdown Slides 생성
3. Notion에 Presentation 페이지 추가
4. 결과 전송
```

---

## 🧠 세컨드 브레인 원칙 적용

### CODE 원칙

| C | O | D | E |
|---|---|---|---|
| Capture | Organize | Distill | Express |
| URL 수집 | Tags/Projects | Summary | 발표/글 |

**Notion 적용:**
- **Capture:** 텔레그램으로 URL 던지기
- **Organize:** Tags, Projects Relations, Status
- **Distill:** Summary 필드 (핵심만)
- **Express:** Weekly Review, Slides

### 제텔카스텐 4원칙

**1. Atomicity (원자성)**
- 하나의 Research 페이지 = 하나의 논문/아티클
- 너무 길면 분할 (예: 논문 Chapter별)

**2. Links (연결)**
- Notion Relations: Research ↔ Projects
- 백링크: @mention으로 다른 페이지 참조

**3. Own Words (자기 언어)**
- Summary는 아르카가 작성 (원문 그대로 X)
- Ideas는 준석 관점에서 재해석

**4. Source (출처)**
- URL 필드 필수
- Source Type으로 신뢰도 판단

---

## 🎯 DSUComfyCG 특화 기능

### Stage별 자동 분류

**Tags 기반 자동 매핑:**
```
LoRA, Character Consistency → Stage 1
Gaussian Splatting, 3D Reconstruction → Stage 2
Maya, Nuke, DCC → Stage 3
Long Video, AnimateDiff → Stage 4
Compositing, EXR → Stage 5-6
```

### 관련도 자동 판단

**High:**
- DSUComfyCG Pipeline에 직접 적용 가능
- 예: LoRA 압축, Gaussian Splatting 압축

**Medium:**
- 간접 연관 (학술적 배경, 유사 기술)
- 예: Diffusion 이론, 3D Vision

**Low:**
- 참고용 (트렌드, 주변 기술)
- 예: 일반 AI 뉴스

---

## 🚀 Quick Start

### 1. Notion Database 생성

**Research DB:**
```
1. Notion에서 "New" → "Database - Full page"
2. Properties 추가 (위 표 참조)
3. Views 생성 (High Priority, This Week 등)
```

**Projects DB:**
```
1. 새 Database 생성
2. Properties 추가
3. Initial Projects 추가 (DSUComfyCG Stages)
```

**Weekly Review DB:**
```
1. 새 Database 생성
2. Properties 추가
```

### 2. Notion API 연동

**Integration 생성:**
```
1. https://www.notion.so/my-integrations
2. "New integration" 클릭
3. 이름: "SOTA Researcher"
4. Associated workspace 선택
5. Token 복사
```

**Database 권한 부여:**
```
1. Research DB 우상단 "..." → "Connections"
2. "SOTA Researcher" 선택
3. Projects DB, Weekly Review DB도 동일하게
```

**Config 설정:**
```bash
# D:\clawdbot_scripts\SOTA_Researcher\config\.env
NOTION_TOKEN=secret_xxxxx
NOTION_RESEARCH_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_PROJECTS_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_WEEKLY_DB=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 첫 수집 테스트

**텔레그램:**
```
https://arxiv.org/abs/2511.06953
```

**아르카 응답:**
```
📄 GFix: Gaussian Splatting 압축
🎯 Relevance: High
💡 Stage 2-4 적용 가능 (6배 압축률!)
✅ Notion 저장 완료
```

---

## 📅 자동화 스케줄 (예정)

| 시간 | 작업 | 설명 |
|------|------|------|
| 매일 09:00 | Daily Roundup | 어제 수집 요약 |
| 금요일 18:00 | Weekly Review | 주간 분석 리포트 |
| 월요일 09:00 | Week Start | 이번 주 계획 |

---

## 💡 활용 예시

### 시나리오 1: 논문 발견 → 적용

```
1. arXiv 논문 발견
2. 텔레그램으로 URL 전송
3. 아르카 분석 → Notion 저장
4. 주말에 Notion에서 Review
5. "이거 Stage 2에 바로 쓸 수 있겠는데?"
6. Projects DB에서 해당 Stage 클릭 → Related Research 확인
```

### 시나리오 2: 발표 준비

```
1. 금요일 Weekly Review 확인
2. "이번 주 리서치로 슬라이드 만들어줘"
3. 아르카가 Top Findings 기반 슬라이드 생성
4. Notion Presentation 페이지에 저장
5. 발표 준비 완료
```

### 시나리오 3: KOCCA 사업 보고서

```
1. Projects DB → "KOCCA 사업" 필터
2. Related Research 모두 확인
3. "이번 달 진행 상황 보고서 작성해줘"
4. 아르카가 Research 기반 보고서 생성
```

---

## 🔧 고급 기능 (Optional)

### Notion Formulas

**Progress Indicator:**
```
if(prop("Status") == "Done", "✅", 
if(prop("Status") == "Processing", "🔄", "📥"))
```

**Days Since Added:**
```
dateBetween(now(), prop("Added"), "days")
```

### Notion API Automation

**자동 태그 추출:**
```python
# AI가 제안한 태그를 자동으로 Multi-select에 추가
tags = ["LoRA", "Gaussian Splatting", "Video Compression"]
notion_client.pages.update(page_id, properties={"Tags": {"multi_select": [{"name": t} for t in tags]}})
```

---

## 📚 참고 자료

- [Building a Second Brain](https://fortelabs.com/blog/basboverview/) - Tiago Forte
- [제텔카스텐 원칙](https://zettelkasten.de/posts/overview/)
- [AI4PKM 온보딩](https://pub.aiforbetter.me/guide/onboarding-scenario-2026-01/)
- [Notion API Docs](https://developers.notion.com/)

---

**Created:** 2026-01-30  
**For:** DSUComfyCG AI Animation Pipeline  
**By:** 아르카 (Arca) 🦊
