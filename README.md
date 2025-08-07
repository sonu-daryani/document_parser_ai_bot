# DOCUMENT PARSER AI BOT

A full-stack AI-powered chatbot that allows users to upload PDF and document files, parses and indexes their content, and enables conversational Q&A over the uploaded documents using OpenAI and vector search.
---


<img width="600" alt="Screenshot" src="https://github.com/user-attachments/assets/14cfffa9-81a6-4996-a1c7-baab9b11dabf" />

---

## Features

- Upload PDF, DOCX, and TXT files via a modern web UI
- Automatic text extraction and chunking
- Embedding and vector search using FAISS and Sentence Transformers
- Conversational chat interface with persistent history (localStorage)
- Backend powered by Flask, OpenAI, and Python
- Nx monorepo for unified frontend and backend development

---

## Quick Start

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd chatbot-monorepo
```

### 2. Backend Setup

- Python 3.9+ required
- Install dependencies (recommended: [uv](https://github.com/astral-sh/uv)):

```sh
cd apps/backend
uv pip install -r requirements.txt
```

- Create a `.env` file in `apps/backend` and add your OpenAI API key:

```
OPENAI_API_KEY=your-key-here
```

- Start the backend:

```sh
python3 app.py
```

### 3. Frontend Setup

- Node.js 18+ recommended
- Install dependencies:

```sh
npm install
```

- Start the frontend (from the root):

```sh
npx nx serve frontend
```

The frontend will be available at [http://localhost:4200](http://localhost:4200).

---

## Usage

1. Upload your PDF or document files using the web UI.
2. Ask questions about the content in the chat interface.
3. The conversation is stored in your browser and will persist after reloads.

---

## Project Structure

- `apps/backend/` — Flask API, file uploads, vector DB, OpenAI integration
- `apps/frontend/` — React + Vite web app, chat UI, file upload UI
- `uploads/` — Uploaded files (gitignored)
- `vector_db/` — FAISS indices and metadata (gitignored)

---

## Development

- To run both frontend and backend together:

```sh
npm run dev
```

- To build for production, use Nx build commands.

---

## Troubleshooting

- If you see `ModuleNotFoundError`, ensure dependencies are installed for the correct Python version.
- For FAISS or Flask errors, try reinstalling dependencies.
- On macOS, if you see PATH warnings, add this to your shell profile:
  ```sh
  export PATH="$HOME/Library/Python/3.9/bin:$PATH"
  ```

---
