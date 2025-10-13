import time, uuid, requests
from pathlib import Path
from typing import Optional


def matrix_send_text(homeserver: str, room_id: str, access_token: str, text: str):
    txn_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    url = f"{homeserver.rstrip('/')}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txn_id}"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"msgtype": "m.text", "body": text}
    r = requests.put(url, headers=headers, json=payload, timeout=15)
    r.raise_for_status()
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


def matrix_send_image(homeserver: str, room_id: str, access_token: str, file_path: Path, caption: str = ''):
    try:
        content_uri = matrix_upload_file(homeserver, access_token, file_path)
        if not content_uri:
            return None
        txn_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        url = f"{homeserver.rstrip('/')}/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txn_id}"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        payload = {
            "msgtype": "m.image",
            "body": file_path.stem + '.png',
            "url": content_uri,
            "info": {"mimetype": 'image/png', "size": file_path.stat().st_size},
        }
        r = requests.put(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        if caption:
            matrix_send_text(homeserver, room_id, access_token, caption)
        return r.json()
    except Exception as e:
        print(f"Image send failed for {file_path.name}: {e}")
        return None
