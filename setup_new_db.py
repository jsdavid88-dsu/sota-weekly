"""
SOTA Weekly - 노션 데이터베이스 스키마 업데이트
새 스키마로 속성 추가/수정
"""

import httpx
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

TOKEN = os.getenv('NOTION_API_TOKEN')
DB_ID = os.getenv('NOTION_DATABASE_ID')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

# 새 스키마 정의
NEW_PROPERTIES = {
    # 카테고리 (기존 태그 대체)
    "카테고리": {
        "select": {
            "options": [
                {"name": "AI생성", "color": "blue"},
                {"name": "3D재구성", "color": "green"},
                {"name": "에이전트", "color": "purple"},
                {"name": "영상", "color": "red"},
                {"name": "오디오", "color": "yellow"},
                {"name": "워크플로우", "color": "orange"}
            ]
        }
    },
    # 관련성
    "관련성": {
        "select": {
            "options": [
                {"name": "🔥핵심", "color": "red"},
                {"name": "⭐관심", "color": "yellow"},
                {"name": "📌참고", "color": "gray"}
            ]
        }
    },
    # 실증가능성
    "실증가능성": {
        "select": {
            "options": [
                {"name": "✅바로가능", "color": "green"},
                {"name": "🔧커스텀필요", "color": "yellow"},
                {"name": "❌코드미공개", "color": "red"},
                {"name": "💻GPU필요", "color": "purple"}
            ]
        }
    },
    # 상태
    "상태": {
        "select": {
            "options": [
                {"name": "🆕신규", "color": "blue"},
                {"name": "👀검토중", "color": "yellow"},
                {"name": "🔬실증요망", "color": "orange"},
                {"name": "✅실증완료", "color": "green"},
                {"name": "⏸️보류", "color": "gray"}
            ]
        }
    },
    # 담당자
    "담당자": {
        "select": {
            "options": [
                {"name": "준석", "color": "blue"},
                {"name": "아르카", "color": "purple"},
                {"name": "미정", "color": "gray"}
            ]
        }
    },
    # 실증노트
    "실증노트": {
        "rich_text": {}
    },
    # 관련링크 (원글에서 추출한 추가 링크)
    "관련링크": {
        "rich_text": {}
    },
    # 산업적용 (인사이트)
    "산업적용": {
        "rich_text": {}
    },
    # 파이프라인위치
    "파이프라인": {
        "select": {
            "options": [
                {"name": "프리프로덕션", "color": "gray"},
                {"name": "모델링", "color": "blue"},
                {"name": "애니메이션", "color": "green"},
                {"name": "텍스처링", "color": "yellow"},
                {"name": "라이팅/렌더링", "color": "orange"},
                {"name": "합성/VFX", "color": "red"},
                {"name": "전체", "color": "purple"}
            ]
        }
    },
    # 주차 (위클리 리포트용)
    "주차": {
        "select": {
            "options": [
                {"name": "2026-W06", "color": "blue"},
                {"name": "2026-W07", "color": "green"}
            ]
        }
    }
}


def update_database_schema():
    """데이터베이스 스키마 업데이트"""
    url = f'https://api.notion.com/v1/databases/{DB_ID}'
    
    payload = {
        "properties": NEW_PROPERTIES
    }
    
    response = httpx.patch(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        print("✅ 데이터베이스 스키마 업데이트 성공!")
        return response.json()
    else:
        print(f"❌ 실패: {response.status_code}")
        print(response.text)
        return None


def get_current_schema():
    """현재 스키마 확인"""
    url = f'https://api.notion.com/v1/databases/{DB_ID}'
    response = httpx.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print("=== 현재 스키마 ===")
        for name, prop in data.get('properties', {}).items():
            print(f"- {name}: {prop.get('type')}")
        return data
    else:
        print(f"❌ 조회 실패: {response.status_code}")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        print("스키마 업데이트 중...")
        update_database_schema()
    else:
        print("현재 스키마 조회 중...")
        get_current_schema()
        print("\n업데이트하려면: python setup_new_db.py --update")
