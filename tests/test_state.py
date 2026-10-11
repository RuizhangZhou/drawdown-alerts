import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from asset_monitor.state import MatrixState, load_state, save_state


def response(status=200, payload=None):
    return Mock(status_code=status, ok=status < 400, json=Mock(return_value=payload))


class StateTests(unittest.TestCase):
    def test_file_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.json'
            save_state(path, {'BTC': 'date'})
            self.assertEqual(load_state(path), {'BTC': 'date'})

    def test_corrupt_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.json'
            path.write_text('invalid')
            with self.assertRaises(RuntimeError):
                load_state(path)

    @patch('asset_monitor.state.requests.get')
    def test_missing_remote_requires_explicit_migration(self, get):
        get.side_effect = [response(payload={'user_id': '@bot:example.org'}), response(404), response(404)]
        store = MatrixState('https://example.org', '!room:example.org', 'test-token')
        with self.assertRaises(RuntimeError):
            store.load()
        self.assertIsNone(store.load(allow_missing=True))

    @patch('asset_monitor.state.requests.get')
    def test_private_room_scoped_and_validated(self, get):
        get.side_effect = [response(payload={'user_id': '@bot:example.org'}),
                           response(payload={'version': 1, 'state': {'key': 'date'}})]
        store = MatrixState('https://example.org', '!room:example.org', 'test-token')
        self.assertEqual(store.load(), {'key': 'date'})
        self.assertIn('/user/%40bot%3Aexample.org/rooms/%21room%3Aexample.org/account_data/', store.url)

    @patch('asset_monitor.state.requests.put', return_value=response(500))
    @patch('asset_monitor.state.requests.get', return_value=response(payload={'user_id': '@bot:example.org'}))
    def test_remote_write_failure_propagates(self, get, put):
        store = MatrixState('https://example.org', '!room:example.org', 'test-token')
        with self.assertRaises(RuntimeError):
            store.save({})


if __name__ == '__main__':
    unittest.main()
