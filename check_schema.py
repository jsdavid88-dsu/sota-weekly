import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv('config/.env')
token = os.getenv('NOTION_API_TOKEN')
db_id = os.getenv('NOTION_DATABASE_ID')

resp = httpx.get(
    f'https://api.notion.com/v1/databases/{db_id}',
    headers={
        'Authorization': f'Bearer {token}',
        'Notion-Version': '2022-06-28'
    }
)
data = resp.json()
print('=== 현재 데이터베이스 속성 ===\n')
for name, prop in data.get('properties', {}).items():
    ptype = prop.get('type', '?')
    print(f'- {name}: {ptype}')
    if ptype == 'select' and prop.get('select', {}).get('options'):
        opts = [o['name'] for o in prop['select']['options']]
        print(f'    옵션: {opts}')
    if ptype == 'multi_select' and prop.get('multi_select', {}).get('options'):
        opts = [o['name'] for o in prop['multi_select']['options']]
        print(f'    옵션: {opts[:10]}...' if len(opts) > 10 else f'    옵션: {opts}')
