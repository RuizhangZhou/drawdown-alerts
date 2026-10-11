"""One-time, explicit local -> private Matrix state migration. No messages."""
import os

from .config import ENV_FILE, STATE_FILE
from .env_loader import load_env
from .state import MatrixState, load_state


def main():
    load_env(ENV_FILE)
    if not STATE_FILE.exists():
        raise RuntimeError('Existing local state required')
    local = load_state(STATE_FILE)
    remote = MatrixState(os.environ['MATRIX_HOMESERVER'], os.environ['MATRIX_ROOM_ID'],
                         os.environ['MATRIX_ACCESS_TOKEN'])
    previous = remote.load(allow_missing=True)
    if previous is not None:
        if any(previous.get(key) != value for key, value in local.items()):
            raise RuntimeError('Remote state differs; refusing to overwrite')
        print('Remote state already contains the local migration; unchanged.')
        return
    remote.save(local)
    if remote.load() != local:
        raise RuntimeError('State read-back did not match')
    print(f'Migrated and verified {len(local)} deduplication entries. No messages sent.')


if __name__ == '__main__':
    main()
