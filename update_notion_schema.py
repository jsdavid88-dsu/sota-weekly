"""
Notion Database 스키마 업데이트
"역할/기능" 중심 분류로 전환
"""
import httpx
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
load_dotenv(env_path)

token = os.getenv('NOTION_API_TOKEN')
db_id = os.getenv('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# 새 필드 추가
new_properties = {
    "기능역할": {
        "select": {
            "options": [
                {"name": "캐릭터 일관성 유지", "color": "blue"},
                {"name": "3D→2D 스타일 변환", "color": "green"},
                {"name": "음성→립싱크 자동화", "color": "yellow"},
                {"name": "서사 구조 시각화", "color": "purple"},
                {"name": "배경 3D 재구성", "color": "red"},
                {"name": "장면 일관성 제어", "color": "pink"},
                {"name": "긴 영상 생성", "color": "orange"},
                {"name": "워크플로우 자동화", "color": "gray"},
                {"name": "DCC 툴 연동", "color": "brown"}
            ]
        }
    },
    "적용영역": {
        "multi_select": {
            "options": [
                {"name": "DSUComfyCG", "color": "blue"},
                {"name": "부산마법소녀", "color": "pink"},
                {"name": "교육", "color": "green"},
                {"name": "연구발표", "color": "purple"},
                {"name": "클라이언트", "color": "orange"}
            ]
        }
    },
    "기술스택": {
        "multi_select": {
            "options": [
                {"name": "ComfyUI", "color": "blue"},
                {"name": "UE5", "color": "red"},
                {"name": "Maya", "color": "orange"},
                {"name": "Nuke", "color": "yellow"},
                {"name": "Gaussian Splatting", "color": "green"},
                {"name": "PyTorch", "color": "purple"},
                {"name": "AnimateDiff", "color": "pink"}
            ]
        }
    },
    "실행난이도": {
        "select": {
            "options": [
                {"name": "즉시 적용", "color": "green"},
                {"name": "커스터마이징 필요", "color": "yellow"},
                {"name": "연구 단계", "color": "orange"},
                {"name": "개념만 참고", "color": "gray"}
            ]
        }
    }
}

response = httpx.patch(
    f"https://api.notion.com/v1/databases/{db_id}",
    headers=headers,
    json={"properties": new_properties},
    timeout=30.0
)

if response.status_code == 200:
    print("OK - Database schema updated!")
    print("\nAdded properties:")
    for key in new_properties.keys():
        print(f"  - {key}")
else:
    print(f"ERROR: {response.status_code}")
    print(response.text)
