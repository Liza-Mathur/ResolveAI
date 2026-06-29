from tools.policy_search import search_policy

results = search_policy("is footwear covered under warranty", source_filter="warranty_policy.md", k=3)

for i, r in enumerate(results):
    print(f"--- Result {i+1} (source: {r['source']}) ---")
    print(r["content"])
    print()