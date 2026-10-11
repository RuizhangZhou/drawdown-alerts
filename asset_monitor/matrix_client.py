import hashlib, time, uuid, requests
from pathlib import Path
from typing import Optional


def matrix_send_text(homeserver: str, room_id: str, access_token: str, text: str, txn_id=None):
    txn_id = txn_id or f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    url = f"{homeserver.rstrip('/')}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txn_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"msgtype": "m.text", "body": text}
    r = requests.put(url, headers=headers, json=payload, timeout=15)
    if not r.ok:
        raise RuntimeError(f'Matrix text send failed: HTTP {r.status_code}')
    return r.json()


def matrix_upload_file(homeserver: str, access_token: str, file_path: Path):
    """Matrix v3 media upload requires content bytes and query param filename.
    We send raw bytes with appropriate Content-Type and filename param.
    """
    try:
        upload_url = f"{homeserver.rstrip('/')}/_matrix/media/v3/upload?filename={file_path.name}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/png",
        }
        data = file_path.read_bytes()
        r = requests.post(upload_url, headers=headers, data=data, timeout=30)
        r.raise_for_status()
        return r.json().get('content_uri')
    except Exception as e:
        print(f"File upload failed for {file_path.name}: {e}")
        return None


def matrix_send_image(homeserver: str, room_id: str, access_token: str, file_path: Path, caption: str = '', txn_id=None):
    try:
        content_uri = matrix_upload_file(homeserver, access_token, file_path)
        if not content_uri:
            raise RuntimeError('Matrix chart upload failed')
        txn_id = txn_id or f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        url = f"{homeserver.rstrip('/')}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txn_id}"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "msgtype": "m.image",
            "body": file_path.stem + '.png',
            "url": content_uri,
            "info": {"mimetype": 'image/png', "size": file_path.stat().st_size},
        }
        r = requests.put(url, headers=headers, json=payload, timeout=15)
        if not r.ok:
            raise RuntimeError(f'Matrix image send failed: HTTP {r.status_code}')
        if caption:
            # A lost caption response must not duplicate its text on chart retry.
            caption_txn = hashlib.sha256(('caption:' + txn_id).encode()).hexdigest()
            matrix_send_text(homeserver, room_id, access_token, caption, txn_id=caption_txn)
        return r.json()
    except Exception as e:
        raise RuntimeError(f'Image send failed for {file_path.name}') from e
