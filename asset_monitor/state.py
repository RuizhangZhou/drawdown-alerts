import json
from pathlib import Path
from typing import Dict, Any


def load_state(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text('utf-8'))
        except Exception:
            return {}
    return {}


def save_state(path: Path, state: Dict[str, Any]):
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
