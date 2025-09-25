#!/usr/bin/env python3
"""兼容旧入口：重定向到新的模块化实现。
建议以后使用: python -m asset_monitor.main
"""
import argparse
from asset_monitor.main import main

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='(Deprecated) 请改用 python -m asset_monitor.main')
    ap.add_argument('--dry-run', action='store_true', help='只计算不发送')
    ap.add_argument('--daily-report', action='store_true', help='生成每日简报')
    ap.add_argument('--send-charts', action='store_true', help='在每日简报后发送各资产图表')
    args = ap.parse_args()
    main(dry_run=args.dry_run, daily_report=args.daily_report, send_charts=args.send_charts)