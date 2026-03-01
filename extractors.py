"""
SOTA Researcher - URL Extractors
URL에서 텍스트를 추출하는 모듈 (LLM 없음)
"""

import re
import httpx
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from urllib.parse import urlparse


# ============================================================================
# Base Classes
# ============================================================================

@dataclass
class ExtractedContent:
    """추출된 콘텐츠 데이터 클래스"""
    title: str
    content: str
    url: str
    source_type: str
    extracted_at: datetime
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
    
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source_type': self.source_type,
            'extracted_at': self.extracted_at.isoformat(),
            'author': self.author,
            'tags': self.tags or [],
            'metadata': self.metadata or {}
        }


class BaseExtractor(ABC):
    """URL에서 콘텐츠를 추출하는 기본 클래스"""
    
    @property
    @abstractmethod
    def source_type(self) -> str:
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        pass
    
    @abstractmethod
    async def extract(self, url: str) -> ExtractedContent:
        pass


# ============================================================================
# YouTube Extractor
# ============================================================================

class YouTubeExtractor(BaseExtractor):
    """유튜브 동영상에서 자막 추출"""
    
    YOUTUBE_PATTERNS = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    
    @property
    def source_type(self) -> str:
        return "YouTube"
    
    def can_handle(self, url: str) -> bool:
        return any(re.search(pattern, url) for pattern in self.YOUTUBE_PATTERNS)
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def extract(self, url: str) -> ExtractedContent:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            raise ImportError("youtube_transcript_api 필요: pip install youtube-transcript-api")
        
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError(f"유효한 YouTube URL이 아닙니다: {url}")
        
        try:
            ytt_api = YouTubeTranscriptApi()
            fetched = ytt_api.fetch(video_id, languages=['ko', 'en'])
            content = ' '.join([snippet.text for snippet in fetched])
        except Exception as e:
            raise Exception(f"자막을 가져올 수 없습니다: {e}")
        
        return ExtractedContent(
            title=f"YouTube Video: {video_id}",
            content=content,
            url=url,
            source_type=self.source_type,
            extracted_at=datetime.now(),
            metadata={'video_id': video_id}
        )


# ============================================================================
# arXiv Extractor
# ============================================================================

class ArxivExtractor(BaseExtractor):
    """arXiv 논문 Abstract 추출"""
    
    ARXIV_PATTERNS = [
        r'arxiv\.org/abs/(\d+\.\d+)',
        r'arxiv\.org/pdf/(\d+\.\d+)',
    ]
    
    @property
    def source_type(self) -> str:
        return "arXiv"
    
    def can_handle(self, url: str) -> bool:
        return any(re.search(pattern, url) for pattern in self.ARXIV_PATTERNS)
    
    def _extract_paper_id(self, url: str) -> Optional[str]:
        for pattern in self.ARXIV_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def extract(self, url: str) -> ExtractedContent:
        try:
            import arxiv as arxiv_lib
        except ImportError:
            raise ImportError("arxiv 필요: pip install arxiv")
        
        paper_id = self._extract_paper_id(url)
        if not paper_id:
            raise ValueError(f"유효한 arXiv URL이 아닙니다: {url}")
        
        try:
            search = arxiv_lib.Search(id_list=[paper_id])
            paper = next(search.results())
        except Exception as e:
            raise Exception(f"논문을 가져올 수 없습니다: {e}")
        
        authors = [author.name for author in paper.authors]
        tags = list(paper.categories) if paper.categories else []
        
        metadata = {
            'paper_id': paper_id,
            'published': paper.published.isoformat() if paper.published else None,
            'pdf_url': paper.pdf_url,
            'primary_category': paper.primary_category,
        }
        
        content = f"""# {paper.title}

## Authors
{', '.join(authors)}

## Abstract
{paper.summary}

## Categories
{', '.join(tags)}
"""
        
        return ExtractedContent(
            title=paper.title,
            content=content,
            url=url,
            source_type=self.source_type,
            extracted_at=datetime.now(),
            author=', '.join(authors[:3]) + ('...' if len(authors) > 3 else ''),
            tags=tags,
            metadata=metadata
        )


# ============================================================================
# GitHub Extractor
# ============================================================================

class GitHubExtractor(BaseExtractor):
    """GitHub 레포지토리 README 추출"""
    
    GITHUB_PATTERN = r'github\.com/([^/]+)/([^/\?#]+)'
    
    @property
    def source_type(self) -> str:
        return "GitHub"
    
    def can_handle(self, url: str) -> bool:
        return bool(re.search(self.GITHUB_PATTERN, url))
    
    def _extract_repo_info(self, url: str) -> Optional[tuple]:
        match = re.search(self.GITHUB_PATTERN, url)
        if match:
            return match.group(1), match.group(2).split('/')[0]
        return None
    
    async def extract(self, url: str) -> ExtractedContent:
        repo_info = self._extract_repo_info(url)
        if not repo_info:
            raise ValueError(f"유효한 GitHub URL이 아닙니다: {url}")
        
        owner, repo = repo_info
        api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                headers={'Accept': 'application/vnd.github.raw'},
                follow_redirects=True
            )
            
            if response.status_code == 404:
                raise Exception(f"README를 찾을 수 없습니다: {owner}/{repo}")
            
            response.raise_for_status()
            content = response.text
            
            repo_response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                follow_redirects=True
            )
            
            metadata = {}
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                metadata = {
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0),
                    'language': repo_data.get('language'),
                    'description': repo_data.get('description'),
                    'topics': repo_data.get('topics', [])
                }
        
        return ExtractedContent(
            title=f"{owner}/{repo}",
            content=content,
            url=url,
            source_type=self.source_type,
            extracted_at=datetime.now(),
            author=owner,
            tags=metadata.get('topics', []),
            metadata=metadata
        )


# ============================================================================
# Article Extractor
# ============================================================================

class ArticleExtractor(BaseExtractor):
    """웹 아티클/블로그 본문 추출"""
    
    EXCLUDED_DOMAINS = [
        'youtube.com', 'youtu.be', 
        'github.com', 'raw.githubusercontent.com',
        'arxiv.org'
    ]
    
    @property
    def source_type(self) -> str:
        return "Article"
    
    def can_handle(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            for excluded in self.EXCLUDED_DOMAINS:
                if excluded in domain:
                    return False
            
            return parsed.scheme in ('http', 'https')
        except:
            return False
    
    async def extract(self, url: str) -> ExtractedContent:
        try:
            from newspaper import Article as NewspaperArticle
        except ImportError:
            raise ImportError("newspaper3k 필요: pip install newspaper3k")
        
        article = NewspaperArticle(url, language='ko')
        
        try:
            article.download()
            article.parse()
        except Exception as e:
            raise Exception(f"아티클을 가져올 수 없습니다: {e}")
        
        title = article.title or "제목 없음"
        content = article.text or ""
        
        if not content:
            raise Exception("본문을 추출할 수 없습니다")
        
        metadata = {}
        if article.publish_date:
            metadata['publish_date'] = article.publish_date.isoformat()
        if article.top_image:
            metadata['image'] = article.top_image
        
        authors = list(article.authors) if article.authors else None
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            source_type=self.source_type,
            extracted_at=datetime.now(),
            author=', '.join(authors) if authors else None,
            tags=list(article.keywords) if article.keywords else None,
            metadata=metadata
        )


# ============================================================================
# URL Router
# ============================================================================

class URLRouter:
    """URL을 분석하여 적절한 추출기를 선택"""
    
    def __init__(self):
        self.extractors = [
            YouTubeExtractor(),
            GitHubExtractor(),
            ArxivExtractor(),
            ArticleExtractor(),
        ]
    
    def get_extractor(self, url: str) -> Optional[BaseExtractor]:
        for extractor in self.extractors:
            if extractor.can_handle(url):
                return extractor
        return None
    
    async def extract(self, url: str) -> ExtractedContent:
        extractor = self.get_extractor(url)
        if not extractor:
            raise ValueError(f"지원하지 않는 URL 형식입니다: {url}")
        return await extractor.extract(url)
    
    def get_source_type(self, url: str) -> Optional[str]:
        extractor = self.get_extractor(url)
        return extractor.source_type if extractor else None


# ============================================================================
# Helper Functions
# ============================================================================

def extract_from_url(url: str) -> ExtractedContent:
    """동기식 URL 추출 헬퍼"""
    import asyncio
    router = URLRouter()
    return asyncio.run(router.extract(url))
