"""
HuggingFace Daily Papers 자동 수집
"""
import httpx
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

def fetch_daily_papers(date: str = None) -> List[Dict[str, Any]]:
    """
    HuggingFace Daily Papers API에서 논문 가져오기
    
    Args:
        date: YYYY-MM-DD 형식, None이면 오늘
    
    Returns:
        논문 리스트
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # date 파라미터 없이 호출하면 최신 데이터 반환
    url = 'https://huggingface.co/api/daily_papers'
    
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return []


def filter_relevant_papers(papers: List[Dict], keywords: List[str] = None) -> List[Dict]:
    """
    관련 논문 필터링 (준석 관심사 기준)
    """
    if keywords is None:
        keywords = [
            # 핵심 관심사
            'diffusion', 'generation', 'video', 'image', 'animation',
            'gaussian', '3d', 'nerf', 'reconstruction',
            'agent', 'multi-agent', 'orchestrat', 'llm',
            'comfyui', 'stable diffusion', 'flux',
            # 추가 관심사
            'controlnet', 'lora', 'fine-tun', 'real-time',
            'transformer', 'attention', 'efficient'
        ]
    
    relevant = []
    for paper_data in papers:
        paper = paper_data.get('paper', {})
        title = paper.get('title', '').lower()
        summary = paper.get('summary', '').lower()
        text = title + ' ' + summary
        
        if any(kw in text for kw in keywords):
            relevant.append(paper_data)
    
    return relevant


def format_for_sota(paper_data: Dict) -> Dict[str, str]:
    """
    SOTA Weekly 저장 형식으로 변환
    """
    paper = paper_data.get('paper', {})
    
    # 카테고리 자동 분류
    title = paper.get('title', '')
    summary = paper.get('summary', '')
    text = (title + ' ' + summary).lower()
    
    if any(w in text for w in ['agent', 'multi-agent', 'orchestrat']):
        category = '에이전트'
    elif any(w in text for w in ['gaussian', '3d', 'nerf', 'reconstruction']):
        category = '3D재구성'
    elif any(w in text for w in ['video', 'motion', 'animation', 'temporal']):
        category = '영상'
    elif any(w in text for w in ['audio', 'speech', 'tts', 'music']):
        category = '오디오'
    else:
        category = 'AI생성'
    
    # 관련성 판단
    core_kw = ['comfyui', 'gaussian splatting', 'animatediff', 'controlnet', 
               'ip-adapter', 'flux', 'multi-agent']
    if any(kw in text for kw in core_kw):
        relevance = '🔥핵심'
    else:
        relevance = '⭐관심'
    
    return {
        'title': title,
        'url': f"https://huggingface.co/papers/{paper.get('id', '')}",
        'arxiv_id': paper.get('id', ''),
        'summary': summary[:500] + '...' if len(summary) > 500 else summary,
        'authors': paper.get('authors', []),
        'category': category,
        'relevance': relevance,
        'upvotes': paper_data.get('paper', {}).get('upvotes', 0)
    }


if __name__ == '__main__':
    print(f"=== HuggingFace Daily Papers ({datetime.now().strftime('%Y-%m-%d')}) ===\n")
    
    papers = fetch_daily_papers()
    print(f"전체: {len(papers)}개")
    
    relevant = filter_relevant_papers(papers)
    print(f"관련: {len(relevant)}개\n")
    
    print("--- 관련 논문 TOP 5 ---")
    for i, p in enumerate(relevant[:5], 1):
        formatted = format_for_sota(p)
        print(f"{i}. [{formatted['category']}] {formatted['title'][:60]}...")
        print(f"   {formatted['relevance']} | upvotes: {formatted['upvotes']}")
        print(f"   {formatted['url']}")
        print()
