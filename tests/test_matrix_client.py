from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from asset_monitor.matrix_client import matrix_send_image


class ChartRetryTests(unittest.TestCase):
    def test_ambiguous_caption_retry_reuses_both_transaction_ids(self):
        response = Mock(ok=True)
        response.json.return_value = {'event_id': '$image'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'chart.png'
            path.write_bytes(b'png')
            with patch('asset_monitor.matrix_client.matrix_upload_file', return_value='mxc://example/image'), \
                 patch('asset_monitor.matrix_client.requests.put', return_value=response) as image, \
                 patch('asset_monitor.matrix_client.matrix_send_text', side_effect=[TimeoutError(), {}]) as caption:
                with self.assertRaises(RuntimeError):
                    matrix_send_image('https://example.org', '!room', 'test', path, 'Caption', 'chart-day')
                matrix_send_image('https://example.org', '!room', 'test', path, 'Caption', 'chart-day')
                self.assertEqual(image.call_args_list[0].args[0], image.call_args_list[1].args[0])
                ids = [call.kwargs['txn_id'] for call in caption.call_args_list]
                self.assertEqual(ids[0], ids[1])
                self.assertNotEqual(ids[0], 'chart-day')

    def test_image_failure_does_not_send_caption(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'chart.png'
            path.write_bytes(b'png')
            with patch('asset_monitor.matrix_client.matrix_upload_file', return_value='mxc://example/image'), \
                 patch('asset_monitor.matrix_client.requests.put', return_value=Mock(ok=False, status_code=500)), \
                 patch('asset_monitor.matrix_client.matrix_send_text') as caption:
                with self.assertRaises(RuntimeError):
                    matrix_send_image('https://example.org', '!room', 'test', path, 'Caption', 'chart-day')
                caption.assert_not_called()
