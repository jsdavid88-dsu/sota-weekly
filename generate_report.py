"""
SOTA Weekly - 자동 리포트 생성기
노션 DB에서 데이터 가져와서 풍부한 위클리 리포트 생성
"""

import httpx
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv('config/.env')

TOKEN = os.getenv('NOTION_API_TOKEN')
DB_ID = os.getenv('NOTION_DATABASE_ID')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}


def get_week_items(week: str = None) -> List[Dict]:
    """특정 주차의 SOTA 항목들 가져오기"""
    if week is None:
        now = datetime.now()
        week = f"{now.year}-W{now.isocalendar()[1]:02d}"
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f'https://api.notion.com/v1/databases/{DB_ID}/query',
            headers=HEADERS,
            json={
                "filter": {
                    "property": "주차",
                    "select": {"equals": week}
                },
                "sorts": [
                    {"property": "관련성", "direction": "ascending"}  # 핵심이 먼저
                ]
            }
        )
    
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return []
    
    results = response.json().get('results', [])
    items = []
    
    for page in results:
        props = page.get('properties', {})
        
        # 제목 추출
        title_prop = props.get('이름', {}).get('title', [])
        title = title_prop[0].get('text', {}).get('content', '') if title_prop else ''
        
        # URL 추출
        url = props.get('URL', {}).get('url', '')
        
        # 요약 추출
        summary_prop = props.get('요약', {}).get('rich_text', [])
        summary = summary_prop[0].get('text', {}).get('content', '') if summary_prop else ''
        
        # 산업적용 추출
        insight_prop = props.get('산업적용', {}).get('rich_text', [])
        insight = insight_prop[0].get('text', {}).get('content', '') if insight_prop else ''
        
        # Select 필드들
        category = props.get('카테고리', {}).get('select', {})
        category = category.get('name', '') if category else ''
        
        relevance = props.get('관련성', {}).get('select', {})
        relevance = relevance.get('name', '') if relevance else ''
        
        testability = props.get('실증가능성', {}).get('select', {})
        testability = testability.get('name', '') if testability else ''
        
        status = props.get('상태', {}).get('select', {})
        status = status.get('name', '') if status else ''
        
        # 태그
        tags = props.get('태그', {}).get('multi_select', [])
        tags = [t.get('name', '') for t in tags]
        
        items.append({
            'title': title,
            'url': url,
            'summary': summary,
            'insight': insight,
            'category': category,
            'relevance': relevance,
            'testability': testability,
            'status': status,
            'tags': tags
        })
    
    return items


def generate_weekly_report(week: str = None) -> str:
    """주간 리포트 마크다운 생성"""
    if week is None:
        now = datetime.now()
        week = f"{now.year}-W{now.isocalendar()[1]:02d}"
    
    # 주차에서 날짜 범위 계산
    year, week_num = int(week.split('-W')[0]), int(week.split('-W')[1])
    first_day = datetime.strptime(f'{year}-W{week_num}-1', '%Y-W%W-%w')
    last_day = first_day + timedelta(days=6)
    date_range = f"{first_day.month}/{first_day.day} ~ {last_day.month}/{last_day.day}"
    
    items = get_week_items(week)
    
    if not items:
        return f"# {week} - 데이터 없음"
    
    # 카테고리별 분류
    by_category = {}
    core_items = []  # 🔥핵심
    
    for item in items:
        cat = item['category'] or '기타'
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
        
        if '핵심' in item['relevance']:
            core_items.append(item)
    
    # 통계
    total = len(items)
    core_count = len(core_items)
    testable_count = len([i for i in items if '바로가능' in i['testability']])
    
    # 리포트 생성
    report = f'''# 🔬 가상융합기술연구원 SOTA Weekly
## {year}년 {first_day.month}월 {week_num}주차 ({date_range})

> **동서대학교 글로컬30 가상융합기술연구원**
> AI·XR·영상 기술 최신 동향 리포트

---

## 📌 이번 주 핵심 {core_count}선

'''
    
    # 핵심 항목들
    for i, item in enumerate(core_items[:5], 1):
        report += generate_item_section(item, i, detailed=True)
    
    report += '\n---\n\n'
    
    # 카테고리별 섹션
    category_emoji = {
        '에이전트': '🤖',
        'AI생성': '🎨',
        '3D재구성': '🧊',
        '영상': '🎬',
        '오디오': '🔊',
        '워크플로우': '⚙️'
    }
    
    for cat, cat_items in by_category.items():
        emoji = category_emoji.get(cat, '📁')
        non_core = [i for i in cat_items if '핵심' not in i['relevance']]
        
        if non_core:
            report += f'## {emoji} {cat}\n\n'
            for item in non_core:
                report += generate_item_section(item, detailed=False)
            report += '\n---\n\n'
    
    # 통계
    report += f'''## 📊 이번 주 통계

| 항목 | 수치 |
|------|------|
| 총 수집 | {total}개 |
| 🔥 핵심 | {core_count}개 |
| ✅ 즉시 실증 가능 | {testable_count}개 |

---

## 🔬 실증 권장 항목

코드가 공개되어 **이번 주 내 테스트 가능**한 항목:

'''
    
    testable = [i for i in items if '바로가능' in i['testability']]
    for i, item in enumerate(testable[:5], 1):
        report += f"{i}. **{item['title']}**"
        if item['tags']:
            report += f" ({', '.join(item['tags'][:3])})"
        report += '\n'
    
    report += f'''
---

## 🔗 전체 데이터베이스

[→ Notion SOTA Database 바로가기](https://www.notion.so/{DB_ID.replace('-', '')})

---

**발행**: 동서대학교 글로컬30 가상융합기술연구원  
**발행일**: {datetime.now().strftime('%Y년 %m월 %d일')}  
**문의**: jsdavid88@g.dongseo.ac.kr

---

*© {year} 동서대학교 가상융합기술연구원*
'''
    
    return report


def generate_item_section(item: Dict, index: int = None, detailed: bool = True) -> str:
    """개별 항목 섹션 생성"""
    
    title = item['title']
    if index:
        title = f"{index}. {title}"
    
    # 한 줄 요약 (요약의 첫 문장)
    summary_first = item['summary'].split('.')[0] + '.' if item['summary'] else ''
    
    if detailed:
        section = f'''<details markdown="1">
<summary><strong>{title}</strong> — {summary_first[:60]}</summary>

{item['summary']}

| 항목 | 내용 |
|------|------|
| 📄 링크 | [{item['url'][:50]}...]({item['url']}) |
| 🏷️ 카테고리 | {item['category']} |
| 🎯 관련성 | {item['relevance']} |
| 🧪 실증가능성 | {item['testability']} |
| 🏷️ 태그 | {', '.join(item['tags']) if item['tags'] else '-'} |

'''
        if item['insight']:
            section += f'''**🏭 산업 적용 인사이트**

{item['insight']}

'''
        section += '</details>\n\n'
    else:
        section = f'''<details markdown="1">
<summary><strong>{title}</strong> — {summary_first[:80]}</summary>

{item['summary']}

- **링크**: [{item['url'][:40]}...]({item['url']})
- **실증가능성**: {item['testability']}

</details>

'''
    
    return section


def save_report(week: str = None):
    """리포트 생성 및 저장"""
    if week is None:
        now = datetime.now()
        week = f"{now.year}-W{now.isocalendar()[1]:02d}"
    
    report = generate_weekly_report(week)
    
    output_path = os.path.join(os.path.dirname(__file__), 'reports', f'{week}.md')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 리포트 저장: {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    
    week = sys.argv[1] if len(sys.argv) > 1 else None
    save_report(week)
