import json

with open('temp_papers.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

for i, p in enumerate(papers[:10], 1):
    t = p.get('title', '')
    c = p.get('category', '')
    v = p.get('upvotes', 0)
    s = p.get('summary', '')[:400]
    print(f"--- PAPER {i} ---")
    print(f"T: {t}")
    print(f"C: {c}")
    print(f"V: {v}")
    print(f"S: {s}")
    print()
