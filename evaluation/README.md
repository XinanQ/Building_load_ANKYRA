# Evaluation code

This folder holds the scoring used for the benchmark, written as a small module on top of `ankyra.metrics`. Given the
forecasts of several models on the same windows and the realised load, it produces the tables in
[`results/`](../results/). It is not imported by the forecaster.

| File | Content |
|---|---|
| `scoring.py` | `score_population` (pairwise contrasts with bootstrap intervals, mean per-unit ranks and conventional metrics, on all windows and on the late windows), `rank_tests` (Friedman, Nemenyi, Holm-corrected Wilcoxon), `scaled_errors` (RMSSE, MASE), `energy_error`, `by_forecast_day`. |
| `windows.py` | Which origins of a unit's record are usable, month-start origins, and the context, target and month label of each window. |
| `baselines.py` | The three untrained reference forecasters that need only the load context: seasonal naive (day, week) and the four-week profile. |
| `run_example.py` | The whole flow on twelve artificial buildings: windows, ANKYRA and the three baselines, scoring. No data and no downloads. |

```bash
python -m evaluation.run_example
```

## Input format

One row per forecast window, the same rows in every array:

| Array | Shape | Meaning |
|---|---|---|
| `forecasts[name]` | (n, 744) | hourly forecast in kW. A model that exists only on part of the windows has NaN rows elsewhere. |
| `y` | (n, 744) | realised load in kW |
| `unit` | (n,) | unit label; the estimand weights units equally |
| `month` | (n,) | label of the month holding the window's midpoint; the bootstrap resamples units and months |
| `context` | (n, 1344) | load before the origin (scaled errors only) |

`score_population(forecasts, y, unit, month, reference="ANKYRA", family=(...))` returns a `full` block (all windows,
the models that cover them all) and a `late` block (the windows every model covers, all models). `family` names the
reference's own reduced versions; they get a pairwise contrast but are left out of the ranking.

## What was checked

On the study's saved forecasts this module reproduces the released tables of the populations it was run on (BDG2,
Cambridge, GoiEner households and the Suzhou park): the pairwise log ratios and their intervals, the mean per-unit
ranks, the conventional metrics, the rank tests, the scaled errors, the energy contrasts and the loss by forecast day.
The intervals reproduce because the default seed is the study's and a fresh generator is drawn for each contrast.

## What is not here

- **The forecasts themselves.** Raw data, saved forecast arrays and model weights are not in the repository
  ([docs/DATA.md](../docs/DATA.md) lists the sources and how the inputs were prepared).
- **The other baselines.** The trained models (TiDE, iTransformer, GBT-T, DLinear, PatchTST, LSTM), the
  covariate-informed foundation-model variants, Holt–Winters, MSTL, the per-unit ridge and the remaining profiles are
  specified in [docs/EVALUATION.md](../docs/EVALUATION.md#baselines) and
  [docs/METHOD.md](../docs/METHOD.md#inputs-and-features-the-shared-information-set); their training and inference
  code is not included.
- **The study's own pipeline.** The tables were produced by the study's research scripts. This module is a clean
  re-implementation of their scoring, checked against their output as described above.
