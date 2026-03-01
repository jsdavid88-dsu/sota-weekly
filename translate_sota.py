"""
SOTA 논문 한글 번역 + 쉬운 설명
로컬 Ollama (qwen3:8b) 사용
"""
import httpx
import json
import re
from typing import Dict

OLLAMA_URL = "http://localhost:11434/api/generate"
PREFERRED_MODELS = ["qwen3:8b", "gpt-oss:latest", "gpt-oss:20b"]
MODEL = "qwen3:8b"  # resolve_translate_model()로 런타임 변경


def resolve_translate_model():
    """사용 가능한 모델 자동 선택"""
    global MODEL
    try:
        import httpx
        r = httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        available = [m["name"] for m in r.json().get("models", [])]
        for m in PREFERRED_MODELS:
            if m in available:
                MODEL = m
                return MODEL
        if available:
            MODEL = available[0]
    except:
        pass
    return MODEL

def translate_and_simplify(title: str, summary: str, max_retries: int = 2) -> Dict[str, str]:
    """
    영어 논문 제목/요약을 한글로 번역하고 쉽게 설명
    
    Returns:
        {
            "title_ko": "한글 제목",
            "summary_ko": "한글 요약",
            "simple_explain": "누구나 이해할 수 있는 쉬운 설명"
        }
    """
    prompt = f"""다음 AI 논문을 한국어로 번역해. JSON만 출력해.

제목: {title[:100]}
요약: {summary[:500]}

JSON 형식으로만 응답:
{{"title_ko": "한글 제목", "summary_ko": "핵심 2문장", "simple_explain": "쉬운 설명 2문장"}}"""

    resolve_translate_model()
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    OLLAMA_URL,
                    json={
                        "model": MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 1000
                        }
                    }
                )
                resp.raise_for_status()
                
                result = resp.json()
                text = result.get("response", "")
                
                # JSON 추출 (```json ... ``` 또는 그냥 JSON)
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]
                
                # JSON 파싱
                json_match = re.search(r'\{[^{}]*"title_ko"[^{}]*\}', text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = json.loads(text.strip())
                
                return {
                    "title_ko": parsed.get("title_ko", title),
                    "summary_ko": parsed.get("summary_ko", summary[:200]),
                    "simple_explain": parsed.get("simple_explain", "")
                }
                
        except json.JSONDecodeError:
            print(f"  [번역] JSON 파싱 실패 (시도 {attempt + 1}/{max_retries})")
        except httpx.ConnectError:
            print(f"  [번역] Ollama 연결 실패 - 로컬 Ollama가 실행 중인지 확인")
            break
        except Exception as e:
            print(f"  [번역] 오류: {e}")
    
    # 실패시 원본 반환
    return {
        "title_ko": title,
        "summary_ko": summary[:200],
        "simple_explain": ""
    }


def check_ollama_available() -> bool:
    """Ollama 서버 상태 확인"""
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get("http://localhost:11434/api/tags")
            return resp.status_code == 200
    except:
        return False


if __name__ == "__main__":
    if not check_ollama_available():
        print("❌ Ollama가 실행 중이 아닙니다")
        exit(1)
    
    print("✅ Ollama 연결 성공\n")
    
    # 테스트
    test_title = "F-GRPO: Don't Let Your Policy Learn the Obvious and Focus on the Difficult"
    test_summary = "Reinforcement Learning from Human Feedback (RLHF) has shown great potential for aligning language models with human values. Recently, Group Relative Policy Optimization (GRPO) has emerged as an efficient alternative to PPO"
    
    print("🔄 번역 중...\n")
    result = translate_and_simplify(test_title, test_summary)
    
    print("=== 번역 결과 ===")
    print(f"한글 제목: {result['title_ko']}")
    print(f"한글 요약: {result['summary_ko']}")
    print(f"쉬운 설명: {result['simple_explain']}")
