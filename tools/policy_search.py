from tools.vectorstore import load_vector_store

def search_policy(query: str, source_filter: str = None, k: int = 3) -> list:
    """
    Search policy documents (returns, warranty, shipping) for relevant chunks.
    Optional source_filter: 'returns_policy.md', 'warranty_policy.md', 'shipping_policy.md'
    """
    vectordb = load_vector_store()

    if source_filter:
        results = vectordb.similarity_search(
            query, k=k, filter={"source_file": source_filter}
        )
    else:
        results = vectordb.similarity_search(query, k=k)

    return [
        {"content": doc.page_content, "source": doc.metadata.get("source_file")}
        for doc in results
    ]