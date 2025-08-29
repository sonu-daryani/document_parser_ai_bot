from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    UPLOAD_FOLDER = 'uploads'
    VECTOR_DB_FOLDER = 'vector_db'
    HISTORY_FOLDER = 'histories'
    USERS_FILE = 'users.json'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
