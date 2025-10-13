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
            -0.10: "Rule: 10% below the 60-day high -> add €50 (raise the next weekly BTC buy from €50 to €100, or add an extra €50 buy)",
            -0.20: "Rule: 20% below the 60-day high -> add another €50 (limit the total BTC top-up this month to €150)",
        },
        "surge_rules": {
            0.15: "Reminder: BTC has climbed sharply, consider reducing the next investment to €30",
            0.25: "Reminder: BTC surged significantly, pause this month's investment or cut it to €20",
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
            -0.04: "Rule: 4% below the 60-day high -> add €50 (raise the next semi-monthly gold buy from €215 to €265)",
            -0.08: "Rule: 8% below the 60-day high -> add another €50 (cap the monthly gold top-up at an extra €100)",
        },
        "surge_rules": {
            0.06: "Reminder: Gold is up notably, reduce the next investment to €165 (-€50)",
            0.12: "Reminder: Gold rallied sharply, pause this month's investment",
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
            -0.05: "Rule: 5% below the 90-day high -> add €100 (increase this month's S&P allocation by €100; if gold was skipped, shift one €215 gold order down to €165 to free budget)",
            -0.10: "Rule: 10% below the 90-day high -> significant S&P pullback, consider adding €200",
        },
        "surge_rules": {
            0.08: "Reminder: S&P500 has risen notably, consider pausing new contributions",
            0.15: "Reminder: S&P500 rallied sharply, consider taking some profits",
        },
    },
]
