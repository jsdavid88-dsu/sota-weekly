"""
HuggingFace Paper → Notion 저장
아르카가 사용하는 간단한 래퍼
"""

import sys
import json
from extractors import extract_from_url
from notion_api import save_to_notion


def save_paper(arxiv_id: str, category: str = None, relevance: str = None):
    """
    arXiv ID로 논문을 노션에 저장
    
    Args:
        arxiv_id: arXiv 논문 ID (예: "2505.19591")
        category: 카테고리 (예: "에이전트", "생성모델", "3D")
        relevance: 관련성 (높음/중간/낮음)
    """
    url = f"https://arxiv.org/abs/{arxiv_id}"
    
    try:
        # 논문 추출
        content = extract_from_url(url)
        
        # 태그 구성
        tags = list(content.tags) if content.tags else []
        if category:
            tags.append(category)
        
        # 요약 텍스트 구성
        summary = content.content[:2000] if content.content else ""
        if relevance:
            summary = f"[관련성: {relevance}]\n\n{summary}"
        
        # 노션 저장
        result = save_to_notion(
            title=content.title,
            url=url,
            content=summary,
            tags=tags,
            author=content.author,
            source_type="arXiv"
        )
        
        print(json.dumps({
            "success": True,
            "title": content.title,
            "notion_url": result.get("url", ""),
            "arxiv_id": arxiv_id
        }, ensure_ascii=False, indent=2))
        
        return result
        
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e),
            "arxiv_id": arxiv_id
        }, ensure_ascii=False, indent=2))
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python save_hf_paper.py <arxiv_id> [category] [relevance]")
        print("Example: python save_hf_paper.py 2505.19591 에이전트 높음")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    relevance = sys.argv[3] if len(sys.argv) > 3 else None
    
    save_paper(arxiv_id, category, relevance)
