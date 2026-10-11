import json
import os
from pathlib import Path
from typing import Dict, Any
from urllib.parse import quote

import requests


def load_state(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text('utf-8'))
        except Exception as exc:
            raise RuntimeError('Invalid state file; refusing to reset deduplication') from exc
    return {}


def save_state(path: Path, state: Dict[str, Any]):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


class MatrixState:
    """Private account data, not public room events or GitHub artifacts.

    Requires one writer (the workflow's concurrency group). Never initialize
    missing remote state implicitly: migrate the server state explicitly first.
    """
    event_type = 'com.rickandzoey.drawdown-alerts.state.v1'

    def __init__(self, homeserver, room_id, token):
        self.headers = {'Authorization': f'Bearer {token}'}
        base = homeserver.rstrip('/') + '/_matrix/client/v3'
        response = requests.get(base + '/account/whoami', headers=self.headers, timeout=20)
        self.check(response)
        user_id = response.json()['user_id']
        self.url = (base + '/user/' + quote(user_id, safe='') + '/rooms/'
                    + quote(room_id, safe='') + '/account_data/' + self.event_type)

    @staticmethod
    def check(response):
        if not response.ok:
            raise RuntimeError(f'Matrix state API failed: HTTP {response.status_code}')

    def load(self, allow_missing=False):
        response = requests.get(self.url, headers=self.headers, timeout=20)
        if response.status_code == 404 and allow_missing:
            return None
        self.check(response)
        payload = response.json()
        if payload.get('version') != 1 or not isinstance(payload.get('state'), dict):
            raise RuntimeError('Invalid remote state; refusing to reset deduplication')
        return payload['state']

    def save(self, state):
        response = requests.put(self.url, headers=self.headers,
                                json={'version': 1, 'state': state}, timeout=20)
        self.check(response)


class FileState:
    def __init__(self, path):
        self.path = path

    def load(self):
        return load_state(self.path)

    def save(self, state):
        save_state(self.path, state)


def state_store(path, hs, rid, token):
    backend = os.environ.get('ASSET_STATE_BACKEND', 'file')
    if backend == 'matrix':
        return MatrixState(hs, rid, token)
    if backend != 'file':
        raise ValueError('Unknown ASSET_STATE_BACKEND')
    return FileState(path)
