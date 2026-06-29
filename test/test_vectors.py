from tools.vectorstore import load_vector_store

vectordb = load_vector_store()

query = "Can I return shoes if they've been worn outside?"
results = vectordb.similarity_search(query, k=3)

for i, doc in enumerate(results):
    print(f"--- Result {i+1} (source: {doc.metadata.get('source_file')}) ---")
    print(doc.page_content)
    print()