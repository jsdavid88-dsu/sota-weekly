"""
SOTA 자동 수집 + 한글 번역 + 노션 저장
HuggingFace Daily Papers → 필터링 → 한글 번역 → 노션 DB

사용법:
  python auto_collect.py              # 기본 (상위 10개, 번역 포함)
  python auto_collect.py --limit 5    # 5개만
  python auto_collect.py --no-translate  # 번역 없이 빠르게
  python auto_collect.py --dry-run    # 저장 안 함, 미리보기만
"""
import argparse
from fetch_hf_daily import fetch_daily_papers, filter_relevant_papers, format_for_sota
from sota_weekly import save_sota_item, get_current_week
from translate_sota import translate_and_simplify, check_ollama_available

def auto_collect_and_save(limit: int = 10, dry_run: bool = False, translate: bool = True):
    """
    자동 수집 후 노션에 저장 (한글 번역 포함)
    """
    print(f"=== SOTA Auto-Collect ({get_current_week()}) ===\n")
    
    # 0. 번역 사용시 Ollama 확인
    use_translate = translate and check_ollama_available()
    if translate and not use_translate:
        print("⚠️  Ollama 연결 실패 - 번역 없이 진행합니다")
    elif use_translate:
        print("✅ Ollama 연결됨 - 한글 번역 활성화\n")
    
    # 1. HuggingFace에서 수집
    papers = fetch_daily_papers()
    print(f"📥 수집: {len(papers)}개")
    
    # 2. 관련 논문 필터링
    relevant = filter_relevant_papers(papers)
    print(f"🎯 필터링: {len(relevant)}개 관련")
    
    # 3. upvotes 기준 정렬 후 상위 N개
    sorted_papers = sorted(
        relevant, 
        key=lambda x: x.get('paper', {}).get('upvotes', 0), 
        reverse=True
    )[:limit]
    
    print(f"📊 상위 {len(sorted_papers)}개 선정\n")
    
    # 4. 노션에 저장
    results = []
    for i, paper_data in enumerate(sorted_papers, 1):
        formatted = format_for_sota(paper_data)
        
        print(f"{i}. [{formatted['category']}] {formatted['title'][:50]}...")
        print(f"   votes: {formatted['upvotes']} | {formatted['relevance']}")
        
        # 한글 번역
        if use_translate:
            print("   🔄 번역 중...")
            translated = translate_and_simplify(formatted['title'], formatted['summary'])
            title_display = translated['title_ko']
            summary_display = translated['summary_ko']
            simple_explain = translated['simple_explain']
            
            # 요약에 쉬운 설명 추가
            if simple_explain:
                summary_display = f"{summary_display}\n\n💡 쉬운 설명: {simple_explain}"
            
            print(f"   📝 {title_display[:40]}...")
        else:
            title_display = formatted['title']
            summary_display = formatted['summary']
        
        if dry_run:
            print("   [DRY RUN] 저장 스킵")
            results.append({'title': formatted['title'], 'dry_run': True})
        else:
            # 노션에 저장 (한글 요약 사용)
            result = save_sota_item(
                title=title_display[:100] if use_translate else formatted['title'][:100],
                url=formatted['url'],
                summary_kr=summary_display,
                category=formatted['category'],
                relevance=formatted['relevance'],
                testability='🔧커스텀필요',
                industry_insight='',
                tags=['HuggingFace', 'AutoCollect', '한글']
            )
            
            if result['success']:
                print(f"   ✅ 저장 완료: {result['url']}")
            else:
                print(f"   ❌ 저장 실패: {result.get('error', 'Unknown')[:50]}")
            
            results.append(result)
        print()
    
    # 5. 결과 요약
    success_count = sum(1 for r in results if r.get('success') or r.get('dry_run'))
    print(f"=== 완료: {success_count}/{len(results)} ===")
    
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SOTA 자동 수집 (한글 번역)')
    parser.add_argument('--limit', type=int, default=10, help='수집 개수 (기본: 10)')
    parser.add_argument('--dry-run', action='store_true', help='저장 안 함, 미리보기')
    parser.add_argument('--no-translate', action='store_true', help='번역 없이 영어로')
    args = parser.parse_args()
    
    auto_collect_and_save(
        limit=args.limit, 
        dry_run=args.dry_run, 
        translate=not args.no_translate
    )
