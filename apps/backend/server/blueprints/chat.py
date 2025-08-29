import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify
import openai
import faiss
from ..services.vectors import get_user_vector_paths, search_similar_chunks, embedding_model
from ..services.history import read_user_history, append_user_history


chat_bp = Blueprint('chat', __name__)


def _get_user_id() -> str:
    return request.cookies.get('user_id') or request.headers.get('X-User-Id')


@chat_bp.post('/chat')
def chat():
    data = request.get_json() or {}
    query = data.get('query', '')
    user_id = _get_user_id()
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    if not user_id:
        return jsonify({'error': 'Unauthorized: missing user cookie'}), 401

    index_path, meta_path = get_user_vector_paths(user_id)
    if not (os.path.exists(index_path) and os.path.exists(meta_path)):
        return jsonify({'error': 'Invalid user_id or no documents uploaded'}), 400

    index = faiss.read_index(index_path)
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta_json = json.load(f)
        metadata = meta_json.get('metadata', [])
    if not metadata:
        return jsonify({'error': 'No documents processed for this user'}), 400

    texts = [meta['text'] for meta in metadata]
    embeddings = embedding_model.encode(texts)
    faiss.normalize_L2(embeddings)

    relevant_chunks = search_similar_chunks(query, index, embeddings, metadata, k=5)
    if not relevant_chunks:
        return jsonify({'error': 'No relevant content found'}), 404

    context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
    system_prompt = (
        "You are a helpful assistant that answers questions based only on the provided context. "
        "If the answer cannot be found in the context, say \"I cannot find information about that in the uploaded documents.\" "
        "Be concise and accurate in your responses."
    )
    user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,
        temperature=0.1,
    )
    answer = response.choices[0].message.content

    sources = []
    for chunk in relevant_chunks:
        meta = chunk.get('metadata', {})
        source_info = {
            'filename': meta.get('filename', ''),
            'chunk_index': meta.get('chunk_index', None),
            'score': chunk.get('score', 0),
        }
        if source_info not in sources:
            sources.append(source_info)

    try:
        append_user_history(user_id, {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'answer': answer,
            'sources': sources,
        })
    except Exception:
        pass

    return jsonify({'answer': answer, 'sources': sources, 'query': query}), 200


@chat_bp.get('/history')
def get_history():
    user_id = _get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized: missing user cookie'}), 401
    history = read_user_history(user_id)
    return jsonify({'history': history}), 200


