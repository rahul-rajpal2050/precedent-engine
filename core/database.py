import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", ".vectorstore.pkl")
_MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def _load_store() -> dict:
    if os.path.exists(_STORE_PATH):
        with open(_STORE_PATH, "rb") as f:
            return pickle.load(f)
    return {"ids": [], "documents": [], "metadatas": [], "embeddings": []}


def _save_store(store: dict) -> None:
    with open(_STORE_PATH, "wb") as f:
        pickle.dump(store, f)


def upsert_precedents(contract_id: str, chunks: list[str]) -> int:
    store = _load_store()
    model = _get_model()

    for i, chunk in enumerate(chunks):
        chunk_id = f"{contract_id}__chunk_{i}"
        embedding = model.encode(chunk).tolist()

        if chunk_id in store["ids"]:
            idx = store["ids"].index(chunk_id)
            store["documents"][idx] = chunk
            store["embeddings"][idx] = embedding
            store["metadatas"][idx] = {"contract_id": contract_id, "chunk_index": i}
        else:
            store["ids"].append(chunk_id)
            store["documents"].append(chunk)
            store["embeddings"].append(embedding)
            store["metadatas"].append({"contract_id": contract_id, "chunk_index": i})

    _save_store(store)
    return len(chunks)


def query_clause(clause_text: str, n_results: int = 3) -> list[dict]:
    store = _load_store()
    if not store["embeddings"]:
        return []

    model = _get_model()
    query_vec = model.encode(clause_text)

    matrix = np.array(store["embeddings"])
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    matrix_norms = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    similarities = matrix_norms @ query_norm

    top_indices = np.argsort(similarities)[::-1][:n_results]

    return [
        {
            "text": store["documents"][i],
            "contract_id": store["metadatas"][i]["contract_id"],
            "chunk_index": store["metadatas"][i]["chunk_index"],
            "similarity": round(float(similarities[i]), 4),
        }
        for i in top_indices
    ]
