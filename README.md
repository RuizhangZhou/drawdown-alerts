# Asset Monitor 资产监控系统

自动监控资产回撤与过度上涨，并通过Matrix发送提醒的系统。

## 🏗️ 文件结构
```
asset-monitor/
├── asset_monitor/        # 模块化包
│   ├── main.py           # 主流程 orchestrator
│   ├── config.py         # 资产 & 常量
│   ├── data_sources.py   # 数据抓取
│   ├── indicators.py     # 指标计算
│   ├── charts.py         # 图表生成
│   ├── thresholds.py     # 阈值穿越日期
│   ├── matrix_client.py  # Matrix 发送
│   ├── state.py          # 状态读写
│   └── env_loader.py     # .env 读取
├── requirements.txt      # Python依赖
├── README.md            # 说明文档
├── .gitignore          # Git忽略文件
├── .env                # Matrix配置 (需要手动创建)
├── state.json          # 运行状态记录 (自动生成)
└── cron.log           # Cron执行日志 (自动生成)
```

## 📊 配置的资产

### BTC (BTCUSDT) - 60天窗口
- **回撤阈值**: -10% → +€50，-20% → 再+€50 (合计最多+€150)
- **涨幅阈值**: +15%/+25% → 减少投资提醒

### Gold (GLD ETF) - 60天窗口
- **回撤阈值**: -4% → +€50，-8% → 再+€50 (合计最多+€100)
- **涨幅阈值**: +6%/+12% → 减少投资提醒

### S&P500 (SPY ETF) - 90天窗口
- **回撤阈值**: -5% → +€100，-10% → +€200
- **涨幅阈值**: +8%/+15% → 暂缓投资提醒

## 🎯 监控机制
- **回撤监控**: 相对滚动高点的下跌幅度
- **涨幅监控**: 相对滚动低点的上涨幅度
- **穿越提醒**: 只在跨越阈值瞬间触发（避免重复骚扰）
- **每日简报**: 显示当前状态 + 阈值穿越日期
- **可视化图表**: 自动生成价格趋势和回撤/涨幅图
- **状态记录**: 使用state.json防止同一天重复提醒

## ⚙️ 安装和配置

### 1. 设置环境
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置Matrix (.env)
```bash
MATRIX_HOMESERVER=https://your.matrix.server
MATRIX_ACCESS_TOKEN=your_access_token
MATRIX_ROOM_ID=!your_room_id:server.com
```

### 3. 设置定时任务
```bash
crontab -e
# 添加 (每日 03:30 发送日报 + 图表):
# 30 3 * * * /root/asset-monitor/.venv/bin/python -m asset_monitor.main --daily-report --send-charts >> /root/asset-monitor/cron.log 2>&1
```

## 🧪 手动测试
```bash
source .venv/bin/activate
python -m asset_monitor.main --dry-run
python -m asset_monitor.main --daily-report --send-charts
```

## 🤖 Matrix机器人
- 使用AlertBot (`@alertbot:rickandzoey.com`) 发送提醒
- 可供多个项目共享使用

## 📝 注意事项
- 敏感文件已在`.gitignore`中排除
- 如需添加更多资产，编辑 `asset_monitor/config.py` 中的 `ASSETS` 配置
- 日志文件：`cron.log`
