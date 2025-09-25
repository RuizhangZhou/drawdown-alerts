from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "state.json"
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

ASSETS = [
    {
        "name": "BTC",
        "source": "binance",
        "symbol": "BTCUSDT",
        "window": 60,
        "drawdown_thresholds": [-0.10, -0.20],
        "surge_thresholds": [0.15, 0.25],
        "drawdown_rules": {
            -0.10: "规则：距60天高点-10% → +€50（把下一次BTC周投从€50提到€100，或加一笔€50）",
            -0.20: "规则：距60天高点-20% → 再+€50（同月BTC触发合计最多+€150）",
        },
        "surge_rules": {
            0.15: "提醒：BTC 近期涨幅较大，考虑适当减少下次投资至 €30",
            0.25: "提醒：BTC 涨幅显著，暂停本月投资或减至 €20",
        },
    },
    {
        "name": "Gold",
        "source": "yahoo",
        "ticker": "GLD",
        "window": 60,
        "drawdown_thresholds": [-0.04, -0.08],
        "surge_thresholds": [0.06, 0.12],
        "drawdown_rules": {
            -0.04: "规则：距60天高点-4% → +€50（将下一次半月金从€215调到€265）",
            -0.08: "规则：距60天高点-8% → 再+€50（本月黄金加注最多+€100）",
        },
        "surge_rules": {
            0.06: "提醒：黄金涨幅较大，下次投资减少至 €165（-€50）",
            0.12: "提醒：黄金大幅上涨，暂停本月投资",
        },
    },
    {
        "name": "S&P500",
        "source": "yahoo",
        "ticker": "SPY",
        "window": 90,
        "drawdown_thresholds": [-0.05, -0.10],
        "surge_thresholds": [0.08, 0.15],
        "drawdown_rules": {
            -0.05: "规则：距90天高点-5% → 当月+€100（把当月S&P由€320/€370调高€100；若当月黄金未执行，可把其中一次黄金从€215暂调到€165来给S&P腾额度）",
            -0.10: "规则：距90天高点-10% → S&P大幅回调，考虑额外加投+€200",
        },
        "surge_rules": {
            0.08: "提醒：S&P500 涨幅较大，考虑暂缓新增投资",
            0.15: "提醒：S&P500 大幅上涨，建议获利了结部分仓位",
        },
    },
]
