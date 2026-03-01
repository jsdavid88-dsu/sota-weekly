"""
SOTA Weekly - 핵심 모듈
수집 → 분석 → 저장 → 리포트
"""

import httpx
import os
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(env_path)

TOKEN = os.getenv('NOTION_API_TOKEN')
DB_ID = os.getenv('NOTION_DATABASE_ID')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}


def get_current_week() -> str:
    """현재 주차 반환 (예: 2026-W06)"""
    now = datetime.now()
    return f"{now.year}-W{now.isocalendar()[1]:02d}"


def save_sota_item(
    title: str,
    url: str,
    summary_kr: str,
    category: str = "AI생성",
    relevance: str = "⭐관심",
    testability: str = "🔧커스텀필요",
    industry_insight: str = "",
    related_links: str = "",
    tags: List[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    SOTA 항목을 노션에 저장 (새 스키마)
    
    Args:
        title: 제목
        url: 원본 URL
        summary_kr: 한국어 요약
        category: 카테고리 (AI생성/3D재구성/에이전트/영상/오디오/워크플로우)
        relevance: 관련성 (🔥핵심/⭐관심/📌참고)
        testability: 실증가능성 (✅바로가능/🔧커스텀필요/❌코드미공개/💻GPU필요)
        industry_insight: 산업 적용 인사이트
        related_links: 관련 링크들
        tags: 태그 리스트
    """
    
    # 페이지 속성 구성
    properties = {
        "이름": {
            "title": [{"text": {"content": title[:100]}}]  # 100자 제한
        },
        "URL": {
            "url": url
        },
        "요약": {
            "rich_text": [{"text": {"content": summary_kr[:2000]}}]  # 2000자 제한
        },
        "카테고리": {
            "select": {"name": category}
        },
        "관련성": {
            "select": {"name": relevance}
        },
        "실증가능성": {
            "select": {"name": testability}
        },
        "상태": {
            "select": {"name": "🆕신규"}
        },
        "담당자": {
            "select": {"name": "아르카"}
        },
        "날짜": {
            "date": {"start": datetime.now().strftime("%Y-%m-%d")}
        },
        "주차": {
            "select": {"name": get_current_week()}
        }
    }
    
    # 선택적 필드
    if industry_insight:
        properties["산업적용"] = {
            "rich_text": [{"text": {"content": industry_insight[:2000]}}]
        }
    
    if related_links:
        properties["관련링크"] = {
            "rich_text": [{"text": {"content": related_links[:2000]}}]
        }
    
    if tags:
        properties["태그"] = {
            "multi_select": [{"name": tag} for tag in tags[:5]]  # 최대 5개
        }
    
    # API 요청
    payload = {
        "parent": {"database_id": DB_ID},
        "properties": properties
    }
    
    # 페이지 본문 블록 추가 (심층 분석 리포트용)
    if kwargs.get("body_blocks"):
        payload["children"] = kwargs["body_blocks"]
    
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            "https://api.notion.com/v1/pages",
            headers=HEADERS,
            json=payload
        )
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": True,
            "page_id": result.get("id"),
            "url": result.get("url"),
            "title": title
        }
    else:
        return {
            "success": False,
            "error": response.text,
            "title": title
        }


def make_report_blocks(sections: List[Dict[str, str]]) -> list:
    """
    심층 분석 리포트를 노션 페이지 본문 블록으로 변환.
    sections: [{"heading": "제목", "content": "내용"}, ...]
    """
    blocks = []
    for section in sections:
        if section.get("heading"):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": section["heading"]}}]
                }
            })
        if section.get("content"):
            # 노션 블록 텍스트 2000자 제한 → 분할
            content = section["content"]
            for i in range(0, len(content), 2000):
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content[i:i+2000]}}]
                    }
                })
    return blocks


def check_github_code(url: str) -> bool:
    """GitHub URL에서 코드 공개 여부 확인"""
    if "github.com" not in url:
        return False
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.head(url, follow_redirects=True)
            return response.status_code == 200
    except:
        return False


def extract_links_from_text(text: str) -> List[str]:
    """텍스트에서 URL 추출"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # 중복 제거


def determine_testability(abstract: str, has_github: bool) -> str:
    """실증가능성 자동 판단"""
    if has_github:
        return "✅바로가능"
    
    # 키워드 기반 판단
    lower_text = abstract.lower()
    
    if any(word in lower_text for word in ["code available", "github", "open source", "code release"]):
        return "✅바로가능"
    elif any(word in lower_text for word in ["a100", "h100", "8x", "multi-gpu"]):
        return "💻GPU필요"
    elif any(word in lower_text for word in ["proprietary", "commercial", "api only"]):
        return "❌코드미공개"
    else:
        return "🔧커스텀필요"


def determine_category(title: str, abstract: str) -> str:
    """카테고리 자동 분류"""
    text = (title + " " + abstract).lower()
    
    if any(word in text for word in ["agent", "multi-agent", "orchestrat", "llm agent", "autonomous"]):
        return "에이전트"
    elif any(word in text for word in ["gaussian", "3d reconstruction", "nerf", "3dgs", "point cloud", "mesh"]):
        return "3D재구성"
    elif any(word in text for word in ["video", "motion", "animation", "temporal", "frame"]):
        return "영상"
    elif any(word in text for word in ["audio", "speech", "tts", "music", "voice", "sound"]):
        return "오디오"
    elif any(word in text for word in ["workflow", "pipeline", "automation", "comfyui"]):
        return "워크플로우"
    else:
        return "AI생성"


def determine_relevance(title: str, abstract: str) -> str:
    """관련성 자동 판단 (준석 관심사 기준)"""
    text = (title + " " + abstract).lower()
    
    # 핵심 키워드 (준석 직접 관심)
    core_keywords = [
        "comfyui", "gaussian splatting", "3dgs", "animatediff", "controlnet",
        "ip-adapter", "flux", "stable diffusion", "character consistency",
        "multi-agent", "orchestrat"
    ]
    
    # 관심 키워드
    interest_keywords = [
        "video generation", "image generation", "diffusion", "transformer",
        "lora", "fine-tuning", "real-time", "neural rendering"
    ]
    
    if any(kw in text for kw in core_keywords):
        return "🔥핵심"
    elif any(kw in text for kw in interest_keywords):
        return "⭐관심"
    else:
        return "📌참고"


# CLI 테스트
if __name__ == "__main__":
    # 테스트 저장
    result = save_sota_item(
        title="테스트 논문 - SOTA Weekly",
        url="https://arxiv.org/abs/test",
        summary_kr="이것은 테스트 요약입니다. 한국어로 작성됩니다.",
        category="에이전트",
        relevance="⭐관심",
        testability="✅바로가능",
        industry_insight="영상 제작 스튜디오에서 자동화 파이프라인에 적용 가능",
        tags=["테스트", "SOTA"]
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
