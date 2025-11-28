from datetime import datetime
from .indicators import rolling_high_drawdown, rolling_low_surge


def find_threshold_cross_date(series, threshold, cross_type='above'):
    try:
        if cross_type == 'above':
            mask = series >= threshold
        else:
            mask = series <= threshold

        if not mask.any():
            return None

        # Find the start of the current (most recent) continuous period where threshold is crossed
        # Work backwards from the latest date to find when the current streak started
        mask_series = mask.astype(int)

        # If the latest value doesn't meet the threshold, return None
        if not mask.iloc[-1]:
            return None

        # Find the start of the current continuous period
        # Look for the last transition from False to True (0 to 1)
        diff = mask_series.diff()

        # Find where the mask changes from 0 to 1 (start of crossing periods)
        cross_starts = diff[diff == 1].index

        if len(cross_starts) == 0:
            # If no transitions found, the entire series meets the threshold
            return series.index[0].date().isoformat()

        # Get the most recent crossing start date
        latest_cross_start = cross_starts[-1]
        return latest_cross_start.date().isoformat()

    except Exception:
        pass
    return None
