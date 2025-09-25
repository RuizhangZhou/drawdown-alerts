from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .indicators import rolling_high_drawdown, rolling_low_surge


def create_asset_chart(asset_name, price_data, window, save_path: Path):
    try:
        plt.style.use('default')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        dd = rolling_high_drawdown(price_data, window)
        surge = rolling_low_surge(price_data, window)
        ax1.plot(price_data.index, price_data.values, linewidth=2, color='#2E86C1', label='Price')
        rolling_high = price_data.rolling(window=window, min_periods=1).max()
        rolling_low = price_data.rolling(window=window, min_periods=1).min()
        ax1.plot(price_data.index, rolling_high, '--', alpha=0.7, color='red', label=f'{window}D High')
        ax1.plot(price_data.index, rolling_low, '--', alpha=0.7, color='green', label=f'{window}D Low')
        ax1.set_title(f'{asset_name} Price Trend ({window} Days)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax2.fill_between(dd.index, 0, dd*100, alpha=0.7, color='red', label='Drawdown %')
        ax2.fill_between(surge.index, 0, surge*100, alpha=0.7, color='green', label='Surge %')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax2.set_title(f'{asset_name} Drawdown & Surge vs {window}D High/Low', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('Percentage %', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        return True
    except Exception as e:
        print(f'图表生成失败 {asset_name}: {e}')
        return False
