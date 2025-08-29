import os
import json
import faiss
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from ..config import Config


embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)


def get_user_vector_paths(user_id: str) -> Tuple[str, str]:
    index_path = os.path.join(Config.VECTOR_DB_FOLDER, f"{user_id}_index.faiss")
    meta_path = os.path.join(Config.VECTOR_DB_FOLDER, f"{user_id}_meta.json")
    return index_path, meta_path


def create_vector_index(texts: List[str], metadata_list: List[Dict[str, Any]]):
    embeddings = embedding_model.encode(texts)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype('float32'))
    return index, embeddings, metadata_list


def search_similar_chunks(query: str, index, embeddings, metadata_list, k: int = 5):
    query_embedding = embedding_model.encode([query])
    faiss.normalize_L2(query_embedding)
    scores, indices = index.search(query_embedding.astype('float32'), k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(metadata_list):
            meta = metadata_list[idx]
            metadata = meta.get('metadata', {}) if isinstance(meta, dict) else {}
            results.append({'text': meta.get('text', ''), 'metadata': metadata, 'score': float(score)})
    return results


