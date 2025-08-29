from flask import Blueprint, jsonify
from datetime import datetime


health_bp = Blueprint('health', __name__)


@health_bp.get('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat(), 'version': '1.0.0'}), 200


