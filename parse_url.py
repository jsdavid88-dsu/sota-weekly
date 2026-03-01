#!/usr/bin/env python3
"""
SOTA Researcher - URL Parser CLI
URL에서 텍스트 추출 (LLM 없음)

Usage:
    python parse_url.py <url> [--save] [--json]

Examples:
    python parse_url.py "https://arxiv.org/abs/2511.06953"
    python parse_url.py "https://github.com/torvalds/linux" --save
    python parse_url.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --json
"""

import sys
import json
import argparse
import asyncio
from extractors import URLRouter, ExtractedContent
from notion_api import save_to_notion_async, check_notion_connection


async def extract_url(url: str) -> ExtractedContent:
    """URL에서 콘텐츠 추출"""
    router = URLRouter()
    return await router.extract(url)


def format_output(content: ExtractedContent, as_json: bool = False) -> str:
    """출력 형식 지정"""
    if as_json:
        return json.dumps(content.to_dict(), indent=2, ensure_ascii=False)
    
    lines = [
        f"=" * 60,
        f"제목: {content.title}",
        f"출처: {content.source_type}",
        f"URL: {content.url}",
        f"작성자: {content.author or 'N/A'}",
        f"태그: {', '.join(content.tags) if content.tags else 'N/A'}",
        f"추출시간: {content.extracted_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"=" * 60,
        "",
        "[본문 내용]",
        "-" * 60,
        content.content,
        "-" * 60,
    ]
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(
        description="URL에서 텍스트 추출 (YouTube, arXiv, GitHub, Article)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python parse_url.py "https://arxiv.org/abs/2511.06953"
  python parse_url.py "https://github.com/torvalds/linux"
  python parse_url.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --json
  python parse_url.py "https://arxiv.org/abs/2511.06953" --save
        """
    )
    
    parser.add_argument("url", help="추출할 URL")
    parser.add_argument("--save", "-s", action="store_true", 
                        help="Notion에 저장")
    parser.add_argument("--json", "-j", action="store_true",
                        help="JSON 형식으로 출력")
    parser.add_argument("--no-content", action="store_true",
                        help="본문 내용을 출력하지 않음 (제목/메타데이터만)")
    
    args = parser.parse_args()
    
    # URL 추출
    try:
        content = await extract_url(args.url)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 출력
    if not args.no_content or args.json:
        print(format_output(content, as_json=args.json))
    else:
        # 메타데이터만 출력
        print(f"제목: {content.title}")
        print(f"출처: {content.source_type}")
        print(f"URL: {content.url}")
    
    # Notion 저장
    if args.save:
        if not check_notion_connection():
            print("\n[!] Notion 연결 실패: 환경변수를 확인하세요 (NOTION_API_TOKEN, NOTION_DATABASE_ID)", file=sys.stderr)
            sys.exit(1)
        
        try:
            result = await save_to_notion_async(
                title=content.title,
                url=content.url,
                content=content.content,
                tags=content.tags,
                author=content.author,
                source_type=content.source_type
            )
            page_id = result.get('id', 'unknown')
            print(f"\n[✓] Notion에 저장됨: {page_id}")
        except Exception as e:
            print(f"\n[!] Notion 저장 실패: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
