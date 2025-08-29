from flask import Blueprint, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import os
import json
from ..config import Config


auth_bp = Blueprint('auth', __name__)


def _read_users():
    path = Config.USERS_FILE
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _write_users(users):
    path = Config.USERS_FILE
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


@auth_bp.get('/ensure')
def ensure_auth():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    resp = make_response(jsonify({'user_id': user_id}), 200)
    resp.set_cookie('user_id', user_id, httponly=True, samesite='Lax', secure=False, max_age=60*60*24*365, path='/')
    return resp


@auth_bp.post('/signup')
def signup():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    users = _read_users()
    if username in users:
        return jsonify({'error': 'Username already exists'}), 409

    user_id = str(uuid.uuid4())
    users[username] = {
        'user_id': user_id,
        'username': username,
        'password_hash': generate_password_hash(password),
        'created_at': datetime.now().isoformat(),
    }
    _write_users(users)

    resp = make_response(jsonify({'user_id': user_id, 'username': username}), 201)
    resp.set_cookie('user_id', user_id, httponly=True, samesite='Lax', secure=False, max_age=60*60*24*365, path='/')
    return resp


@auth_bp.post('/login')
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip().lower()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    users = _read_users()
    user = users.get(username)
    if not user or not check_password_hash(user.get('password_hash', ''), password):
        return jsonify({'error': 'Invalid credentials'}), 401

    user_id = user['user_id']
    resp = make_response(jsonify({'user_id': user_id, 'username': username}), 200)
    resp.set_cookie('user_id', user_id, httponly=True, samesite='Lax', secure=False, max_age=60*60*24*365, path='/')
    return resp


@auth_bp.post('/logout')
def logout():
    resp = make_response(jsonify({'message': 'Logged out'}), 200)
    resp.set_cookie('user_id', '', expires=0, path='/')
    return resp


@auth_bp.get('/me')
def me():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False}), 200
    users = _read_users()
    username = None
    for uname, data in users.items():
        if data.get('user_id') == user_id:
            username = uname
            break
    if username is None:
        return jsonify({'authenticated': False}), 200
    return jsonify({'authenticated': True, 'user_id': user_id, 'username': username}), 200


