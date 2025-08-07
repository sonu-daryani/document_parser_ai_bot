import os
from dotenv import load_dotenv
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

import faiss
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import openai
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Load environment variables from .env if present
load_dotenv()

# Configuration
class Config:
    UPLOAD_FOLDER = 'uploads'
    VECTOR_DB_FOLDER = 'vector_db'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

app.config.from_object(Config)

# Initialize OpenAI
openai.api_key = app.config['OPENAI_API_KEY']

# Initialize sentence transformer for embeddings
embedding_model = SentenceTransformer(app.config['EMBEDDING_MODEL'])

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VECTOR_DB_FOLDER'], exist_ok=True)


def get_user_vector_paths(user_id):
    """Return file paths for a user's FAISS index and metadata."""
    vector_db_folder = app.config['VECTOR_DB_FOLDER']
    index_path = os.path.join(vector_db_folder, f"{user_id}_index.faiss")
    meta_path = os.path.join(vector_db_folder, f"{user_id}_meta.json")
    return index_path, meta_path

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(file_path, filename):
    """Extract text content from different file types"""
    file_extension = filename.rsplit('.', 1)[1].lower()
    
    try:
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        elif file_extension == 'pdf':
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        
        elif file_extension in ['docx', 'doc']:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {str(e)}")
        raise e

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundaries
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:
                chunk = text[start:break_point + 1]
                end = break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
        
        if start >= len(text) - overlap:
            break
    
    return chunks

def create_vector_index(texts, metadata_list):
    """Create FAISS vector index from text chunks"""
    # Generate embeddings
    embeddings = embedding_model.encode(texts)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    return index, embeddings, metadata_list

def search_similar_chunks(query, index, embeddings, metadata_list, k=5):
    """Search for similar chunks using FAISS"""
    # Generate query embedding
    query_embedding = embedding_model.encode([query])
    faiss.normalize_L2(query_embedding)
    
    # Search for similar chunks
    scores, indices = index.search(query_embedding.astype('float32'), k)
    
    results = []
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < len(metadata_list):
            results.append({
                'text': metadata_list[idx]['text'],
                'metadata': metadata_list[idx]['metadata'],
                'score': float(score)
            })
    
    return results


@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle multiple file uploads and persist vector index/metadata to disk"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        files = request.files.getlist('files')
        user_id = request.form.get('user_id', str(uuid.uuid4()))

        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': 'No files selected'}), 400

        uploaded_files = []
        all_chunks = []
        all_metadata = []
        documents = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_id = str(uuid.uuid4())
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
                file.save(file_path)

                try:
                    text_content = extract_text_from_file(file_path, filename)
                    chunks = chunk_text(text_content, app.config['CHUNK_SIZE'], app.config['CHUNK_OVERLAP'])
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
                    logger.info(f"Processed file: {filename} ({len(chunks)} chunks)")
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {str(e)}")
                    return jsonify({'error': f'Error processing file {filename}: {str(e)}'}), 500
            else:
                return jsonify({'error': f'File type not allowed: {file.filename}'}), 400

        # Create and persist vector index and metadata
        if all_chunks:
            index, embeddings, metadata = create_vector_index(all_chunks, all_metadata)
            index_path, meta_path = get_user_vector_paths(user_id)
            faiss.write_index(index, index_path)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({'metadata': metadata, 'documents': documents}, f, ensure_ascii=False, indent=2)

        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'user_id': user_id,
            'files': uploaded_files,
            'total_chunks': len(all_chunks)
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat queries using RAG, loading vector index/metadata from disk"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        user_id = data.get('user_id', '')

        if not query:
            return jsonify({'error': 'No query provided'}), 400

        index_path, meta_path = get_user_vector_paths(user_id)
        if not (os.path.exists(index_path) and os.path.exists(meta_path)):
            return jsonify({'error': 'Invalid user_id or no documents uploaded'}), 400

        # Load vector index and metadata
        index = faiss.read_index(index_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta_json = json.load(f)
            metadata = meta_json.get('metadata', [])

        if not metadata:
            return jsonify({'error': 'No documents processed for this user'}), 400

        # Generate embeddings for all chunks (needed for search)
        # For efficiency, you could persist embeddings as well, but here we recompute
        texts = [meta['text'] for meta in metadata]
        embeddings = embedding_model.encode(texts)
        faiss.normalize_L2(embeddings)

        # Search for relevant chunks
        relevant_chunks = search_similar_chunks(
            query,
            index,
            embeddings,
            metadata,
            k=5
        )

        if not relevant_chunks:
            return jsonify({'error': 'No relevant content found'}), 404

        # Prepare context from relevant chunks
        context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])

        # Create prompt for OpenAI
        system_prompt = """You are a helpful assistant that answers questions based only on the provided context. 
        If the answer cannot be found in the context, say \"I cannot find information about that in the uploaded documents.\"
        Be concise and accurate in your responses."""

        user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )

        answer = response.choices[0].message.content

        # Prepare source information
        sources = []
        for chunk in relevant_chunks:
            source_info = {
                'filename': chunk['metadata']['metadata']['filename'],
                'chunk_index': chunk['metadata']['metadata']['chunk_index'],
                'score': chunk['score']
            }
            if source_info not in sources:
                sources.append(source_info)

        return jsonify({
            'answer': answer,
            'sources': sources,
            'query': query
        }), 200

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/<user_id>', methods=['GET'])
def get_user_documents(user_id):
    """Get list of uploaded documents for a user from vector_db metadata"""
    try:
        _, meta_path = get_user_vector_paths(user_id)
        if not os.path.exists(meta_path):
            return jsonify({'documents': []}), 200
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta_json = json.load(f)
            documents = meta_json.get('documents', [])
        return jsonify({'documents': documents}), 200
    except Exception as e:
        logger.error(f"Get documents error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/documents/<user_id>/<file_id>', methods=['DELETE'])
def delete_document(user_id, file_id):
    """Delete a specific document and update vector index/metadata on disk"""
    try:
        index_path, meta_path = get_user_vector_paths(user_id)
        if not os.path.exists(meta_path):
            return jsonify({'error': 'User not found'}), 404
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta_json = json.load(f)
            documents = meta_json.get('documents', [])
            metadata = meta_json.get('metadata', [])

        # Find and remove document
        document_to_remove = None
        for doc in documents:
            if doc['file_id'] == file_id:
                document_to_remove = doc
                break
        if not document_to_remove:
            return jsonify({'error': 'Document not found'}), 404

        # Remove file from filesystem
        if os.path.exists(document_to_remove['file_path']):
            os.remove(document_to_remove['file_path'])

        # Remove from documents list
        documents = [doc for doc in documents if doc['file_id'] != file_id]
        # Remove chunks from metadata
        metadata = [meta for meta in metadata if meta['metadata']['file_id'] != file_id]

        # Rebuild or remove vector index and update metadata file
        if metadata:
            texts = [meta['text'] for meta in metadata]
            index, embeddings, new_metadata = create_vector_index(texts, metadata)
            faiss.write_index(index, index_path)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump({'metadata': new_metadata, 'documents': documents}, f, ensure_ascii=False, indent=2)
        else:
            # Remove index and metadata files if no docs left
            if os.path.exists(index_path):
                os.remove(index_path)
            os.remove(meta_path)

        return jsonify({'message': 'Document deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)