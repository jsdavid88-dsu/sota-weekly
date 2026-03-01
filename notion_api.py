"""
SOTA Researcher - Notion API Wrapper
Notion 데이터베이스에 콘텐츠 저장 (LLM 없음)
"""

import httpx
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()


def save_to_notion(
    title: str,
    url: str,
    content: str,
    tags: List[str] = None,
    author: Optional[str] = None,
    source_type: str = "Unknown",
    api_token: str = None,
    database_id: str = None
) -> Dict[str, Any]:
    """
    콘텐츠를 Notion 데이터베이스에 저장 (동기 함수)
    
    Args:
        title: 페이지 제목
        url: 원본 URL
        content: 본문 내용 (요약 없이 전체 텍스트)
        tags: 태그 리스트 (선택)
        author: 작성자 (선택)
        source_type: 출처 타입 (YouTube, arXiv, GitHub, Article)
        api_token: Notion API token (없으면 환경변수 사용)
        database_id: Notion database ID (없으면 환경변수 사용)
    
    Returns:
        생성된 페이지 정보 (dict)
    
    Raises:
        Exception: API 호출 실패 시
    """
    token = api_token or os.getenv('NOTION_API_TOKEN')
    db_id = database_id or os.getenv('NOTION_DATABASE_ID')
    
    if not token:
        raise ValueError("Notion API token이 필요합니다. 환경변수 NOTION_API_TOKEN을 설정하거나 api_token 인자를 전달하세요.")
    if not db_id:
        raise ValueError("Notion Database ID가 필요합니다. 환경변수 NOTION_DATABASE_ID를 설정하거나 database_id 인자를 전달하세요.")
    
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 페이지 속성 구성
    properties = {
        "이름": {
            "title": [{"text": {"content": title[:100]}}]
        },
        "URL": {
            "url": url
        },
        "요약": {
            "rich_text": [{"text": {"content": content[:2000]}}]
        },
        "연계아이디어": {
            "rich_text": [{"text": {"content": f"Source: {source_type}"}}]
        },
        "출처타입": {
            "select": {"name": source_type}
        },
        "날짜": {
            "date": {"start": datetime.now().strftime("%Y-%m-%d")}
        }
    }
    
    # 태그 추가 (기존 옵션에 있는 것만)
    if tags:
        valid_tags = ["AI", "개발", "아이디어", "논문", "YouTube"]
        filtered_tags = [t for t in tags if t in valid_tags]
        if filtered_tags:
            properties["태그"] = {
                "multi_select": [{"name": tag} for tag in filtered_tags[:5]]
            }
    
    # 페이지 생성
    payload = {
        "parent": {"database_id": db_id},
        "properties": properties
    }
    
    response = httpx.post(
        f"{base_url}/pages",
        headers=headers,
        json=payload
    )
    
    response.raise_for_status()
    return response.json()


async def save_to_notion_async(
    title: str,
    url: str,
    content: str,
    tags: List[str] = None,
    author: Optional[str] = None,
    source_type: str = "Unknown",
    api_token: str = None,
    database_id: str = None
) -> Dict[str, Any]:
    """
    콘텐츠를 Notion 데이터베이스에 저장 (비동기 함수)
    """
    token = api_token or os.getenv('NOTION_API_TOKEN')
    db_id = database_id or os.getenv('NOTION_DATABASE_ID')
    
    if not token:
        raise ValueError("Notion API token이 필요합니다.")
    if not db_id:
        raise ValueError("Notion Database ID가 필요합니다.")
    
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    properties = {
        "이름": {
            "title": [{"text": {"content": title[:100]}}]
        },
        "URL": {
            "url": url
        },
        "요약": {
            "rich_text": [{"text": {"content": content[:2000]}}]
        },
        "연계아이디어": {
            "rich_text": [{"text": {"content": f"Source: {source_type}"}}]
        },
        "출처타입": {
            "select": {"name": source_type}
        },
        "날짜": {
            "date": {"start": datetime.now().strftime("%Y-%m-%d")}
        }
    }
    
    if tags:
        valid_tags = ["AI", "개발", "아이디어", "논문", "YouTube"]
        filtered_tags = [t for t in tags if t in valid_tags]
        if filtered_tags:
            properties["태그"] = {
                "multi_select": [{"name": tag} for tag in filtered_tags[:5]]
            }
    
    payload = {
        "parent": {"database_id": db_id},
        "properties": properties
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/pages",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()


def check_notion_connection(
    api_token: str = None,
    database_id: str = None
) -> bool:
    """Notion API 연결 확인"""
    token = api_token or os.getenv('NOTION_API_TOKEN')
    db_id = database_id or os.getenv('NOTION_DATABASE_ID')
    
    if not token or not db_id:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = httpx.get(
            f"https://api.notion.com/v1/databases/{db_id}",
            headers=headers
        )
        return response.status_code == 200
    except:
        return False
