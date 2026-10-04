"""End-to-end example of the evaluation on artificial buildings: windows, forecasts, scoring.

    python -m evaluation.run_example

Twelve artificial buildings are forecast at their usable month-start origins by ANKYRA (with a stand-in for the
foundation model, so nothing is downloaded) and by three untrained baselines, and the population is scored as in the
study.  The numbers mean nothing; the example shows the data flow and the output format.
"""
from __future__ import annotations

import json

import numpy as np

import ankyra
from ankyra.history import History
from ankyra.synthetic import synthetic_history, seasonal_naive as stand_in
from evaluation import baselines, scoring, windows


def population(n_units=12, hours=16000, seed=0):
    rng = np.random.default_rng(seed); units = []
    for i in range(n_units):
        h = synthetic_history(hours)
        scale = float(rng.uniform(0.5, 3.0)); noise = rng.normal(0.0, 0.05, len(h.load_kw))
        units.append(History(np.maximum(h.load_kw * scale * (1.0 + noise), 0.0), h.temperature_c, h.day_types, h.start_timestamp))
    return units


def main():
    forecasts = {k: [] for k in ("ANKYRA", "SN-day", "SN-week", "WeekProf4")}; ys, ctxs, unit, month = [], [], [], []
    for i, h in enumerate(population()):
        usable = h.load_kw[:len(h.load_kw) - windows.HORIZON]                      # keep the last month as a target
        origins = windows.usable_origins(h.load_kw, windows.month_starts(h.start_timestamp, len(usable) + 1))[-3:]
        ctx, y, mo = windows.window_arrays(h.load_kw, origins, h.start_timestamp)
        for o in origins:                                                          # the forecaster sees nothing at or after o
            past = History(h.load_kw[:o], h.temperature_c[:o], h.day_types[:o + windows.HORIZON], h.start_timestamp)
            forecasts["ANKYRA"].append(ankyra.forecast(past, group="Office", temp_sigma_std=0.25, foundation=stand_in).trajectory_kw)
        forecasts["SN-day"].append(baselines.seasonal_naive(ctx, 24)); forecasts["SN-week"].append(baselines.seasonal_naive(ctx, 168))
        forecasts["WeekProf4"].append(baselines.week_profile(ctx))
        ys.append(y); ctxs.append(ctx); unit += [f"building_{i:02d}"] * len(origins); month += list(mo)
    F = {k: np.vstack(v) for k, v in forecasts.items()}; y = np.vstack(ys); ctx = np.vstack(ctxs); unit = np.array(unit); month = np.array(month)
    res = scoring.score_population(F, y, unit, month, reference="ANKYRA", n_boot=200)["full"]
    tests = scoring.rank_tests(scoring.unit_rmse(F, y, unit)[1])
    print(json.dumps({"windows": res["windows"], "units": res["units"],
                      "ankyra_against": {k: {"improvement_pct": round(v["improvement_pct"], 2), "interval_log": [round(v["um_low"], 4), round(v["um_high"], 4)],
                                             "resolved": v["resolved"]} for k, v in res["pairwise"].items()},
                      "mean_unit_rank": {k: round(v, 3) for k, v in res["mean_unit_rank"].items()},
                      "cv_rmse_pct": {k: round(v["CV_RMSE_pct"], 2) for k, v in res["conventional"].items()},
                      "friedman_p": tests["friedman_p"],
                      "rmsse_geo_mean": {k: round(v["RMSSE_geo_mean"], 3) for k, v in scoring.scaled_errors(F, y, ctx, unit).items()}}, indent=1))


if __name__ == "__main__":
    main()
