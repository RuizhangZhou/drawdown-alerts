import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from asset_monitor.main import run_assets


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.patches = [patch.dict(os.environ, {'MATRIX_HOMESERVER': 'https://example.org',
                         'MATRIX_ROOM_ID': '!test:example.org', 'MATRIX_ACCESS_TOKEN': 'test-token'}),
                        patch('asset_monitor.main.load_env'),
                        patch('asset_monitor.main.ASSETS', [{'name': 'BTC', 'source': 'binance',
                              'symbol': 'BTCUSDT', 'window': 2, 'drawdown_thresholds': [-0.1],
                              'drawdown_rules': {-0.1: 'test'}}])]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        self.store = Mock()
        self.store.load.return_value = {}
        for name in ['state_store', 'fetch_binance_klines', 'matrix_send_text', 'matrix_send_image', 'create_asset_chart']:
            item = patch('asset_monitor.main.' + name)
            setattr(self, name, item.start())
            self.addCleanup(item.stop)
        self.state_store.return_value = self.store
        self.fetch_binance_klines.return_value = pd.Series([100.0, 100.0, 80.0],
                                                index=pd.date_range('2026-10-09', periods=3))
        self.create_asset_chart.return_value = True

    def test_dry_run_never_sends_or_writes_state(self):
        run_assets(dry_run=True, daily_report=True, send_charts=True)
        self.matrix_send_text.assert_not_called()
        self.matrix_send_image.assert_not_called()
        self.store.save.assert_not_called()
        self.assertEqual(self.store.load.return_value, {})

    def test_failed_send_does_not_mark_delivered(self):
        self.matrix_send_text.side_effect = RuntimeError('send failed')
        with self.assertRaises(RuntimeError):
            run_assets()
        self.store.save.assert_not_called()
        self.assertEqual(self.store.load.return_value, {})

    def test_successful_alert_persisted_and_repeated_run_skips(self):
        self.store.save.side_effect = lambda state: setattr(self.store.load, 'return_value', copy.deepcopy(state))
        run_assets()
        self.assertEqual(self.matrix_send_text.call_count, 1)
        self.assertIn('txn_id', self.matrix_send_text.call_args.kwargs)
        run_assets()
        self.assertEqual(self.matrix_send_text.call_count, 1)

    def test_failed_data_never_sends_partial_report(self):
        self.fetch_binance_klines.side_effect = RuntimeError('temporary failure')
        with self.assertRaises(RuntimeError):
            run_assets(daily_report=True)
        self.matrix_send_text.assert_not_called()
        self.store.save.assert_not_called()

    def test_weekly_report_same_day_is_deduplicated(self):
        self.store.save.side_effect = lambda state: setattr(self.store.load, 'return_value', copy.deepcopy(state))
        run_assets(daily_report=True)
        count = self.matrix_send_text.call_count
        run_assets(daily_report=True)
        self.assertEqual(self.matrix_send_text.call_count, count)

    def render_chart(self, name, series, window, path):
        path.write_bytes(b'test image')
        return True

    def test_existing_chart_caption_and_checkpoint_are_deduplicated(self):
        self.store.save.side_effect = lambda state: setattr(self.store.load, 'return_value', copy.deepcopy(state))
        self.create_asset_chart.side_effect = self.render_chart
        with tempfile.TemporaryDirectory() as directory, patch('asset_monitor.main.__file__',
                str(Path(directory) / 'asset_monitor' / 'main.py')):
            run_assets(daily_report=True, send_charts=True)
            self.matrix_send_image.assert_called_once()
            sent = self.matrix_send_image.call_args
            self.assertEqual(sent.kwargs['caption'], 'BTC 2D price & drawdown/surge chart')
            self.assertTrue(sent.args[3].exists())
            self.assertTrue(any(key.startswith('chart|') for key in self.store.load.return_value))
            run_assets(daily_report=True, send_charts=True)
            self.matrix_send_image.assert_called_once()

    def test_failed_chart_keeps_checkpoint_unset_and_reuses_transaction(self):
        self.store.save.side_effect = lambda state: setattr(self.store.load, 'return_value', copy.deepcopy(state))
        self.create_asset_chart.side_effect = self.render_chart
        self.matrix_send_image.side_effect = [RuntimeError('ambiguous response'), {}]
        with tempfile.TemporaryDirectory() as directory, patch('asset_monitor.main.__file__',
                str(Path(directory) / 'asset_monitor' / 'main.py')):
            with self.assertRaises(RuntimeError):
                run_assets(daily_report=True, send_charts=True)
            self.assertFalse(any(key.startswith('chart|') for key in self.store.load.return_value))
            first = self.matrix_send_image.call_args.kwargs['txn_id']
            run_assets(daily_report=True, send_charts=True)
            self.assertEqual(self.matrix_send_image.call_args.kwargs['txn_id'], first)
            self.assertTrue(any(key.startswith('chart|') for key in self.store.load.return_value))


if __name__ == '__main__':
    unittest.main()
