import json

with open('temp_papers.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

for i, p in enumerate(papers[:10]):
    print(f"--- {i+1}. {p.get('title','')}")
    print(f"    abstract: {p.get('abstract','')[:400]}")
    print(f"    category: {p.get('category','')}")
    votes = p.get('upvotes', p.get('votes', p.get('score', 0)))
    print(f"    votes: {votes}")
    print()
