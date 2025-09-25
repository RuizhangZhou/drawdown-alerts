import os, sys, argparse
from datetime import datetime
from pathlib import Path
from typing import List

from .config import ASSETS, STATE_FILE, ENV_FILE
from .env_loader import load_env
from .data_sources import fetch_binance_klines, fetch_yf_close
from .indicators import rolling_high_drawdown, rolling_low_surge
from .matrix_client import matrix_send_text, matrix_send_image
from .state import load_state, save_state
from .charts import create_asset_chart
from .thresholds import find_threshold_cross_date


def run_assets(dry_run=False, daily_report=False, send_charts=False):
    load_env(ENV_FILE)
    hs  = os.environ.get('MATRIX_HOMESERVER')
    rid = os.environ.get('MATRIX_ROOM_ID')
    tok = os.environ.get('MATRIX_ACCESS_TOKEN')
    if not (hs and rid and tok):
        print('Missing MATRIX_* env vars', file=sys.stderr)
        sys.exit(2)

    state = load_state(STATE_FILE)
    messages: List[str] = []
    daily_summary: List[str] = []

    for a in ASSETS:
        try:
            if a.get('source') == 'binance':
                s = fetch_binance_klines(a['symbol'])
            else:
                s = fetch_yf_close(a.get('ticker') or a['symbol'])
        except Exception as e:
            messages.append(f"[WARN] 获取 {a['name']} 数据失败：{e}")
            continue
        if len(s) < 2:
            continue
        today = s.index[-1]
        chart_path = None
        if daily_report:
            chart_path = Path(__file__).resolve().parent.parent / f"{a['name'].lower()}_chart.png"
            if not create_asset_chart(a['name'], s, a['window'], chart_path):
                chart_path = None
        dd = rolling_high_drawdown(s, a['window'])
        surge = rolling_low_surge(s, a['window'])
        dd_today = float(dd.iloc[-1]) if len(dd) else 0.0
        surge_today = float(surge.iloc[-1]) if len(surge) else 0.0
        asset_summary = f"**{a['name']}** ({a['window']}天): 回撤 {dd_today:.1%}, 涨幅 {surge_today:.1%}"
        threshold_notes = []
        if 'drawdown_thresholds' in a:
            for thr in a['drawdown_thresholds']:
                if dd_today <= thr:
                    cross_date = find_threshold_cross_date(dd, thr, 'below')
                    date_info = f" (穿越: {cross_date})" if cross_date else ''
                    threshold_notes.append(f"⚠️ 回撤 {thr:.0%}{date_info}")
        if 'surge_thresholds' in a:
            for thr in sorted(a['surge_thresholds'], reverse=True):
                if surge_today >= thr:
                    cross_date = find_threshold_cross_date(surge, thr, 'above')
                    date_info = f" (穿越: {cross_date})" if cross_date else ''
                    threshold_notes.append(f"📈 涨幅 {thr:.0%}{date_info}")
                    break
        if threshold_notes:
            asset_summary += '\n    ' + ', '.join(threshold_notes)
        daily_summary.append(asset_summary)
        if len(dd) >= 2 and 'drawdown_thresholds' in a:
            dd_prev = float(dd.iloc[-2])
            for thr in sorted(a['drawdown_thresholds']):
                crossed = (dd_prev > thr) and (dd_today <= thr)
                key = f"{a['name']}|drawdown|{thr}"
                if crossed and state.get(key, '') != today.date().isoformat():
                    txt = (f"【回撤提醒】{a['name']}：相对滚动高点({a['window']}D)回撤 "
                           f"{dd_today:.2%}（阈值 {thr:.0%}）\n{a['drawdown_rules'][thr]}\n"
                           f"日期：{today.date().isoformat()}")
                    messages.append(txt)
                    state[key] = today.date().isoformat()
        if len(surge) >= 2 and 'surge_thresholds' in a:
            surge_prev = float(surge.iloc[-2])
            for thr in sorted(a['surge_thresholds'], reverse=True):
                crossed = (surge_prev < thr) and (surge_today >= thr)
                key = f"{a['name']}|surge|{thr}"
                if crossed and state.get(key, '') != today.date().isoformat():
                    txt = (f"【涨幅提醒】{a['name']}：相对滚动低点({a['window']}D)涨幅 "
                           f"{surge_today:.2%}（阈值 {thr:.0%}）\n{a['surge_rules'][thr]}\n"
                           f"日期：{today.date().isoformat()}")
                    messages.append(txt)
                    state[key] = today.date().isoformat()
    if messages:
        final_msg = '\n\n'.join(messages)
        print('🚨 穿越提醒:')
        print(final_msg)
        if not dry_run:
            matrix_send_text(hs, rid, tok, final_msg)
    if daily_report and daily_summary:
        today_str = datetime.now().strftime('%Y-%m-%d')
        summary_msg = f"📊 **投资监控日报** ({today_str})\n\n" + "\n\n".join(daily_summary)
        summary_msg += f"\n\n⏰ 监控时间: {datetime.now().strftime('%H:%M:%S')} UTC"
        summary_msg += "\n🤖 来自 AlertBot 的每日简报"
        print('\n📊 每日简报:')
        print(summary_msg)
        if not dry_run:
            matrix_send_text(hs, rid, tok, summary_msg)
        if send_charts and not dry_run:
            for a in ASSETS:
                p = Path(__file__).resolve().parent.parent / f"{a['name'].lower()}_chart.png"
                if p.exists():
                    caption = f"{a['name']} {a['window']}D 价格 & 回撤/涨幅图"
                    try:
                        matrix_send_image(hs, rid, tok, p, caption=caption)
                    except Exception as e:
                        print(f"[WARN] 图表发送失败 {p.name}: {e}")
    if not messages and not daily_report:
        print('[Info] 无触发。')
    save_state(STATE_FILE, state)


def main(dry_run=False, daily_report=False, send_charts=False):
    run_assets(dry_run=dry_run, daily_report=daily_report, send_charts=send_charts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--daily-report', action='store_true')
    parser.add_argument('--send-charts', action='store_true')
    args = parser.parse_args()
    main(dry_run=args.dry_run, daily_report=args.daily_report, send_charts=args.send_charts)
