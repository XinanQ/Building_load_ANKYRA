"""Scoring of one population: the tables of the benchmark from forecasts and realised load.

Inputs are plain arrays, one row per forecast window (see ``evaluation/README.md``):

    forecasts   {model name: (n, 744) hourly forecast in kW}; a model that exists only on part of the windows (the
                trained baselines, which exist after their training cutoff) has NaN rows elsewhere
    y           (n, 744) realised load in kW
    unit        (n,) unit label of each window
    month       (n,) label of the month that holds the window's midpoint (the bootstrap resamples these)
    context     (n, 1344) load before the origin; needed for the scaled errors only

``score_population`` returns two blocks with the same content: ``full`` (all windows, the models that cover them all)
and ``late`` (the windows every model covers, all models).  Each block holds

    pairwise        the reference forecaster against every other model: unit-equal log RMS ratio (negative favours the
                    reference), its 95% unit-and-month bootstrap interval, the improvement 100[1 - exp(r)] and the
                    pooled MSE ratio
    mean_unit_rank  mean over units of each model's rank by that unit's RMSE; the reference's own reduced versions
                    (``family``) are left out of the ranking, as in the study
    conventional    RMSE, MAE, CV(RMSE), NMBE, WAPE per model

The estimands are those of ``ankyra.metrics``; this module only arranges them into the released tables.  The interval
uses 2,000 replicates and, by default, the seed of the study, with a fresh generator for every contrast.
"""
from __future__ import annotations

import math

import numpy as np

from ankyra import metrics

SEED = 20260935            # seed of the study's panel scoring; a fresh generator is drawn for every contrast
SEASON = 168               # weekly seasonal-naive lag of the scaled errors


def window_mse(pred, y):
    return ((np.asarray(pred, dtype=np.float64) - y) ** 2).mean(1)


def block(forecasts, y, unit, month, reference, family=(), seed=SEED, n_boot=metrics.N_BOOT):
    """Pairwise contrasts, mean unit ranks and conventional metrics on one set of windows."""
    y = np.asarray(y, dtype=np.float64); unit = np.asarray(unit); month = np.asarray(month)
    for name, p in forecasts.items():
        if np.shape(p) != y.shape or not np.isfinite(p).all():
            raise ValueError(f"forecast {name!r} must be finite with the shape of y on these windows")
    mse = {k: window_mse(p, y) for k, p in forecasts.items()}
    out = {"windows": int(len(y)), "units": int(len(np.unique(unit))), "months": int(len(np.unique(month))), "reference": reference,
           "pairwise": {}, "conventional": {k: metrics.conventional(np.asarray(p, dtype=np.float64), y, unit) for k, p in forecasts.items()}}
    for k in forecasts:
        if k == reference:
            continue
        r = metrics.log_ratio(mse[reference], mse[k], unit)
        iv = metrics.um_interval(mse[reference], mse[k], unit, month, np.random.default_rng(seed), n_boot)["UM"]
        out["pairwise"][k] = {"log_ratio": r, "um_low": iv[0], "um_high": iv[1], "improvement_pct": 100 * (1 - math.exp(r)),
                              "pooled_mse_ratio": float(mse[reference].mean() / mse[k].mean()),
                              "resolved": "better" if iv[1] < 0 else "worse" if iv[0] > 0 else "no"}
    out["mean_unit_rank"] = metrics.mean_unit_rank({k: v for k, v in mse.items() if k not in family}, unit)
    return out


def score_population(forecasts, y, unit, month, reference="ANKYRA", family=(), seed=SEED, n_boot=metrics.N_BOOT):
    """The full-window and late-window blocks of one population (see the module docstring)."""
    y = np.asarray(y, dtype=np.float64)
    covered = {k: np.isfinite(np.asarray(p, dtype=np.float64)).all(1) for k, p in forecasts.items()}
    if not covered[reference].all():
        raise ValueError("the reference forecaster must cover every window")
    everywhere = [k for k, c in covered.items() if c.all()]
    late = np.logical_and.reduce(list(covered.values()))
    out = {"full": block({k: forecasts[k] for k in everywhere}, y, unit, month, reference, family, seed, n_boot)}
    if late.any() and len(everywhere) < len(forecasts):
        out["late"] = block({k: np.asarray(p)[late] for k, p in forecasts.items()}, y[late], np.asarray(unit)[late], np.asarray(month)[late],
                            reference, family, seed, n_boot)
    return out


def unit_rmse(forecasts, y, unit):
    """{model: per-unit RMSE over the unit's windows}, with the unit labels."""
    uu, inv = np.unique(unit, return_inverse=True); cnt = np.bincount(inv)
    return uu, {k: np.sqrt(np.bincount(inv, window_mse(p, y), len(uu)) / cnt) for k, p in forecasts.items()}


def rank_tests(unit_rmse_by_model, reference="ANKYRA", alpha=0.05):
    """Friedman test, mean ranks, Nemenyi critical difference, and Holm-corrected Wilcoxon signed-rank tests of the
    reference against every other model, with units as blocks (Demsar 2006; Garcia and Herrera 2008)."""
    from scipy import stats
    models = sorted(unit_rmse_by_model); X = np.stack([unit_rmse_by_model[m] for m in models], 1); n, k = X.shape
    mean_rank = dict(zip(models, stats.rankdata(X, axis=1).mean(0)))
    fr = stats.friedmanchisquare(*[X[:, j] for j in range(k)])
    cd = float(stats.studentized_range.ppf(1 - alpha, k, np.inf) / math.sqrt(2) * math.sqrt(k * (k + 1) / (6 * n)))
    a = X[:, models.index(reference)]; raw = {}
    for j, m in enumerate(models):
        if m != reference:
            raw[m] = float(stats.wilcoxon(a, X[:, j], zero_method="wilcox").pvalue) if np.any(a != X[:, j]) else 1.0
    holm, run = {}, 0.0
    for i, m in enumerate(sorted(raw, key=raw.get)):
        run = max(run, min(1.0, (len(raw) - i) * raw[m])); holm[m] = run
    return {"units": int(n), "models": int(k), "friedman_p": float(fr.pvalue), "nemenyi_cd": cd, "mean_rank": {m: float(v) for m, v in mean_rank.items()},
            "wilcoxon_holm_p": holm,
            "significantly_better_than": [m for m in holm if holm[m] < alpha and mean_rank[reference] < mean_rank[m]],
            "significantly_worse_than": [m for m in holm if holm[m] < alpha and mean_rank[reference] > mean_rank[m]]}


def scaled_errors(forecasts, y, context, unit):
    """RMSSE and MASE per model: errors scaled by the in-sample weekly seasonal-naive error over the context, per unit,
    summarised by the median and the geometric mean over units.  Windows with a zero scale are left out."""
    d = context[:, SEASON:] - context[:, :-SEASON]; s2 = (d ** 2).mean(1); s1 = np.abs(d).mean(1); ok = (s2 > 0) & (s1 > 0)
    uu, inv = np.unique(np.asarray(unit)[ok], return_inverse=True); cnt = np.bincount(inv); out = {}
    for k, p in forecasts.items():
        e = (np.asarray(p, dtype=np.float64) - y)[ok]
        rmsse = np.sqrt(np.bincount(inv, (e ** 2).mean(1) / s2[ok], len(uu)) / cnt); mase = np.bincount(inv, np.abs(e).mean(1) / s1[ok], len(uu)) / cnt
        out[k] = {"RMSSE_median_unit": float(np.median(rmsse)), "RMSSE_geo_mean": float(np.exp(np.log(rmsse[rmsse > 0]).mean())),
                  "MASE_median_unit": float(np.median(mase)), "MASE_geo_mean": float(np.exp(np.log(mase[mase > 0]).mean())), "units": int(len(uu))}
    return out


def energy_error(forecasts, y, unit, month, reference="ANKYRA", seed=SEED, n_boot=metrics.N_BOOT):
    """The primary estimand applied to the monthly energy error (744 x the error of the window mean) instead of the
    hourly error."""
    lev = {k: (y - np.asarray(p, dtype=np.float64)).mean(1) ** 2 for k, p in forecasts.items()}; out = {}      # mean of the hourly errors, as in the study
    for k in forecasts:
        if k != reference:
            r = metrics.log_ratio(lev[reference], lev[k], unit)
            iv = metrics.um_interval(lev[reference], lev[k], unit, month, np.random.default_rng(seed), n_boot)["UM"]
            out[k] = {"log_ratio": r, "um_low": iv[0], "um_high": iv[1], "improvement_pct": 100 * (1 - math.exp(r))}
    return out


def by_forecast_day(forecasts, y, unit):
    """Hourly loss by forecast day: for each model the geometric mean, over one fixed set of units, of the day's
    CV(RMSE) (the unit's RMSE over that day's 24 hours in all its windows, over the unit's mean load).  The unit set is
    the units with a mean load of at least 1e-6 kW and a nonzero error on every day for every model."""
    y = np.asarray(y, dtype=np.float64); uu = np.unique(unit); days = y.shape[1] // 24; r = {}
    ybar = np.array([y[unit == u].mean() for u in uu])
    for k, p in forecasts.items():
        e = (y - np.asarray(p, dtype=np.float64)).reshape(len(y), days, 24)
        r[k] = np.stack([np.sqrt((e[unit == u] ** 2).mean(axis=(0, 2))) for u in uu])
    keep = (np.abs(ybar) >= 1e-6) & np.logical_and.reduce([(v > 0).all(1) for v in r.values()])
    return {"units_in_set": int(keep.sum()), "gm_cv_rmse_pct": {k: np.exp(np.log(100 * v[keep] / ybar[keep, None]).mean(0)) for k, v in r.items()}}
