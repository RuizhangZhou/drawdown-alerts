from datetime import datetime
from .indicators import rolling_high_drawdown, rolling_low_surge


def find_threshold_cross_date(series, threshold, cross_type='above'):
    try:
        if cross_type == 'above':
            mask = series >= threshold
        else:
            mask = series <= threshold
        if mask.any():
            first_cross = series[mask].index[0]
            return first_cross.date().isoformat()
    except Exception:
        pass
    return None
