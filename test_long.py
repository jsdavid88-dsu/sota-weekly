import httpx

title = "F-GRPO: Don't Let Your Policy Learn the Obvious and Focus on the Difficult"
summary = "Reinforcement Learning from Human Feedback (RLHF) has shown great potential for aligning language models with human values."

prompt = f"""다음 AI 논문을 한국어로 번역해. JSON만 출력해.

제목: {title[:80]}
요약: {summary[:300]}

JSON 형식으로만 응답:
{{"title_ko": "한글 제목", "summary_ko": "핵심 2문장", "simple_explain": "쉬운 설명 2문장"}}"""

with httpx.Client(timeout=60.0) as client:
    resp = client.post(
        'http://localhost:11434/api/generate',
        json={'model': 'qwen3:8b', 'prompt': prompt, 'stream': False, 'options': {'temperature': 0.3}}
    )
    result = resp.json()
    print('=== RAW RESPONSE ===')
    print(repr(result.get('response', '')))
