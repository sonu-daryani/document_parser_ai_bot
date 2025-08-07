# apps/backend


# Backend Setup Instructions

## 1. Python Version
Ensure you are using Python 3.9 or newer (but less than 4.0).


## 2. Install Dependencies (Recommended: uv)

First, install [uv](https://github.com/astral-sh/uv) (a fast Python package manager):

```sh
curl -Ls https://astral.sh/uv/install.sh | sh
```

Then install dependencies with:

```sh
uv pip install -r requirements.txt
```

If you use a virtual environment, activate it first, then run the above command.

## 3. Running the Backend

To run the backend directly:

```sh
python3 app.py
```

Or, if using Nx:

```sh
npm run dev
```

## 4. Troubleshooting

- If you see `ModuleNotFoundError`, ensure you installed dependencies with the correct Python version and environment.
- If you see `faiss` or `flask` errors, try running the install command again.
- If you use macOS and see warnings about PATH, add this to your shell profile:
  ```sh
  export PATH="$HOME/Library/Python/3.9/bin:$PATH"
  ```

## 5. Environment Variables

Create a `.env` file in this directory and add your OpenAI API key:

```
OPENAI_API_KEY=your-key-here
```
