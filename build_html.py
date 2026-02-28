"""
SOTA Weekly - Markdown → HTML 변환기
"""

import markdown
import os
from datetime import datetime

# HTML 템플릿
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #2563eb;
            --bg: #f8fafc;
            --card: #ffffff;
            --text: #1e293b;
            --muted: #64748b;
            --border: #e2e8f0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        header {{
            text-align: center;
            padding: 2rem 0;
            border-bottom: 2px solid var(--primary);
            margin-bottom: 2rem;
        }}
        header h1 {{
            font-size: 1.8rem;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        header p {{
            color: var(--muted);
            font-size: 0.9rem;
        }}
        .logo {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        h1 {{ font-size: 1.6rem; margin: 2rem 0 1rem; color: var(--primary); }}
        h2 {{ font-size: 1.3rem; margin: 1.5rem 0 0.8rem; color: var(--text); border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }}
        h3 {{ font-size: 1.1rem; margin: 1.2rem 0 0.5rem; }}
        p {{ margin: 0.8rem 0; }}
        a {{ color: var(--primary); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        th, td {{
            border: 1px solid var(--border);
            padding: 0.6rem;
            text-align: left;
        }}
        th {{
            background: var(--bg);
            font-weight: 600;
        }}
        code {{
            background: #f1f5f9;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.85em;
        }}
        blockquote {{
            border-left: 4px solid var(--primary);
            padding-left: 1rem;
            margin: 1rem 0;
            color: var(--muted);
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 1px solid var(--border);
            margin: 2rem 0;
        }}
        ul, ol {{
            margin: 0.8rem 0;
            padding-left: 1.5rem;
        }}
        li {{ margin: 0.3rem 0; }}
        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        details {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin: 0.8rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            overflow: hidden;
        }}
        details summary {{
            padding: 1rem 1.2rem;
            cursor: pointer;
            font-weight: 500;
            list-style: none;
        }}
        details summary::-webkit-details-marker {{
            display: none;
        }}
        details summary::before {{
            content: "▶ ";
            font-size: 0.75rem;
        }}
        details[open] summary::before {{
            content: "▼ ";
        }}
        details[open] summary {{
            border-bottom: 1px solid var(--border);
            background: var(--bg);
        }}
        details > :not(summary) {{
            padding: 0 1.2rem;
        }}
        details p:last-child, details table:last-child {{
            margin-bottom: 1rem;
        }}
        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--muted);
            font-size: 0.85rem;
        }}
        @media (max-width: 600px) {{
            .container {{ padding: 1rem; }}
            h1 {{ font-size: 1.4rem; }}
            table {{ font-size: 0.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🔬</div>
            <h1>가상융합기술연구원</h1>
            <p>동서대학교 글로컬30 | AI·XR·영상 기술 동향</p>
        </header>
        <main>
            {content}
        </main>
        <footer>
            <p>© 2026 동서대학교 가상융합기술연구원</p>
            <p>편집: AI 리서치 어시스턴트 아르카</p>
        </footer>
    </div>
</body>
</html>
'''


def build_html(md_path: str, output_path: str = None):
    """Markdown 파일을 HTML로 변환"""
    
    # Markdown 읽기
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 첫 번째 h1을 제목으로 추출
    lines = md_content.split('\n')
    title = "SOTA Weekly"
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    # Markdown → HTML 변환
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc', 'md_in_html']
    )
    
    # 템플릿에 삽입
    full_html = HTML_TEMPLATE.format(
        title=title,
        content=html_content
    )
    
    # 출력 경로 결정
    if output_path is None:
        output_path = md_path.replace('.md', '.html')
    
    # HTML 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ HTML 생성 완료: {output_path}")
    return output_path


def build_all_reports():
    """reports 폴더의 모든 MD를 HTML로 변환"""
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    output_dir = os.path.join(os.path.dirname(__file__), 'public')
    
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(reports_dir):
        if filename.endswith('.md'):
            md_path = os.path.join(reports_dir, filename)
            html_path = os.path.join(output_dir, filename.replace('.md', '.html'))
            build_html(md_path, html_path)
    
    # index.html 생성
    create_index(output_dir)


def create_index(output_dir: str):
    """인덱스 페이지 생성"""
    html_files = [f for f in os.listdir(output_dir) if f.endswith('.html') and f != 'index.html']
    html_files.sort(reverse=True)
    
    links = '\n'.join([f'<li><a href="{f}">{f.replace(".html", "")}</a></li>' for f in html_files])
    
    index_content = f'''
# 🔬 SOTA Weekly Archive

> 동서대학교 글로컬30 가상융합기술연구원

## 📚 리포트 목록

<ul>
{links}
</ul>

---

*최신 AI/XR/영상 기술 동향을 매주 정리합니다.*
'''
    
    index_html = HTML_TEMPLATE.format(
        title="SOTA Weekly Archive",
        content=markdown.markdown(index_content)
    )
    
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    print(f"✅ 인덱스 생성 완료: {output_dir}/index.html")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        build_html(sys.argv[1])
    else:
        build_all_reports()
