from notion_api_v2 import save_to_notion

result = save_to_notion(
    title='bkit - Vibecoding Kit (PDCA + Claude Code)',
    url='https://github.com/popup-studio-ai/bkit-claude-code',
    content='PDCA methodology + AI coding assistant mastery for AI-native development. Context Engineering with 21 Skills, 11 Agents, 39 Scripts. 9-Stage Development Pipeline (Starter/Dynamic/Enterprise levels). Dual platform: Claude Code & Gemini CLI.',
    source_type='GitHub',
    tags=['AI', '개발'],
    projects=['교육'],  # bkit은 교육 도구
    difficulty='즉시 적용'
)

print('Page created!')
print('URL:', result['url'])
print('ID:', result['id'])

# Check auto-classification
props = result.get('properties', {})
if 'gineungyeoghal' in props:
    role = props['gineungyeoghal'].get('select', {}).get('name', 'None')
    print('Auto Role:', role)
if 'gisulseuteaeg' in props:
    techs = [t['name'] for t in props['gisulseuteaeg'].get('multi_select', [])]
    print('Auto Tech:', techs)
