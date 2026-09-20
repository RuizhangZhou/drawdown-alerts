# Asset Monitor

Automated monitoring for asset drawdowns and sharp rallies with Matrix notifications.

## 🏗️ Project Layout
```
asset-monitor/
├── asset_monitor/        # modular package
│   ├── main.py           # main orchestrator
│   ├── config.py         # asset definitions and constants
│   ├── data_sources.py   # data fetching
│   ├── indicators.py     # indicator calculations
│   ├── charts.py         # chart rendering
│   ├── thresholds.py     # threshold crossover dates
│   ├── matrix_client.py  # Matrix helpers
│   ├── state.py          # state persistence
│   └── env_loader.py     # .env loader
├── requirements.txt      # Python dependencies
├── README.md             # documentation
├── .gitignore            # Git ignore rules
├── .env                  # Matrix configuration (create manually)
├── state.json            # runtime state (auto-generated)
└── cron.log              # cron execution log (auto-generated)
```

## 📊 Configured Assets

### BTC (BTCUSDT) — 60-day window
- **Drawdown thresholds**: -10% -> +€50, -20% -> an additional +€50 (maximum +€150 this month)
- **Surge thresholds**: +15%/+25% -> reminder to scale back investments

### Gold (GLD ETF) — 60-day window
- **Drawdown thresholds**: -4% -> +€50, -8% -> an additional +€50 (maximum +€100 this month)
- **Surge thresholds**: +6%/+12% -> reminder to reduce investments

### S&P500 (SPY ETF) — 90-day window
- **Drawdown thresholds**: -5% -> +€100, -10% -> +€200
- **Surge thresholds**: +8%/+15% -> reminder to pause new investments

## 🎯 Monitoring Mechanics
- **Drawdown monitoring**: drop versus the rolling high
- **Surge monitoring**: gain versus the rolling low
- **Threshold alerts**: trigger only on crossovers to avoid alert fatigue
- **Weekly briefing**: current status plus crossover dates
- **Charts**: automatically generated price and drawdown/surge plots
- **State tracking**: persist state.json to avoid duplicate alerts on the same day

## ⚙️ Setup

### 1. Create the environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Matrix credentials (.env)
```bash
MATRIX_HOMESERVER=https://your.matrix.server
MATRIX_ACCESS_TOKEN=your_access_token
MATRIX_ROOM_ID=!your_room_id:server.com
```

### 3. Schedule the cron job
```bash
crontab -e
# add (Monday 03:30 UTC report + charts):
# 30 3 * * 1 /root/asset-monitor/.venv/bin/python -m asset_monitor.main --daily-report --send-charts >> /root/asset-monitor/cron.log 2>&1
```

## 🧪 Manual Checks
```bash
source .venv/bin/activate
python -m asset_monitor.main --dry-run
python -m asset_monitor.main --daily-report --send-charts
```

## 🤖 Matrix Bot
- Uses AlertBot (`@alertbot:rickandzoey.com`) for outbound notifications
- Shared across multiple projects

## 📝 Notes
- Sensitive files are excluded via `.gitignore`
- Edit `asset_monitor/config.py` to add more assets
- Log output: `cron.log`
