"""
SOTA Researcher - Notion API Wrapper v2.0
역할/기능 중심 분류 시스템
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


def auto_classify_role(title: str, content: str) -> Optional[str]:
    """
    제목과 내용 기반 역할/기능 자동 분류
    """
    text = (title + " " + content).lower()
    
    if any(word in text for word in ["character", "consistency", "캐릭터", "일관성", "ip-adapter", "lora"]):
        return "캐릭터 일관성 유지"
    elif any(word in text for word in ["3d", "gaussian", "splat", "reconstruction", "재구성"]):
        return "배경 3D 재구성"
    elif any(word in text for word in ["style", "stylize", "스타일", "변환"]):
        return "3D→2D 스타일 변환"
    elif any(word in text for word in ["lip", "sync", "립싱크", "음성"]):
        return "음성→립싱크 자동화"
    elif any(word in text for word in ["narrative", "story", "서사", "구조"]):
        return "서사 구조 시각화"
    elif any(word in text for word in ["temporal", "consistency", "시간", "일관성", "장면"]):
        return "장면 일관성 제어"
    elif any(word in text for word in ["long video", "긴 영상", "animatediff"]):
        return "긴 영상 생성"
    elif any(word in text for word in ["workflow", "automation", "워크플로우", "자동화"]):
        return "워크플로우 자동화"
    elif any(word in text for word in ["dcc", "maya", "nuke", "bridge", "연동"]):
        return "DCC 툴 연동"
    
    return None


def auto_classify_tech(title: str, content: str, tags: List[str] = None) -> List[str]:
    """
    기술 스택 자동 분류
    """
    text = (title + " " + content).lower()
    techs = []
    
    if "comfyui" in text or "comfy" in text:
        techs.append("ComfyUI")
    if "unreal" in text or "ue5" in text:
        techs.append("UE5")
    if "maya" in text:
        techs.append("Maya")
    if "nuke" in text:
        techs.append("Nuke")
    if "gaussian" in text or "splat" in text:
        techs.append("Gaussian Splatting")
    if "pytorch" in text or "torch" in text:
        techs.append("PyTorch")
    if "animatediff" in text:
        techs.append("AnimateDiff")
    
    # 태그 기반 추가
    if tags:
        tag_text = " ".join(tags).lower()
        if "comfyui" in tag_text and "ComfyUI" not in techs:
            techs.append("ComfyUI")
    
    return techs


def save_to_notion(
    title: str,
    url: str,
    content: str,
    tags: List[str] = None,
    author: Optional[str] = None,
    source_type: str = "Unknown",
    role: Optional[str] = None,  # 수동 분류
    projects: List[str] = None,  # 적용 영역
    tech_stack: List[str] = None,  # 기술 스택 (수동)
    difficulty: Optional[str] = None,  # 실행 난이도
    api_token: str = None,
    database_id: str = None
) -> Dict[str, Any]:
    """
    콘텐츠를 Notion 데이터베이스에 저장 (v2.0 - 역할 기반)
    
    Args:
        title: 페이지 제목
        url: 원본 URL
        content: 본문 내용
        tags: 태그 리스트 (선택)
        author: 작성자 (선택)
        source_type: 출처 타입 (YouTube, arXiv, GitHub, Article)
        role: 기능/역할 (None이면 자동 분류)
        projects: 적용 영역 리스트 (DSUComfyCG, 부산마법소녀 등)
        tech_stack: 기술 스택 (None이면 자동 분류)
        difficulty: 실행 난이도 (즉시 적용 / 커스터마이징 필요 / 연구 단계 / 개념만 참고)
        api_token: Notion API token
        database_id: Notion database ID
    
    Returns:
        생성된 페이지 정보 (dict)
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
    
    # 자동 분류
    if not role:
        role = auto_classify_role(title, content)
    
    if not tech_stack:
        tech_stack = auto_classify_tech(title, content, tags)
    
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
        "출처타입": {
            "select": {"name": source_type}
        },
        "날짜": {
            "date": {"start": datetime.now().strftime("%Y-%m-%d")}
        }
    }
    
    # 기능/역할
    if role:
        properties["기능역할"] = {"select": {"name": role}}
    
    # 적용 영역
    if projects:
        properties["적용영역"] = {
            "multi_select": [{"name": p} for p in projects[:5]]
        }
    
    # 기술 스택
    if tech_stack:
        properties["기술스택"] = {
            "multi_select": [{"name": t} for t in tech_stack[:7]]
        }
    
    # 실행 난이도
    if difficulty:
        properties["실행난이도"] = {"select": {"name": difficulty}}
    
    # 기존 태그 (호환성)
    if tags:
        valid_tags = ["AI", "개발", "아이디어", "논문", "YouTube"]
        filtered_tags = [t for t in tags if t in valid_tags]
        if filtered_tags:
            properties["태그"] = {
                "multi_select": [{"name": tag} for tag in filtered_tags[:5]]
            }
    
    # Ideas 필드
    if role or tech_stack:
        ideas = []
        if role:
            ideas.append(f"Role: {role}")
        if tech_stack:
            ideas.append(f"Tech: {', '.join(tech_stack)}")
        properties["연계아이디어"] = {
            "rich_text": [{"text": {"content": " | ".join(ideas)}}]
        }
    
    # 페이지 생성
    payload = {
        "parent": {"database_id": db_id},
        "properties": properties
    }
    
    response = httpx.post(
        f"{base_url}/pages",
        headers=headers,
        json=payload,
        timeout=30.0
    )
    
    response.raise_for_status()
    page_data = response.json()
    page_id = page_data["id"]
    
    # 본문 내용 추가 (blocks)
    if content and len(content) > 100:
        # 2000자씩 나눠서 paragraph blocks로 추가
        chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
        blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": chunk}}]
                }
            }
            for chunk in chunks[:10]  # 최대 10개 블록 (20,000자)
        ]
        
        # Blocks 추가
        if blocks:
            httpx.patch(
                f"{base_url}/blocks/{page_id}/children",
                headers=headers,
                json={"children": blocks},
                timeout=30.0
            )
    
    return page_data


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
            headers=headers,
            timeout=10.0
        )
        return response.status_code == 200
    except:
        return False


# 사용 예시
if __name__ == "__main__":
    # 테스트
    result = save_to_notion(
        title="GFix: Gaussian Splatting Compression Test",
        url="https://arxiv.org/abs/2511.06953",
        content="This paper presents GFix, a compression method for Gaussian Splatting that achieves 6x compression...",
        source_type="arXiv",
        tags=["AI", "논문"],
        # role은 자동 분류
        projects=["DSUComfyCG"],
        # tech_stack도 자동 분류
        difficulty="연구 단계"
    )
    print("Page created:", result['url'])
