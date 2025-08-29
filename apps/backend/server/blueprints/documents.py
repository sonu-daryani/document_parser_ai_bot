import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..config import Config
from ..services.vectors import get_user_vector_paths, create_vector_index
from ..utils.files import allowed_file, extract_text_from_file, chunk_text


documents_bp = Blueprint('documents', __name__)


def _get_user_id() -> str:
    return request.cookies.get('user_id') or request.headers.get('X-User-Id')


@documents_bp.post('/upload')
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    user_id = _get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized: missing user cookie'}), 401

    files = request.files.getlist('files')
    uploaded_files = []
    all_chunks = []
    all_metadata = []
    documents = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_id = str(uuid.uuid4())
            file_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}_{filename}")
            file.save(file_path)

            text_content = extract_text_from_file(file_path, filename)
            chunks = chunk_text(text_content, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'text': chunk,
                    'metadata': {
                        'file_id': file_id,
                        'filename': filename,
                        'chunk_index': i,
                        'upload_time': datetime.now().isoformat()
                    }
                })
            doc_info = {
                'file_id': file_id,
                'filename': filename,
                'file_path': file_path,
                'upload_time': datetime.now().isoformat(),
                'chunk_count': len(chunks)
            }
            documents.append(doc_info)
            uploaded_files.append(doc_info)
        else:
            return jsonify({'error': f'File type not allowed: {file.filename}'}), 400

    if all_chunks:
        index, embeddings, metadata = create_vector_index(all_chunks, all_metadata)
        index_path, meta_path = get_user_vector_paths(user_id)
        import faiss
        faiss.write_index(index, index_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({'metadata': metadata, 'documents': documents}, f, ensure_ascii=False, indent=2)

    return jsonify({'message': f'Successfully uploaded {len(uploaded_files)} files', 'user_id': user_id, 'files': uploaded_files, 'total_chunks': len(all_chunks)}), 200


@documents_bp.get('/documents')
def get_user_documents():
    user_id = _get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized: missing user cookie'}), 401
    _, meta_path = get_user_vector_paths(user_id)
    if not os.path.exists(meta_path):
        return jsonify({'documents': []}), 200
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta_json = json.load(f)
        documents = meta_json.get('documents', [])
    return jsonify({'documents': documents}), 200


@documents_bp.delete('/documents/<file_id>')
def delete_document(file_id):
    user_id = _get_user_id()
    if not user_id:
        return jsonify({'error': 'Unauthorized: missing user cookie'}), 401
    index_path, meta_path = get_user_vector_paths(user_id)
    if not os.path.exists(meta_path):
        return jsonify({'error': 'User not found'}), 404
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta_json = json.load(f)
        documents = meta_json.get('documents', [])
        metadata = meta_json.get('metadata', [])

    document_to_remove = None
    for doc in documents:
        if doc['file_id'] == file_id:
            document_to_remove = doc
            break
    if not document_to_remove:
        return jsonify({'error': 'Document not found'}), 404

    if os.path.exists(document_to_remove['file_path']):
        os.remove(document_to_remove['file_path'])

    documents = [doc for doc in documents if doc['file_id'] != file_id]
    metadata = [meta for meta in metadata if meta['metadata']['file_id'] != file_id]

    if metadata:
        texts = [meta['text'] for meta in metadata]
        index, embeddings, new_metadata = create_vector_index(texts, metadata)
        import faiss
        faiss.write_index(index, index_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({'metadata': new_metadata, 'documents': documents}, f, ensure_ascii=False, indent=2)
    else:
        if os.path.exists(index_path):
            os.remove(index_path)
        os.remove(meta_path)

    return jsonify({'message': 'Document deleted successfully'}), 200


