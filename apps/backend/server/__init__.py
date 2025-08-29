import os
from flask import Flask
from flask_cors import CORS
import openai

from .config import Config
from .blueprints.auth import auth_bp
from .blueprints.documents import documents_bp
from .blueprints.chat import chat_bp
from .blueprints.health import health_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    openai.api_key = app.config['OPENAI_API_KEY']

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['VECTOR_DB_FOLDER'], exist_ok=True)
    os.makedirs(app.config['HISTORY_FOLDER'], exist_ok=True)

    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": ["http://localhost:4200"]}},
    )

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(documents_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')

    return app


