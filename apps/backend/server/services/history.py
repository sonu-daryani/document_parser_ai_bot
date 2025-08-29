import os
import json
from typing import List, Dict, Any
from ..config import Config


def get_history_path(user_id: str) -> str:
    return os.path.join(Config.HISTORY_FOLDER, f"{user_id}.json")


def read_user_history(user_id: str) -> List[Dict[str, Any]]:
    path = get_history_path(user_id)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def append_user_history(user_id: str, entry: Dict[str, Any]) -> None:
    history = read_user_history(user_id)
    history.append(entry)
    if len(history) > 500:
        history = history[-500:]
    with open(get_history_path(user_id), 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


