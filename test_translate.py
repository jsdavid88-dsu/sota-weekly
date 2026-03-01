import httpx

prompt = """다음 AI 논문을 한국어로 번역해. JSON만 출력해.

영어 제목: F-GRPO: Focus on Difficult Examples
영어 요약: RLHF has shown great potential.

응답 형식:
{"title_ko": "한글 제목", "summary_ko": "요약", "simple_explain": "설명"}"""

with httpx.Client(timeout=60.0) as client:
    resp = client.post(
        'http://localhost:11434/api/generate',
        json={'model': 'qwen3:8b', 'prompt': prompt, 'stream': False}
    )
    result = resp.json()
    print('=== RAW RESPONSE ===')
    print(result.get('response', ''))
