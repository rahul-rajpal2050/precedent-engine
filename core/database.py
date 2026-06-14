import os
import chromadb
from chromadb.utils import embedding_functions

_CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", ".chroma")
_COLLECTION_NAME = "contracts"

_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def _get_collection():
    client = chromadb.PersistentClient(path=_CHROMA_PATH)
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        embedding_function=_ef,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_precedents(contract_id: str, chunks: list[str]) -> int:
    collection = _get_collection()
    ids = [f"{contract_id}__chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"contract_id": contract_id, "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)
    return len(chunks)


def query_clause(clause_text: str, n_results: int = 2) -> list[dict]:
    collection = _get_collection()
    total = collection.count()
    n = min(n_results, total) if total > 0 else 0
    if n == 0:
        return []

    results = collection.query(
        query_texts=[clause_text],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, dists):
        similarity = round(1 - dist, 4)  # cosine distance → similarity
        output.append({
            "text": doc,
            "contract_id": meta.get("contract_id", "unknown"),
            "chunk_index": meta.get("chunk_index", 0),
            "similarity": similarity,
        })

    return output
