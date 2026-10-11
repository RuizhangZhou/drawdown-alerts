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

## GitHub Actions deployment (2026-10)

Production runs in `.github/workflows/asset-monitor.yml`, every **Monday 03:30 UTC**
(Berlin 05:30 CEST / 04:30 CET), preserving the former server schedule. Manual
dispatch defaults to **dry-run**; uncheck `dry_run` to send a real report.
Schedule execution can be delayed by GitHub; public scheduled workflows may be
disabled after 60 days without repository activity. Check Actions if reports stop.

Required repository Actions secrets: `MATRIX_HOMESERVER`, `MATRIX_ROOM_ID`,
`MATRIX_ACCESS_TOKEN`. Never commit `.env`, state, access tokens or generated charts.
Only schedule and manually authorized default-branch runs have notification access;
this workflow does not run on pull requests. Official actions are SHA-pinned,
the checkout token is not persisted and permissions are read-only.

The existing alert state is migrated **once** to the bot user's private Matrix
room account data (`com.rickandzoey.drawdown-alerts.state.v1`). This is not a room
message, public repository file, cache or artifact. No new storage credential is
needed. The workflow concurrency group permits only one writer. **Never run the
server timer and Actions together**. A missing or corrupt remote state causes
failure, not a silent reset. Local runs still use `state.json` unless
`ASSET_STATE_BACKEND=matrix` is set. `ASSET_STATE_FILE` optionally selects the local
state file for migration:

```bash
# Run from a trusted environment with the existing MATRIX_* variables loaded.
ASSET_STATE_FILE=/root/asset-monitor/state.json python -m asset_monitor.migrate_state
ASSET_STATE_BACKEND=matrix python -m asset_monitor.main --dry-run --daily-report --send-charts
```

Dry-run does not send notifications or update state. Successful text/chart sends
are checkpointed individually. Repeated reports on the same UTC day are skipped.
Stable Matrix transaction IDs reduce duplicates after ambiguous send failures;
this is not an unlimited cross-system exactly-once guarantee. State API failures,
missing asset data and chart-send failures make the Actions run fail visibly.
The official Binance market-data-only endpoint is used for BTC.

Rollback: disable this Actions workflow first; export the Matrix account-data
`state` object to the local state file, or configure the server service to use
`ASSET_STATE_BACKEND=matrix`; only then re-enable `asset-monitor.timer`.
Do not blindly reuse the old local state after weeks of Actions updates.

Tests: `python -m unittest discover -s tests -v`.
