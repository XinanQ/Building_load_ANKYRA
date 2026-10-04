"""Forecast windows of one unit: which origins are usable, and the arrays the scoring needs.

A window at origin ``o`` (an index into the unit's hourly record) uses the 1,344 hours before ``o`` as context and the
744 hours from ``o`` as target.  It is usable when both are completely observed and the record before ``o`` is long
enough for the forecaster's pseudo-origins.  The study placed origins at the first hour of calendar months; any
spacing can be passed here.
"""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np

CONTEXT, HORIZON, STEP = 1344, 744, 744


def usable_origins(load_kw, origins, pseudo_origins=6):
    """The origins with a complete context and target and ``pseudo_origins`` completed monthly steps behind them."""
    load = np.asarray(load_kw, dtype=np.float64); keep = []
    for o in origins:
        o = int(o)
        if o - CONTEXT - pseudo_origins * STEP < 0 or o + HORIZON > len(load):
            continue
        if np.isfinite(load[o - CONTEXT:o + HORIZON]).all():
            keep.append(o)
    return np.array(keep, dtype=int)


def month_starts(start_timestamp, hours):
    """Indices of the first hour of each calendar month in a record of ``hours`` hours starting at ``start_timestamp``."""
    t0 = datetime.fromisoformat(start_timestamp.replace("Z", "+00:00")); out = []
    y, m = t0.year, t0.month
    while True:
        t = datetime(y, m, 1, tzinfo=t0.tzinfo); i = int((t - t0).total_seconds() // 3600)
        if i >= hours:
            return np.array(out, dtype=int)
        if i >= 0:
            out.append(i)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def window_arrays(load_kw, origins, start_timestamp):
    """context (n, 1344), target (n, 744) and the month label of each window's midpoint."""
    load = np.asarray(load_kw, dtype=np.float64); t0 = datetime.fromisoformat(start_timestamp.replace("Z", "+00:00"))
    ctx = np.stack([load[o - CONTEXT:o] for o in origins]); y = np.stack([load[o:o + HORIZON] for o in origins])
    month = np.array([(t0 + timedelta(hours=int(o) + HORIZON // 2)).strftime("%Y-%m") for o in origins])
    return ctx, y, month
