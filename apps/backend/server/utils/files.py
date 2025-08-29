import os
from typing import List
import PyPDF2
import docx
from ..config import Config


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def extract_text_from_file(file_path: str, filename: str) -> str:
    file_extension = filename.rsplit('.', 1)[1].lower()
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
        d = docx.Document(file_path)
        text = ""
        for paragraph in d.paragraphs:
            text += paragraph.text + "\n"
        return text
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
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


