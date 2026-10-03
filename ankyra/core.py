"""ANKYRA: a unit's own history and a time-series foundation model, divided by blocks and weighted by the unit's errors.

For a forecast origin o the 744-hour trajectory is assembled from three orthogonal blocks (see ``ankyra.blocks``):

* within-day shape    the day-demeaned foundation-model forecast from the last 1,344 hours of load;
* level               six historical candidates (recent / long-history / annual means, each with and without weather
                      adjustment) plus the foundation model's own window mean, weighted by the inverse mean squared
                      window-mean error of each candidate at earlier pseudo-origins o - 744k and shrunk towards equal
                      weights (K0 = 8);
* centred daily path  seven historical candidate paths weighted the same way (K0 = 2).

Since 2.0 the within-day block is anchored as well (``ankyra.analog``): the unit's own analog-day shape competes with
the foundation model's shape, with a per-lead-block weight set by the unit's own errors at three completed
pseudo-origins, shrunk towards the foundation model and capped at one half.  Both shapes have zero daily means, so the
level, the daily path and the energy and peak readouts are exactly those of the 1.x division of labour.

The history-side daily means (level with the model candidate, plus the daily path) are then mixed with the foundation
model's daily means week by week (days 1-7, 8-14, 15-21, 22-31).  The weekly weights are least-squares combination
weights shrunk towards 1/2 (K0 = 2).  They are estimated on up to six completed pseudo-origin pairs of the *fixed
division* (six-candidate level plus daily path, without the model candidate) against the model's daily means, and
applied at the origin to the history-side daily means that include the model candidate.  Using the fixed division at
the pseudo-origins avoids nested pseudo-origins.  If the last 168 hours are all at or below 1e-6 kW the foundation-model trajectory is returned
unchanged (off-state rule).  The delivered trajectory is projected onto nonnegative load.

Nothing is trained on the target series.  The historical estimator is the frozen reference implementation shipped in
``ankyra.history``; this module adds the foundation-model level candidate, the week-by-week handover and the off-state
rule exactly as evaluated in the study.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Callable, Mapping, Optional, Union

import numpy as np
import torch

from .history import History, estimate_from_history
from .history import api as _api
from .history import _level
from .blocks import within_day, HORIZON, D, HR
from . import analog as _analog

CONTEXT = 1344            # hours of load given to the foundation model
STEP = 744                # spacing of pseudo-origins
K_FM = 6                  # pseudo-origins with foundation-model forecasts
K0_WEEK = 2.0             # shrinkage of the lead-week weights towards 1/2
ZERO_KW = 1e-6            # off-state threshold (kW)
WEEKS = ((0, 7), (7, 14), (14, 21), (21, 31))
GROUPS = ("Industrial", "Office", "Public", "Residential", "Commercial")

Foundation = Union[Mapping[int, np.ndarray], Callable[[np.ndarray], np.ndarray]]


@dataclass(frozen=True)
class AnkyraForecast:
    """Output of :func:`forecast`.  All quantities in kW; the energy readout is ``744 * level_kw`` kWh."""
    trajectory_kw: np.ndarray                 # (744,) delivered trajectory (nonnegative unless off-state)
    level_kw: float                           # window mean before the nonnegativity projection
    daily_means_kw: np.ndarray                # (31,) after the week-by-week handover
    within_day_kw: np.ndarray                 # (744,) day-demeaned foundation-model shape
    off_state: bool                           # True when the last 168 h were zero and the model was used unchanged
    lead_week_weights: tuple = ()             # alpha_w on the model's daily means, weeks 1-4
    level_weights: dict = field(default_factory=dict)      # candidate -> weight, including 'fm'
    fixed_division_daily_means_kw: Optional[np.ndarray] = None   # F0 (history level + daily path), for ablation
    pseudo_pairs: int = 0                     # completed pseudo-origin pairs behind the lead-week weights
    foundation_within_day_kw: Optional[np.ndarray] = None  # (744,) the foundation model's own within-day block
    analog_shape_kw: Optional[np.ndarray] = None           # (744,) the unit's analog-day shape (None when not built)
    within_trust: tuple = (0.0, 0.0, 0.0, 0.0)             # w_k on the analog shape, lead blocks 1-7, 8-14, 15-21, 22-31
    within_pseudo_pairs: int = 0              # completed pseudo-origin triples behind the within-day trust
    analog_kept: bool = False                 # False when the whole-window sanity fallback applied

    @property
    def energy_kwh(self) -> float:
        return float(HORIZON * self.level_kw)


# ----------------------------------------------------------------------------- level with the model candidate
def _level_parts(history: History, group: str, sigma: float):
    """Level hypotheses, their pseudo-origin errors and the pseudo-origin bookkeeping of the reference estimator."""
    cfg = _api.frozen_config()
    gi = GROUPS.index(group)
    curves = {i: np.asarray(cfg["source_curves"][g], dtype=np.float64) for i, g in enumerate(GROUPS) if g in cfg["source_curves"]}
    store = _api._store(history, gi, sigma)
    batcher = _api._PredictionBatcher(store)
    sigs = _api._BoundarySignatures(store, curves, "strict")
    system = SimpleNamespace(lam=cfg["signature_lambda"], mu=np.zeros(len(GROUPS)))
    b, o = np.array([0]), np.array([store.origin])
    a = cfg["level"]
    with torch.no_grad(), warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        h = _level.hypotheses(store, sigs, system, batcher, b, o, system.lam)
        err = _level.pseudo_errors(store, sigs, system, batcher, b, o, system.lam, a["K"])
        names, _, _ = _level.weights(err, a["K"], a["K0"], scale=a["scale"], prior=a["prior"], annual_in_w=a["annual_in_w"])
        pseudo = {}
        for k in range(1, K_FM + 1):
            ok = int(o[0] - k * STEP)
            if batcher.observed(0, ok):
                hk = _level.hypotheses(store, sigs, system, batcher, b, np.array([ok]), system.lam)
                pseudo[k] = {"o": ok, "l0": float(hk["l0"][0]), "s0": float(hk["s0"][0]), "truth": float(hk["truth"][0])}
    return {"h": h, "err": err, "names": names, "cfg": a, "l0": float(h["l0"][0]), "s0": float(h["s0"][0]),
            "c_bar": float(h["c_bar"][0]), "pseudo": pseudo}


def _weights(err, names, K, K0, scale, min_valid=2):
    """Inverse-MSE weights over the candidates, shrunk towards equal weights by K0 (formula of the reference package)."""
    E = {n: err[n][:, :K] for n in names}
    valid = {n: np.isfinite(E[n]) for n in names}
    counts = {n: valid[n].sum(axis=1) for n in names}
    m = {}
    for n in names:
        a = np.abs(np.where(valid[n], E[n], np.nan))
        with np.errstate(all="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)          # all-missing rows are handled by min_valid below
            m[n] = np.nanmedian(a, axis=1) if scale == "mad" else np.sqrt(np.nanmean(a ** 2, axis=1))
        m[n] = np.where(counts[n] >= min_valid, m[n], np.nan)
    avail = np.stack([np.isfinite(m[n]) for n in names], axis=1)
    inv = np.stack([np.where(np.isfinite(m[n]), 1.0 / np.maximum(m[n], 1e-6) ** 2, 0.0) for n in names], axis=1)
    what = inv / np.maximum(inv.sum(axis=1, keepdims=True), 1e-300)
    w0 = avail / np.maximum(avail.sum(axis=1, keepdims=True), 1)
    k_eff = (valid["s_u"] & valid["l_u"]).sum(axis=1).astype(np.float64)[:, None]
    w = (k_eff * what + K0 * w0) / (k_eff + K0)
    none = avail.sum(axis=1) == 0
    w[none] = 1.0 / len(names)
    return w


def _level_path(h, names, w):
    H = np.stack([np.where(np.isfinite(h[n]), h[n], 0.0) for n in names], axis=1)
    w = np.where(np.isfinite(np.stack([h[n] for n in names], axis=1)), w, 0.0)
    w = w / np.maximum(w.sum(axis=1, keepdims=True), 1e-300)
    lvl = (H * w).sum(axis=1)
    w_w = w[:, [i for i, n in enumerate(names) if n in _level.W_SET]].sum(axis=1)
    return lvl[:, None] + w_w[:, None] * h["g_h"] + h["c_d"], w


def level_with_model_candidate(parts, fm_mean_origin: float, fm_means_pseudo: Mapping[int, float]):
    """Level (kW) with the foundation model's window mean as an extra candidate, and the candidate weights."""
    h, err, names, a = parts["h"], parts["err"], parts["names"], parts["cfg"]
    K = a["K"]
    err_x = {n: err[n].copy() for n in names}
    err_x["fm"] = np.full((1, K), np.nan)
    for k in range(1, K + 1):
        p = parts["pseudo"].get(k)
        if p is None or k not in fm_means_pseudo:
            continue
        err_x["fm"][0, k - 1] = (fm_means_pseudo[k] - p["l0"]) / p["s0"] - p["truth"]
    names_x = list(names) + ["fm"]
    h_x = dict(h)
    h_x["fm"] = np.array([(fm_mean_origin - parts["l0"]) / parts["s0"] - parts["c_bar"]])
    w = _weights(err_x, names_x, K, a["K0"], a["scale"])
    la, used = _level_path(h_x, names_x, w)
    return float(parts["l0"] + parts["s0"] * la[0].mean()), dict(zip(names_x, used[0].tolist()))


# ----------------------------------------------------------------------------- week-by-week handover
def lead_week_weights(pairs, k0: float = K0_WEEK):
    """Least-squares weight on the model's daily means for each lead week, shrunk towards 1/2.

    pairs: list of (realised daily means, fixed-division daily means, model daily means), each (31,), from completed
    pseudo-origins; the fixed division is the six-candidate historical level plus the daily path.
    Returns four weights alpha_w in [0, 1]."""
    out = []
    for a0, a1 in WEEKS:
        num = den = 0.0
        n = 0
        for y, hh, ff in pairs:
            e_h = hh[a0:a1] - y[a0:a1]
            d = ff[a0:a1] - hh[a0:a1]
            num += float((-e_h * d).sum())
            den += float((d * d).sum())
            n += 1
        lam = min(max(num / den, 0.0), 1.0) if den > 0 else 0.5
        out.append((n * lam + k0 * 0.5) / (n + k0))
    return out


def lead_week_transition(daily_hist, daily_fm, alphas):
    """Week-wise convex combination of the historical and model daily means."""
    out = np.array(daily_hist, dtype=np.float64, copy=True)
    for (a0, a1), al in zip(WEEKS, alphas):
        out[a0:a1] = al * daily_fm[a0:a1] + (1 - al) * daily_hist[a0:a1]
    return out


# ----------------------------------------------------------------------------- driver
def pseudo_origin_contexts(load_kw: np.ndarray, k_max: int = K_FM):
    """Contexts the foundation model must forecast from: k = 0 (the origin) and pseudo-origins o - 744k.

    Returns {k: (1344,) context} for every k whose context is completely observed."""
    load = np.asarray(load_kw, dtype=np.float64)
    o = len(load)
    out = {}
    for k in range(0, k_max + 1):
        ok = o - k * STEP
        if ok - CONTEXT >= 0 and np.isfinite(load[ok - CONTEXT:ok]).all():
            out[k] = load[ok - CONTEXT:ok]
    return out


def _foundation_map(foundation: Foundation, load_kw) -> dict:
    if callable(foundation):
        ctx = pseudo_origin_contexts(load_kw)
        keys = sorted(ctx)
        pred = np.asarray(foundation(np.stack([ctx[k] for k in keys])), dtype=np.float64)
        if pred.shape != (len(keys), HORIZON):
            raise ValueError(f"foundation forecaster must return ({len(keys)}, {HORIZON}), got {pred.shape}")
        return dict(zip(keys, pred))
    return {int(k): np.asarray(v, dtype=np.float64) for k, v in foundation.items() if v is not None}


def forecast(history: History, *, group: str, temp_sigma_std: float, foundation: Foundation, dst_region: str = "none",
             within_anchor: bool = True) -> AnkyraForecast:
    """ANKYRA forecast for the 744 hours after the end of ``history``.

    history         pre-origin hourly load and temperature and the calendar through the horizon (``ankyra.History``)
    group           category used by the temperature-signature prior: Industrial, Office, Public, Residential, Commercial
    temp_sigma_std  fixed temperature-anomaly scale (units of 10 degC), estimated before the first origin
    foundation      either {k: 744-hour forecast issued at o - 744k} for k = 0..6 (k = 0 required), or a callable that maps
                    an (N, 1344) array of contexts to (N, 744) point forecasts (e.g. ``ankyra.timesfm_adapter``), or
                    None for the history-only configuration (no foundation model: within-day default, no model
                    candidate, no handover; a reduced configuration kept for ablation and offline use)
    dst_region      daylight-saving rule used to match analog days: "EU", "US" or "none"
    within_anchor   False reproduces the 1.x forecast (foundation model's within-day block unchanged)
    """
    load = np.asarray(history.load_kw, dtype=np.float64)
    temp = np.asarray(history.temperature_c, dtype=np.float32)
    types = np.asarray(history.day_types)
    obs = np.isfinite(load) if history.observed is None else np.asarray(history.observed, dtype=bool)
    o = len(load)
    if foundation is None:
        return _history_only(history, load, temp, types, group, temp_sigma_std)
    T = _foundation_map(foundation, load)
    if 0 not in T or T[0].shape != (HORIZON,):
        raise ValueError("a 744-hour foundation-model forecast at the origin (k = 0) is required")
    T0 = T[0]
    wT0 = within_day(T0)

    if np.nanmax(load[o - 168:o]) <= ZERO_KW:                         # off-state rule
        return AnkyraForecast(trajectory_kw=T0.copy(), level_kw=float(T0.mean()), daily_means_kw=T0.reshape(D, HR).mean(1),
                              within_day_kw=wT0, off_state=True, foundation_within_day_kw=wT0)

    parts = _level_parts(history, group, temp_sigma_std)
    est = estimate_from_history(history, group=group, temp_sigma_std=temp_sigma_std)
    daily_f0 = est.level_kw + np.asarray(est.daily_path_kw, dtype=np.float64)          # fixed division (F0)

    fm_ps = {k: float(T[k].mean()) for k in range(1, K_FM + 1) if k in parts["pseudo"] and k in T}
    lvl, w_level = level_with_model_candidate(parts, float(T0.mean()), fm_ps)
    daily_level = daily_f0 - daily_f0.mean() + lvl                                     # model candidate in the level

    pairs = []                                   # fixed division vs the model at completed pseudo-origins (see module docstring)
    for k in range(1, K_FM + 1):
        p = parts["pseudo"].get(k)
        if p is None or k not in T:
            continue
        ok = p["o"]
        ek = estimate_from_history(History(load_kw=load[:ok], temperature_c=temp[:ok], day_types=types[:ok + HORIZON],
                                           start_timestamp=history.start_timestamp, observed=obs[:ok]),
                                   group=group, temp_sigma_std=temp_sigma_std)
        pairs.append((load[ok:ok + HORIZON].reshape(D, HR).mean(1), ek.level_kw + ek.daily_path_kw, T[k].reshape(D, HR).mean(1)))
    alphas = lead_week_weights(pairs) if pairs else [0.5] * 4
    daily = lead_week_transition(daily_level, T0.reshape(D, HR).mean(1), alphas)

    W, S0, trust, n_w, kept = wT0, None, (0.0, 0.0, 0.0, 0.0), 0, False
    if within_anchor:                                                 # within-day anchoring (2.0)
        shapes = _analog.AnalogShapes(load, temp, types, history.start_timestamp, dst_region, origin=o)
        S0, kept = shapes.shape_with_sanity(o, wT0)
        triples = []
        for k in range(1, _analog.K_WITHIN + 1):
            q = o - k * STEP
            if k not in T or q - CONTEXT < 0 or not (obs[q - CONTEXT:q + HORIZON].all() and np.isfinite(load[q - CONTEXT:q + HORIZON]).all()):
                continue
            wTq = within_day(T[k]); Sq, _ = shapes.shape_with_sanity(q, wTq)
            triples.append((Sq, wTq, within_day(load[q:q + HORIZON])))
        w, n_w = _analog.within_trust(triples); trust = tuple(float(x) for x in w)
        W = _analog.anchored_within_day(wT0, S0, w)

    raw = np.repeat(daily, HR) + W
    return AnkyraForecast(trajectory_kw=np.maximum(raw, 0.0), level_kw=float(daily.mean()), daily_means_kw=daily,
                          within_day_kw=W, off_state=False, lead_week_weights=tuple(float(a) for a in alphas),
                          level_weights=w_level, fixed_division_daily_means_kw=daily_f0, pseudo_pairs=len(pairs),
                          foundation_within_day_kw=wT0, analog_shape_kw=S0, within_trust=trust, within_pseudo_pairs=n_w, analog_kept=kept)


def _history_only(history, load, temp, types, group, temp_sigma_std) -> AnkyraForecast:
    """History-only configuration: fixed division with the same-day-type within-day default (no foundation model)."""
    from .readouts import within_day_default
    o = len(load)
    est = estimate_from_history(history, group=group, temp_sigma_std=temp_sigma_std)
    daily = est.level_kw + np.asarray(est.daily_path_kw, dtype=np.float64)
    ctx = load[o - CONTEXT:o]
    if not np.isfinite(ctx).all():
        raise ValueError("the history-only configuration needs a complete 1,344-hour context")
    ct = types[o - CONTEXT + 12 + HR * np.arange(CONTEXT // HR)]; tt = types[o + 12 + HR * np.arange(D)]
    W = within_day_default(ctx[None], ct[None], tt[None])[0]
    raw = np.repeat(daily, HR) + W
    return AnkyraForecast(trajectory_kw=np.maximum(raw, 0.0), level_kw=float(daily.mean()), daily_means_kw=daily, within_day_kw=W,
                          off_state=False, fixed_division_daily_means_kw=daily)
