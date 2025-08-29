import os
import json
from typing import Dict, Any
from ..config import Config


def read_users() -> Dict[str, Any]:
    path = Config.USERS_FILE
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def write_users(users: Dict[str, Any]) -> None:
    path = Config.USERS_FILE
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


