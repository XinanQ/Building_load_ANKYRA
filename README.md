# ANKYRA

**Month-ahead hourly load forecasts that anchor a time-series foundation model to each unit's own history**

[中文说明](README.zh-CN.md) · [Install and run](#install-and-run) · [Your own data](#forecast-your-own-unit) · [Method](docs/METHOD.md) · [Theory](theory/) · [Evaluation](docs/EVALUATION.md) · [Data](docs/DATA.md) · [Scoring code](evaluation/) · [Results data](results/)

ANKYRA forecasts the hourly electricity load of one unit (a building, a meter or a supply point) for the next 31 days
(744 hours); it is meant for researchers and practitioners who need month-ahead load or energy forecasts for many units
without training or fine-tuning a neural network on each of them. It combines the zero-shot forecast of a pretrained foundation model,
TimesFM 2.5, with estimates from the unit's own past load, outdoor temperature and calendar, and weights the two by how
well each has forecast the unit's own earlier months.

Current package version: **2.2.0**; the forecasting model is ANKYRA 2.2 (6 October 2026; `gap_tolerance=False` reproduces 2.1; `gap_tolerance=False, single_trust=False` reproduces 2.0.1)
([what changed](#what-changed-in-20-201-21-and-22) · [version history](#version-history)).

![ANKYRA architecture](figures/fig1_architecture.png)

*Figure 1. Architecture.*

With an eight-week (1,344-hour) context, as used here, pretrained time-series foundation models reproduce the shape
of a day well, but over a 31-day horizon their monthly level follows the last few days and drifts; with a one-year
context TimesFM improved modestly. A unit's own history anchors the month, but reacts slowly and cannot
represent a load that has switched off. **ANKYRA** (Greek *ἄγκυρα*, anchor) uses each source where it is reliable, and
lets the unit's own forecast record decide where that is. The terms used below (pseudo-origin, block, handover and
others) are defined in [Terms used on this page](#terms-used-on-this-page).

- A 744-hour forecast splits exactly into a **level**, a **centred daily path** and a **within-day shape**. The blocks are
  orthogonal, so their squared errors add.
- The level comes from six historical candidates plus the foundation model's own level, and the daily path from seven
  historical candidate paths. Each unit's errors at earlier pseudo-origins weight them, and the **same errors decide
  how much of the month to hand over** to the foundation model.
- The within-day shape starts from **TimesFM 2.5** (zero-shot). Since **2.0** it is anchored too: the unit's own
  analog-day shape competes with the model's, with a weight set by the unit's errors at three completed pseudo-origins,
  shrunk towards the model and capped at one half; since **2.1** that weight is one value for the whole month (2.0–2.0.1:
  one per forecast week). All three blocks now take their weights from the unit's own pseudo-origin errors, but with
  different estimators and priors: inverse-error candidate weights shrunk towards equal weights for the level and
  daily path, least-squares handover weights shrunk towards one half, and a within-day trust shrunk towards zero and
  capped at one half. One whole-window weight per unit was not shown to be less accurate.
- A unit that has been **off for a week** is handed to the foundation model entirely. Since **2.0.1** so is a unit
  whose whole 1,344-hour context stays within 10⁻³ kW of zero: a record that stays inside the floor of the
  normalisation scale for eight weeks is treated as switched off.
- **No neural network is trained or fine-tuned on the target series.** The history-side estimates are fitted to the
  unit's own pre-origin record, and every weight to the unit's own completed pseudo-forecasts.
- Three **readout operators** reuse the same computation:
  - energy from the level, before the nonnegativity projection;
  - a monthly peak from a historical excursion envelope;
  - a prediction interval from pseudo-forecast residuals.
- The design choices and their limits are explained by **exact properties**: identities, bounds and the counterexamples
  that mark where they stop. They are kept in their own folder, [theory/](theory/), apart from the forecaster in
  [ankyra/](ankyra/): each has a proof, an operator and a numerical check.

## Contents

- **Use it:** [What is in this repository](#what-is-in-this-repository) · [Install and run](#install-and-run) ·
  [Forecast your own unit](#forecast-your-own-unit) ([inputs](#the-inputs) · [what comes out](#what-comes-out) ·
  [how long it takes](#how-long-it-takes) · [when not to use it](#when-not-to-use-it))
- **Read the results:** [Terms used on this page](#terms-used-on-this-page) ·
  [No information after the origin](#no-information-after-the-origin) ·
  [Information set](#inputs-and-features-one-information-set-for-every-forecaster) ·
  [Results on six test populations](#results-on-six-test-populations) ·
  [LCL households and two changes not adopted](#lcl-households-and-two-changes-not-adopted) ·
  [Three checks with the forecaster frozen](#three-checks-with-the-forecaster-frozen) ·
  [External test of the frozen 2.1 (UNICON)](#external-test-of-the-frozen-21-unicon)
- **How it works:** [Handover](#how-the-handover-works) · [Within-day anchoring](#within-day-anchoring-20) ·
  [What the parts buy](#what-the-parts-buy) · [Readouts](#readouts-peak-and-prediction-interval) ·
  [When anchoring is expected to help](#when-anchoring-is-expected-to-help) ·
  [Long-context models and generic combinations](#long-context-foundation-models-and-generic-combinations) ·
  [Theory](#theory-exact-properties)
- **Check it:** [Reproducibility](#reproducibility) · [What changed in 2.0, 2.0.1, 2.1 and 2.2](#what-changed-in-20-201-21-and-22) ·
  [Version history](#version-history) · [License and acknowledgements](#license-and-acknowledgements)

## What is in this repository

```
ankyra/              the forecaster
  core.py            forecast(): model level candidate, week-by-week handover, within-day anchoring, off-state and
                     micro-load rules
  analog.py          analog-day shapes and the error-weighted within-day trust (2.0; one value per window since 2.1)
  history/           frozen reference estimator of the historical level and daily path
  readouts.py        energy, peak envelope operator, pseudo-origin interval
  blocks.py          orthogonal block decomposition
  metrics.py         unit-equal log RMS ratio, unit-and-month bootstrap, mean per-unit rank, pooled decomposition
  synthetic.py       artificial building history and stand-in forecaster for the quickstart and the tests
  timesfm_adapter.py TimesFM 2.5 as configured in the study
examples/            quickstart on an artificial building
tests/               tests of the forecaster, including the no-future-information tests, and of the evaluation module
theory/              the exact properties P1–P20, apart from the forecaster
  README.md          index: condition, use, code and check of each property
  PROOFS.md          statements, proofs, counterexamples and measured consequences
  operators.py       the properties as operators (replacement, support, shrinkage, projection, peak)
  test_operators.py  numerical checks, counterexamples included
evaluation/          scoring of a population from forecasts and realised load; a runnable example
results/             scored statistics (CSV / JSON) and the reproduction record; 2.0.1, 2.0.0 and 1.x in subfolders
figures/             make_figures.py and the figures (PDF and PNG)
docs/                METHOD.md (equations and constants), EVALUATION.md (protocol and full tables),
                     DATA.md (sources and preparation), LCL_AND_CLOSEOUT.md (LCL households; two changes not adopted),
                     FROZEN_MODEL_CHECKS.md (checks with the forecaster frozen)
```

Deliberately not included:

- **Raw data and prepared data.** The evaluation populations are public. [docs/DATA.md](docs/DATA.md) lists each
  source and how the study prepared it.
- **Saved forecasts.** `results/` holds the scored statistics, not the forecasts they were computed from, so the
  tables cannot be regenerated from the repository alone.
- **Model weights.** TimesFM 2.5 is downloaded from Hugging Face on first use, or loaded from a local copy.
- **The code of the trained baselines.** Of the comparison models, only three simple reference forecasters are
  included (`evaluation/baselines.py`).

## Install and run

Requires Python ≥ 3.10, NumPy, SciPy and PyTorch. A CPU is enough for the quickstart and the tests.

```bash
git clone https://github.com/XinanQ/Building_load_ANKYRA.git
cd Building_load_ANKYRA
pip install -e .
python examples/quickstart.py
```

`pip install -e .` installs PyTorch if it is missing. For a CPU-only build, install that first:
`pip install torch --index-url https://download.pytorch.org/whl/cpu`.

The quickstart forecasts an artificial building, with a stand-in for the foundation model (the last week repeated).
It needs no data and no download and takes a few seconds. It prints the fields explained under
[What comes out](#what-comes-out). The artificial building is almost exactly periodic, so the stand-in is nearly
perfect: the weekly weights reach their upper limit 0.875 and the within-day trust is 0. The output shows the format,
not typical values.

To use TimesFM 2.5 (Apache-2.0) as the foundation model:

```bash
pip install -e ".[timesfm]"
python examples/quickstart.py --timesfm
```

- The first call downloads the checkpoint `google/timesfm-2.5-200m-pytorch` (about 0.9 GB; the revision is pinned in
  `ankyra/timesfm_adapter.py`) from Hugging Face into its cache.
- To run offline, pass a local directory that contains `model.safetensors`:
  `python examples/quickstart.py --timesfm --checkpoint DIR`, or `load_timesfm("DIR")` in code.
- A GPU is recommended ([How long it takes](#how-long-it-takes)).
- The extra installs the `timesfm` package (`timesfm>=2.0`). The adapter needs a version that provides
  `TimesFM_2p5_200M_torch` and `ForecastConfig`. CI does not install this extra, so this install route is not tested
  there.

**Software environment.** The repository records the following, and no more:

- `pyproject.toml` gives lower bounds only: Python ≥ 3.10, NumPy ≥ 1.26, SciPy ≥ 1.11, PyTorch ≥ 2.4; optionally
  `timesfm` ≥ 2.0 and, for the figures, Matplotlib ≥ 3.8.
- CI (`.github/workflows/tests.yml`) runs both test suites, the quickstart and the evaluation example on
  Python 3.10, 3.11, 3.12 and 3.13 (Ubuntu, CPU-only PyTorch), and regenerates the figures on Python 3.11.
- The checkpoints are pinned by revision: TimesFM 2.5 in `ankyra/timesfm_adapter.py`, Chronos-2 (a baseline) in
  [docs/DATA.md](docs/DATA.md).
- The exact package versions of the study's own runs are not recorded here. The hardware of the timing run is given
  under [How long it takes](#how-long-it-takes).

## Forecast your own unit

`ankyra.forecast` forecasts the 744 hours that follow the last value of `load_kw`. Put the unit on one regular hourly
grid first: the forecaster does no resampling, no filling of the context at the origin and no time-zone or
daylight-saving conversion ([details](docs/DATA.md#the-input-format-the-forecaster-expects)). An input that breaks the
contract below raises an error; nothing is repaired silently. The one documented exception is the gap tolerance of 2.2
(`gap_tolerance`, below): for the pseudo-origin bookkeeping only, short gaps before the origin are interpolated.

### The inputs

The record, `ankyra.History`:

| Input | What to supply |
|---|---|
| `load_kw` | Hourly mean load in kW (the off-state and micro-load thresholds are absolute values in kW). Index 0 is 1 January 00:00 of the year in which the record starts; the last value is the hour before the forecast starts. The last 1,344 hours (the context at the origin) must be complete: the package never fills them, a gap there raises an error, and you have to fill it yourself. Earlier gaps are NaN; since 2.2 gaps of at most 6 hours before the origin are interpolated for the pseudo-origin bookkeeping only (`gap_tolerance`). A record that starts later in the year is padded back to 1 January with NaN. Aggregate sub-hourly readings first (four 15-minute kWh readings sum to the hour's mean kW). |
| `temperature_c` | Hourly outdoor air temperature in °C for the same hours, finite everywhere, the padded hours included. The annual temperature harmonic is fitted on all of them, so use archive temperature for the padded hours if you can; a fixed value there also runs (the study's LCL preparation used 15 °C). Where load is observed the series must vary: if the daily mean temperature is constant over a year, the temperature signature cannot be fitted and `forecast` raises an error. A nearby weather station or a reanalysis series is enough. No future temperature is needed. |
| `day_types` | One integer per hour for the history plus the 744 forecast hours (length `len(load_kw) + 744`, integer dtype): Monday = 0 … Sunday = 6 from the date, 7 on a public holiday; constant within each day. |
| `start_timestamp` | The time of index 0. It must be 1 January 00:00 written with a `+00:00` offset (or `Z`), for example `"2019-01-01T00:00:00+00:00"`. The offset is a label and no conversion is made: use a fixed-offset grid (UTC or local standard time, without daylight-saving jumps). |
| `observed` (optional) | Boolean mask of the load. `False` marks an hour as unobserved: its value, finite or not, is ignored by every part of the forecast (since 2.0.2). Default: the finite values. |

Only hourly data are supported, and the forecast is always 744 hours long. The 1 January anchor fixes the phase of the
annual temperature harmonic; any other anchor is rejected.

A worked example for a record that starts in the middle of a year (checked end to end on artificial data, with the
stand-in model):

```python
from datetime import datetime, timedelta
import numpy as np
import ankyra
from ankyra.timesfm_adapter import load_timesfm, timesfm_forecaster

# first: datetime of your first hourly reading; load_meter, temp_meter: hourly arrays from that hour on;
# temp_before_first: hourly temperature from 1 January 00:00 up to `first`; holidays: a set of dates
anchor = datetime(first.year, 1, 1)
pad = int((first - anchor).total_seconds() // 3600)
load_kw = np.concatenate([np.full(pad, np.nan), load_meter])
temperature_c = np.concatenate([temp_before_first, temp_meter])      # finite, same length as load_kw
days = [(anchor + timedelta(hours=h)).date() for h in range(len(load_kw) + 744)]
day_types = np.array([7 if d in holidays else d.weekday() for d in days], dtype=np.int64)
history = ankyra.History(load_kw, temperature_c, day_types, f"{first.year}-01-01T00:00:00+00:00")

f = ankyra.forecast(history, group="Office", temp_sigma_std=0.25, dst_region="EU",
                    foundation=timesfm_forecaster(load_timesfm()))
print(f.trajectory_kw.shape, f.energy_kwh)        # (744,) hourly forecast in kW; the month's energy in kWh
```

**How much history.** The counts are of complete hours up to the origin; padded hours do not count.

- 1,344 complete hours: the forecast runs; every weight is at its default.
- 2,088 hours: the handover weights leave ½ (one completed pseudo-origin).
- 2,832 hours: the level weights leave equal weights (two completed pseudo-origins).
- 10,248 hours (about 14 months): the candidates that use the window one year earlier can be weighted.
- The study's windows had at least 10,248 hours before the origin (the exceptions are in
  [docs/DATA.md](docs/DATA.md#common-window-rules)), and the gain over TimesFM alone is resolved only from two years
  of history.

The other arguments of `ankyra.forecast`:

- `group`: `"Industrial"`, `"Office"`, `"Public"`, `"Residential"` or `"Commercial"` (exact spelling). It selects a
  fixed prior curve for the unit's response to temperature (its *temperature signature*); choose the closest
  category. The study's assignment for each population is in [docs/DATA.md](docs/DATA.md).
  **`"Commercial"` has no prior curve.** In the frozen configuration its curve is stored under the key `group_4`,
  which is not read, so a Commercial unit gets a zero temperature signature and its weather-adjusted candidates equal
  the unadjusted ones. This is the behaviour that was evaluated (13 BDG2 units and one Suzhou series were
  Commercial). It is kept as a known property.
- `temp_sigma_std`: how far the daily temperature strays from its seasonal normal, as a standard deviation in units
  of 10 °C (0.25 means 2.5 °C). The forecaster uses it to average the temperature response over the temperatures the
  forecast month may bring. It is one number per population, fitted once before the first origin and then kept
  fixed. The study's recipe:
  1. standardise the temperature as (T − 15 °C) / 10 °C and take daily means;
  2. subtract a centred 31-day moving mean;
  3. take the standard deviation of that anomaly, pooled over the units of the population, on a fit period that ends
     at or before the population's first scored origin (15 days are dropped at each end): the first 244 days of the
     record for BDG2, GoiEner non-household and the Suzhou park, and the complete days before the first scored
     origin for the other seven populations ([details](docs/DATA.md#the-input-format-the-forecaster-expects)).

  The values the study used for each population are not listed in the repository. The quickstart and the tests use
  0.25. On the quickstart's artificial building the level moves only from 23.014 to 23.019 kW when the value goes
  from 0.05 to 1.0; that is one artificial case, not evidence for real data. The input check verifies only that the
  value is finite and positive. That it was fitted on data from before the first origin is the caller's
  responsibility.
- `dst_region`: `"EU"` (clocks change on the last Sundays of March and October), `"US"` (second Sunday of March to
  first Sunday of November) or `"none"` (the default: no daylight saving, or any other rule). The load stays on its
  fixed-offset grid. The rule is used only so that analog days are taken from the same daylight-saving state.
- `foundation`: one of three forms.
  - A callable that maps an (N, 1344) array of contexts to (N, 744) point forecasts:
    `timesfm_forecaster(load_timesfm())`, or any other model.
  - A dict `{k: forecast}` of 744-hour forecasts issued at the origin (k = 0, required) and at the pseudo-origins
    744·k hours earlier (k = 1 … 6). This lets forecasts stored in earlier months be reused;
    `ankyra.pseudo_origin_contexts(load_kw)` returns the contexts in question.
  - `None`: a history-only configuration without a foundation model, to which the off-state and micro-load rules do
    not apply.
- `micro_load_rule` (default `True`): the micro-load rule of 2.0.1
  ([definition](docs/METHOD.md#off-state-and-micro-load-rules)). `gap_tolerance=False, single_trust=False,
  micro_load_rule=False` reproduces the 2.0.0 forecast.
- `within_anchor` (default `True`): the within-day anchoring of 2.0. `gap_tolerance=False, within_anchor=False,
  micro_load_rule=False` reproduces the 1.x forecast.
- `single_trust` (default `True`): one within-day trust value per window (2.1). `False` estimates one value per
  forecast week; `gap_tolerance=False, single_trust=False` reproduces the 2.0.1 forecast.
- `gap_tolerance` (default `True`): the gap tolerance of 2.2 ([definition](docs/METHOD.md#gap-tolerance-22)). For the
  pseudo-origin bookkeeping only, gaps of at most 6 hours inside one 744-hour block are interpolated and a pseudo-origin's
  target month counts when at least 90% of its hours are observed. The context at the origin is never filled: it must
  be complete, and a gap in it raises an error (`ankyra.fill_short_gaps` applies the same rule to your own record, but
  leaves a gap that touches the origin or a block boundary, or is longer than 6 hours, missing). `False` reproduces the 2.1 forecast; on a record
  without gaps the two are identical.

See [docs/METHOD.md](docs/METHOD.md) for the equations and all constants.

### What comes out

`ankyra.forecast` returns an `AnkyraForecast`. The quickstart prints these lines:

| Quickstart line | Field | Meaning |
|---|---|---|
| `foundation_model` | — | Which model filled the foundation-model slot. |
| `trajectory_first_day_kw` | `trajectory_kw[:24]` | `trajectory_kw` is the hourly forecast in kW, 744 values; element 0 is the hour after the last load value. It is nonnegative, except when one of the two rules in the last row returned the model's forecast unchanged. |
| `level_kw`, `energy_kwh` | same names | The level is the mean of the 744 forecast hours, and the month's energy is 744 × the level. Both are read before negative hours are set to zero. |
| `peak_kw` | computed by `readouts.peak_readout` | The monthly peak: the largest, over the 31 days, of the forecast daily mean plus the largest recent excursion of that day's type. |
| `interval_80pct_first_hour_kw` | computed by `readouts.interval_bands` | The 80% prediction interval of the first forecast hour: its lower and upper bound in kW. The interval adds quantiles of the unit's own pseudo-forecast residuals to the forecast. |
| `interval_pseudo_windows` | returned by `readouts.residual_quantiles` | The number of completed pseudo-origins whose residuals the interval uses (at most 12). |
| `lead_week_weights_on_model` | `lead_week_weights` | The handover: the weight on the foundation model's daily means in days 1–7, 8–14, 15–21 and 22–31. ½ means no evidence. |
| `level_weights` | same name | The weight of each level candidate. `s`, `l` and `a` are the recent 7-day mean, the long-history mean and the mean of the window one year earlier; `_u` is without and `_w` with weather adjustment; `fm` is the foundation model's own window mean. |
| `pseudo_origin_pairs` | `pseudo_pairs` | The number of completed pseudo-origins behind the handover weights (at most 6). |
| `within_day_trust_on_analog_shape` | `within_trust` | The weight on the unit's own analog-day shape, between 0 and ½, given for the same four parts of the month. Since 2.1 it is one value repeated four times (with `single_trust=False`, one value per part, as in 2.0.1). 0 leaves the foundation model's shape. |
| `within_day_pseudo_origin_triples` | `within_pseudo_pairs` | The number of completed pseudo-origins behind the trust (at most 3). |
| `analog_shape_kept` | `analog_kept` | `False` when the analog shape was implausibly large (more than three times the largest context value) and the model's shape was used for the whole window. |
| `off_state`, `micro_load` | same names | `True` when the off-state or the micro-load rule fired. The foundation model's forecast is then returned unchanged, without setting negative hours to zero. |
| `anchoring_record` | same name | Two statistics of the unit's own pseudo-forecast record on the level, read before the forecast and not used by it (2.2): `carrier_level_weight` (the weight of the foundation model's window mean in the level, `level_weights['fm']`) and `history_vs_carrier_log_ratio` (log of the best historical candidate's pseudo-origin RMS error over the foundation model's; negative = the unit's history beat the model at its earlier origins), with `pseudo_origins`. Across the fourteen populations the realised gain over the foundation model fell with both ([table](results/anchoring_gain_deciles.csv); [section](#when-anchoring-is-expected-to-help)). Empty on off-state and micro-load windows. |

Further fields: `daily_means_kw` (the 31 daily means after the handover), `within_day_kw` (the delivered within-day
block), `foundation_within_day_kw` and `analog_shape_kw` (the two shapes it is mixed from) and
`fixed_division_daily_means_kw` (the daily means without handover, kept for ablation).

The peak and the prediction interval are separate calls in `ankyra.readouts`;
[`examples/quickstart.py`](examples/quickstart.py) shows both. `readouts.interval_bands` returns five quantile
trajectories (5, 10, 50, 90 and 95%); the second and the fourth bound the 80% interval.

### How long it takes

Timed per 744-hour window on one laptop: RTX 5060 Laptop GPU and Ryzen 9 8940HX, with one CPU thread for the history
side.

| Forecaster | First run | Pseudo-origins reused |
|---|---:|---:|
| TimesFM alone, per-core batch 64 | 18 ms | — |
| TimesFM alone, study configuration (per-core batch 1) | 0.72 s | — |
| ANKYRA 2.0, per-core batch 64 | 0.56 s | 0.13 s |
| ANKYRA 2.0, study configuration | 5.5 s | 0.83 s |
| Chronos-2-X | 80 ms | — |
| Per-unit ridge (CPU) | 108 ms | — |

- **Which rows you get.** `load_timesfm()` compiles the study configuration (per-core batch 1; 0.9 GiB of GPU
  memory). Expect a few seconds per window, most of it in the seven TimesFM calls (one at the origin and six at
  pseudo-origins, 0.72 s each). `load_timesfm(per_core_batch_size=64)` (3.0 GiB) gives the batch-64 rows and the same
  forecasts to within 3×10⁻⁵ kW. There most of the time goes to the historical estimator at six pseudo-origins
  (0.32 s), not to the foundation model (seven contexts, 0.13 s).
- **Reuse.** The column "Pseudo-origins reused" assumes that the results at the six pseudo-origins are kept from
  earlier runs, which is possible when forecasts are issued every 744 hours. The released `forecast()` reuses stored
  TimesFM forecasts when they are passed as a dict (see `foundation` above). It recomputes the historical
  pseudo-forecasts (0.32 s) on every call.
- **Version.** The timings were measured on 2.0.0. The micro-load rule of 2.0.1 adds one maximum over the 1,344-hour
  context. The within-day anchoring adds the analog shapes at four origins and no model call; 1.x measured 0.50 s and
  0.11 s on the same machine, within the benchmark's run-to-run spread. 2.1 sums the same products over the whole month
  before dividing; it adds no model call and was not timed separately.
- **Once per session.** Loading TimesFM takes 2.3 s. The interval readout, when requested, adds 0.56 s per window.

Full timings are in [`results/cost_per_window.csv`](results/cost_per_window.csv) and
[docs/EVALUATION.md](docs/EVALUATION.md#cost).

### When not to use it

Use ANKYRA for hourly, month-ahead forecasts of buildings and non-household supply points with two or more years of
history, above all when the monthly energy or the later weeks of the month matter. On the evidence of this page it is
not the better choice in these cases:

- **Households.** On GoiEner households zero-shot TimesFM has the lower hourly error (3.9%, resolved); on LCL
  households the two are not separated. ANKYRA's monthly energy error is still lower. The weakness does not come from
  TimesFM: with Chronos-2 as the foundation model it is the same
  ([check](#three-checks-with-the-forecaster-frozen)).
- **The first days of the month.** On day 1 the zero-shot foundation models are lower on every population.
- **Less than two years of history.** ANKYRA is not separated from TimesFM alone on the ten populations. On the
  HKUST blind test, where most windows have less than two years, the hourly gain is borderline and the energy gain
  is resolved.
- **Coarsely quantised meters.** Where the meter's step is a quarter of the mean load or more (HKUST, 11 units),
  ANKYRA's hourly error does not differ from TimesFM's.
- **Against a covariate-informed foundation model on a new population.** On the Helsinki confirmation test
  ANKYRA's hourly and monthly energy errors are 5.6% and 13.6% higher than those of Chronos-2-X with temperature
  and calendar covariates, both resolved, mainly because Chronos-2-X forecast the monthly level better. The
  temperature-sensitivity measures tested did not support that explanation; the cause is not known. On the UNICON
  external test the order is reversed (ANKYRA 5.8% lower hourly, resolved; 11.7% lower monthly energy, not resolved).
  Do not assume ANKYRA's energy advantage against such a model. The anchoring takes any foundation model, so it can be
  put on that model instead: anchored to Chronos-2-X, it improves Chronos-2-X resolvably on 8 of 12 populations
  (hourly and energy alike), but on Helsinki it is not separated from it (post hoc;
  [carrier swaps](#three-checks-with-the-forecaster-frozen)).
- **Buildings ruled by closure days.** On Norwegian schools a trained cross-unit model with calendar features is
  12.3% better.
- **A context with a single large spike.** The hourly error rises and the peak readout, which takes the largest
  recent excursion, is ruined.
- **Units that switch off.** The prediction interval should not be used for them; its width explodes.
- **Data that are not hourly, or not in kW.** The off-state and micro-load thresholds are absolute values in kW.
- **Sites in the southern hemisphere.** The annual temperature harmonic has a fixed phase, with its coldest day in
  January, and a nonnegative amplitude. UNICON (Victoria, Australia) is the only evaluated population in the southern
  hemisphere; it was run with the package unchanged. A descriptive analysis with the phase corrected in a
  development copy changed UNICON's errors by about −0.01% hourly and −0.2% for monthly energy, so the phase does not
  explain the failed test there ([details](#long-context-foundation-models-and-generic-combinations)). The frozen
  package keeps the original behaviour (northern-hemisphere phase).

The evidence for the first eight points is in the results sections below. The last two follow from the code.

## Terms used on this page

- **Unit**: one metered series: a building, a meter, a supply point or a household.
- **Origin**: the hour at which a forecast is issued. The forecast covers the 744 hours (31 days) that follow.
- **Context**: the 1,344 hours (eight weeks) of load before an origin; the foundation model's only input.
- **Window**: one origin of one unit, with its context and its 744-hour target.
- **Pseudo-origin**: an earlier origin inside the unit's own record, 744, 1,488, … hours before the origin, whose
  744-hour target has already been observed. ANKYRA forecasts from it as if it were the origin (a *pseudo-forecast*)
  and uses the error to set its weights.
- **Blocks**: the three parts of a 744-hour forecast. The *level* is the mean of the 744 hours; the *centred daily
  path* is the 31 daily means minus the level; the *within-day shape* is each hour minus its day's mean.
- **Handover**: the share of the daily means taken from the foundation model instead of the history side, one weight
  for each forecast week (days 1–7, 8–14, 15–21, 22–31). To *hand a window to the foundation model* is to return its
  forecast unchanged.
- **Fixed division (F0)**: the history side's level and daily path with the model's within-day shape, without
  handover.
- **Trust**: the weight on the unit's own analog-day shape in the within-day block, between 0 and ½; one value per
  window since 2.1 (one per forecast week in 2.0–2.0.1).
- **Training cutoff, late windows**: the trained baselines are fitted on targets that end before a cutoff date, one
  per population. The *late* (post-cutoff) windows are those after it, the only ones on which all 21 forecasters
  exist.
- **Same-information baseline**: one of the five baselines given ANKYRA's inputs (TiDE, iTransformer-X, GBT-T,
  Chronos-2-X, TimesFM-X).
- **Resolved**: the 95% interval of a contrast excludes zero.
- **Tier**: the role of a population in the evaluation: *test* (scored once, after the forecaster had been fixed),
  *preview* (used for diagnosis during development) or *reserved* (held out).
- **Seen / first read**: a population is *seen* if its results were known when some component of ANKYRA was
  specified. It is a *first read* if it was scored for the first time after the handover had been fixed. A
  *re-evaluation* scores windows that had been scored before.
- **Frozen protocol**: the rule, the windows and the pass criteria were written down before the scoring.
- **Design sets**: the data on which a rule was selected: the three development populations and the pre-cutoff
  windows of the six test populations.

**Populations.** The main comparison has ten populations, called *the ten populations* on this page:

- six *test* populations: BDG2 2017, Cambridge, HEEW, EWELD, GoiEner non-household and GoiEner households;
- four *preview* populations: Oslo schools, Drammen municipal buildings, CINELDI industrial customers and four
  category aggregates of a Suzhou industrial park.

An eleventh, the Low Carbon London households (LCL), was held out of this comparison and scored last, separately
([below](#lcl-households-and-two-changes-not-adopted)). Two more were scored with the forecaster frozen, the HKUST
campus and Helsinki's city service buildings ([below](#three-checks-with-the-forecaster-frozen)); *the twelve
populations* are the ten plus these two. UNICON, the campuses of La Trobe University, is the external test of the
frozen 2.1 ([below](#external-test-of-the-frozen-21-unicon)). The three *development populations* on which rules were
selected are a Spanish non-household development store (disjoint from the GoiEner test units), Oslo and Drammen.
Units, windows, sources and the status of each population are in
[docs/EVALUATION.md](docs/EVALUATION.md#populations-and-tiers).

## No information after the origin

At an origin, ANKYRA uses only what is known at that moment.

- **Inputs.** It receives:
  - load and temperature up to the origin;
  - the calendar of the forecast month (weekday or public-holiday type);
  - the unit's category.

  The interface has no argument for future load or weather.
- **Weather.** Future temperature enters only as an expectation formed before the origin: an annual harmonic of past
  temperatures plus a fixed anomaly scale. Observed future weather is never used.
- **Weights.** Every weight is estimated at pseudo-origins inside the record, whose targets end by the origin. Each
  level pseudo-forecast uses only data before its own pseudo-origin.
- **Foundation model.** TimesFM receives only the 1,344 hours before each origin or pseudo-origin.
- **Checked by tests.** [`tests/test_no_future_information.py`](tests/test_no_future_information.py) changes every value
  after the origin, or after each pseudo-origin. It checks that the forecast, the model's inputs, the pseudo-origin
  errors and the interval stay bit-identical.
- **Evaluation.**
  - The baselines receive the same information set, with leakage assertions on feature and lag time indices,
    normalisation statistics and training-target ends.
  - Trained baselines are scored only after their training cutoff.
  - The six test populations were scored once for 1.x, after the model was fixed, and nothing was tuned on them. The
    2.0 within-day rule was then developed on the pre-cutoff windows of the same populations and re-evaluated on the
    post-cutoff windows under a frozen protocol ([details](docs/EVALUATION.md#within-day-anchoring-20)).
  - The micro-load rule of 2.0.1 is the exception. It was written after the BDG2 post-cutoff result of 2.0.0 had been
    seen, so BDG2 under 2.0.1 is not a test set scored once with the model fixed. The other five test populations are
    unchanged by the rule. The rule itself reads only load before the origin.
  - The 2.1 change (one within-day trust value per window instead of four) was chosen after all twelve populations had
    been scored with 2.0.1. Every 2.1 number on this page re-evaluates windows that had been read before and is not a
    test, with one exception: the UNICON external test scored the frozen 2.1 once, on data not read before.

**What the tests show, and what they do not.** The tests establish input isolation in the implementation: nothing
recorded after the origin reaches the computation. They do not by themselves show that the inputs are free of later
information. Three sources lie outside the implementation:

- the providers' data preparation, such as gap filling (imputed or zero-filled hours are masked where documented);
- weather archives, whose past values may have been quality-controlled later;
- the pretraining corpora of TimesFM 2.5 and Chronos-2, which may contain some evaluation series (seven BDG2 sites are
  listed in them). This could favour every forecaster built on these models, ANKYRA included
  ([limitations](docs/EVALUATION.md#limitations)).

The information set is detailed in [docs/METHOD.md](docs/METHOD.md#information-at-the-origin).

## Inputs and features: one information set for every forecaster

A comparison is only meaningful when the forecasters are given the same information. The shared information set was
fixed in writing before the baselines were run. ANKYRA receives it as the raw record (load, temperature, day types,
category) and forms its own quantities from it; the same-information baselines receive it as engineered features.
**Nothing in the set is observed after the origin.**

**Hourly features** (past = the 1,344-hour context, future = the 744-hour horizon):

| # | Feature | Past | Future | Construction | What ANKYRA makes of it |
|---|---|:---:|:---:|---|---|
| 1 | load | observed | — | per-unit z-score; statistics from the context or from before the training cutoff | level and daily-path candidates, analog-day shapes, pseudo-origin errors, the foundation model's context |
| 2 | temperature | observed | climatology | horizon values are an annual harmonic fitted on pre-origin temperature; **observed future temperature is never used** | weather-adjusted level and path candidates, analog-day selection |
| 3 | load one year earlier | ✓ | ✓ | $t-8{,}736$ h (52 weeks, weekday-aligned; always before the origin), 0 where missing | the annual level and path candidates |
| 4 | availability of 3 | ✓ | ✓ | 1 where feature 3 is observed | annual candidates switched off without support |
| 5–6 | hour of day | sin, cos | sin, cos | period 24 | the hour grid of every block |
| 7–8 | weekday | sin, cos | sin, cos | period 7 | day types Monday … Sunday |
| 9–10 | day of year | sin, cos | sin, cos | period 365.25 | climatology phase, analog-day window (±14 days) |
| 11 | holiday / non-working day | ✓ | ✓ | public holiday or Saturday/Sunday | day type 7 in every day-typed quantity |

That is 11 past and 10 future dimensions (features 2–11). **Static features** (6 dimensions): the unit's category
(Industrial, Office, Public, Residential, Commercial; one-hot) and the log ratio of its long-history mean to its
context mean. ANKYRA 2.0 has one further input, the daylight-saving rule of the region (EU, US or none), a calendar
fact used only to keep analog days in the same daylight-saving state.

**How each forecaster receives the set**

| Forecaster | Receives | Not accepted by the architecture |
|---|---|---|
| ANKYRA | the raw record behind all 11 + 10 + 6 features, plus the foundation model's forecasts at the origin and pseudo-origins | — |
| TiDE | 11 past, 10 future, 6 static | — |
| iTransformer-X | 11 past as variable channels, 6 static as constant channels | future covariates |
| GBT-T | 21 features per forecast hour derived from the set (load aggregates, features 3–4, temperature, calendar, lead time, static) | raw sequences |
| Chronos-2-X | features 2–11 as past and known-future covariates | static features |
| TimesFM-X | features 2–11 through its linear covariate regression, the category as a categorical covariate | nonlinear covariate effects |
| PatchTST | the same channels, but it is channel-independent: its load forecast equals the load-only one | information between channels |
| load-only models (TimesFM, Chronos-2, DLinear, iTransformer, LSTM, Holt–Winters, MSTL, naive and profile forecasters) | feature 1 only | — |
| per-unit ridge | calendar and climatological temperature, refitted at every origin | — |

**Deliberately excluded everywhere:** observed future weather; humidity and other meteorological variables
(available for one population only); hand-made signal transforms (smoothing, wavelet, Fourier or EMD decompositions),
which add no information and are a common source of look-ahead. Every feature's time index is checked by assertions
(lags, normalisation statistics and training-target ends before the origin or the cutoff). The full specification is
in [docs/METHOD.md](docs/METHOD.md#inputs-and-features-the-shared-information-set).

## Results on six test populations

"The study" on this page is the evaluation of ANKYRA documented in
[docs/EVALUATION.md](docs/EVALUATION.md).

Five of the 20 baselines were given **ANKYRA's information set**: past load and temperature, climatological future
temperature, the load one year earlier, calendar features and unit category. They are per-population trained TiDE,
iTransformer-X and a gradient-boosting model (GBT-T), and covariate-conditioned Chronos-2 and TimesFM.

Each uses the part its architecture accepts:

- iTransformer-X takes no future covariates;
- Chronos-2-X takes no static features;
- TimesFM-X uses the covariates through a linear regression;
- GBT-T receives 21 features derived from the set. Its first implementation mis-scaled flat or all-zero contexts; the
  corrected version is reported ([details](docs/EVALUATION.md#correction-of-the-gbt-t-baseline)).

PatchTST is channel-independent, so its forecast is the same with or without these inputs. The six test populations
were scored **once, after the model had been fixed**, for 1.x; the numbers below are those of 2.2, a re-evaluation: 2.1 was chosen after every population had been scored
with 2.0.1, 2.2 adds the gap tolerance, and the counts in the table equal those of 2.0.1 and 2.1 ([`results/ankyra_2_0_1/`](results/ankyra_2_0_1/),
[`results/ankyra_2_1/`](results/ankyra_2_1/)). The
BDG2 row (†) also includes the micro-load rule, which was written after that population's 2.0.0 result had been seen.

**Primary estimand.** For each unit, take the RMS of the hourly errors over its windows. The unit-equal log RMS ratio
is r = the mean over units of log(RMS of ANKYRA / RMS of the baseline).

- Tables report it as the improvement 100·[1 − exp(r)], so a positive percentage favours ANKYRA.
- Where an interval is quoted "in log units" it is the interval of r itself, and there a negative value favours
  ANKYRA.
- The 95% intervals come from 2,000 bootstrap replicates that resample units and months. A contrast is *resolved*
  when its interval excludes zero.
- The mean per-unit rank is a secondary summary: it stays defined when some units have zero error, but it does not
  replace the ratio.

| Test population | Country | Units / windows | Resolved better than (of 20) | …of them, same-information (of 5) | Resolved worse than | Rank among 21 |
|---|---|---:|:---:|:---:|:---:|:---:|
| BDG2 2017 (commercial and institutional meters) † | USA / Europe | 142 / 474 | 15 | 4 | — | 1 |
| University of Cambridge estate | UK | 108 / 730 | 17 | 2 | — | 1 |
| HEEW, Arizona State University campus | USA | 138 / 658 | 17 | 4 | — | 1 |
| EWELD industrial and commercial meters | China | 197 / 523 | 18 | 5 | — | 1 |
| GoiEner non-household supply points | Spain | 481 / 890 | 17 | 4 | — | 1 |
| GoiEner households | Spain | 696 / 696 | 16 | 3 | TimesFM (3.5%) | 2 |

Windows are those after each population's training cutoff, where all 21 forecasters are available. (ANKYRA 1.x: 10,
16, 16, 18, 15, 16 resolved wins; ranks 1, 2, 1, 1, 1, 2.)

† The BDG2 row includes the micro-load rule, written after the BDG2 result of 2.0.0 had been seen. It describes what
the rule changes and is not a test of it. ANKYRA 2.0.0 was resolved better than 10 of 20 (2 of the 5
same-information baselines), resolved worse than none, and ranked first. Without the three near-zero meters 2.0.1 is
resolved better than 14 and 2.0.0 than 11. Three of the 14 are resolved only under the rule, so the reading that does
not involve the rule is 11 of 20. The BDG2 item under *Where ANKYRA falls behind* gives the comparison.

- On the test populations **ANKYRA is never resolvably worse than any baseline given its information set**.
- Among those five baselines, it is resolvably better than:
  - TiDE on all six populations;
  - GBT-T on five;
  - iTransformer-X and TimesFM-X on five (four under 2.0.0; the fifth is BDG2 with the micro-load rule);
  - Chronos-2-X on one (EWELD).
- Among the load-only statistical models, it is resolvably better than Holt–Winters on all six and MSTL on five.
- Its only resolved deficit on a test population is against zero-shot **TimesFM on households** (3.5%), where the
  within-day anchoring does not act.
- Mean per-unit rank over the six populations: **5.39** (2.1: 5.45; 2.0.1: 5.49; 2.0.0: 5.51; 1.x: 6.00). Next are the per-unit ridge (7.31),
  Chronos-2-X (7.84) and iTransformer-X (8.17).

![Test-set ranks and head-to-head](figures/fig2_test_ranks.png)

*Figure 2. Test-set ranks and head-to-head comparison.*

![Pairwise improvements with intervals](figures/fig3_test_pairwise.png)

*Figure 3. Pairwise improvements with intervals.*

**Loss metrics against every baseline.** The figure below gives the conventional losses of all 21 forecasters on the
same late windows, for the six test populations and the Suzhou industrial park (a preview population with four
aggregate series). The ordering depends on the metric:

- **RMSE** (mean over units): ANKYRA is lowest on BDG2, the Suzhou park and households (there by less than 0.5%:
  0.1721 kW against the per-unit ridge's 0.1728 kW) and second on the other four. The lower ones are iTransformer-X
  (Cambridge), GBT-T (HEEW), Chronos-2 (EWELD) and Chronos-2-X (GoiEner non-household).
- **MAE and WAPE** are minimised by the median of the predictive distribution, squared-error metrics by its mean. On
  them, zero-shot Chronos-2 or TimesFM variants are lower than ANKYRA on EWELD and on both GoiEner populations, where
  ANKYRA ranks second to fifth.
- **CV(RMSE) at the median unit**: ANKYRA is lowest on the Suzhou park and HEEW and second on the other five.
- Across the four metrics and seven populations ANKYRA ranks between first and fifth of 21, and no baseline is lower on
  all of them. These metrics weight units differently from the primary estimand
  ([details](docs/EVALUATION.md#loss-metrics-of-every-forecaster)).

![Loss metrics of all 21 forecasters](figures/fig8_loss_metrics.png)

*Figure 8. Loss metrics of all 21 forecasters.*

**Loss by forecast day.** Figure 9 below shows the error of the hourly load forecast. It splits the same late-window
forecasts of all 21 forecasters by forecast day, 1 to 31. The loss is each day's CV(RMSE) over its 24 hours, averaged
geometrically over a fixed set of units, the scale of the primary estimand. The split was made after scoring; it is a
description. Its eleven panels are the seven late-window populations (the six test populations and the Suzhou park)
and four populations scored separately, with the same definitions: LCL households (21 forecasters on its 710 late
windows) and HKUST, Helsinki and UNICON (14 forecasters, no trained baselines, on the windows where the per-unit
ridge is defined). All panels show ANKYRA 2.2.

- On every forecast day of each of the seven late-window populations ANKYRA is among the six forecasters with the
  lowest loss of 21. It is the lowest on 8 of the 31 days on BDG2, 16 on Cambridge, 13 on HEEW and 13 on the Suzhou park, but
  only on 2 on EWELD and on none on the two GoiEner populations.
- **The zero-shot foundation models are lower in the first days.** On day 1 TimesFM and Chronos-2 are below ANKYRA on
  every population, and ANKYRA ranks third to fifth of 21. On BDG2, HEEW and the Suzhou park at least two of the four
  zero-shot variants stay below it through day 3.
- From the second week ANKYRA is lowest or second-lowest on 17–21 of the 24 days on BDG2, Cambridge, HEEW and the
  Suzhou park, and on 8 on EWELD. From the first week (days 1–7) to the fourth (days 22–31) its loss grows by
  ×1.19–1.55, less than TimesFM's (×1.24–1.68) and Chronos-2's (×1.25–1.80) on all seven populations.
- On GoiEner households all four zero-shot variants are lower on every day. On GoiEner non-household ANKYRA is below
  TimesFM on 19 days, but Chronos-2-X is lower on every day and Chronos-2 on 29. On EWELD at least one variant is
  lower on 29 days.
- The hourly error is dominated by the within-day shape, which is still mostly the foundation model's. The micro-load
  rule moves the BDG2 curve by at most 0.012 points on any day. The curves use a fixed set of units whose daily errors
  are nonzero for all 21 forecasters (132 of 142 on BDG2), and the three meters that are near zero in every window are
  not in it. The day-by-day comparison, the same curves relative to ANKYRA ([Figure 10](figures/fig10_loss_by_day_relative.png)) and the exact relation to the
  monthly estimand are in [docs/EVALUATION.md](docs/EVALUATION.md#loss-by-forecast-day).
- **The four further panels.** ANKYRA has the lowest hourly loss of the 14 on 15 of the 31 days on HKUST and on 18 on
  UNICON, but on only two on Helsinki, where Chronos-2-X is lower on 28 days. On LCL it ranks first to fifth of 21
  on every day (lowest on 3); the forecasters below it are always zero-shot foundation-model variants (Chronos-2-X on
  25 days, Chronos-2 on 24, TimesFM on 15), as on GoiEner households.

![Loss by forecast day](figures/fig9_loss_by_day.png)

*Figure 9. Hourly loss by forecast day: eleven panels (six test populations, the Suzhou park, LCL, HKUST, Helsinki,
UNICON).*

**Energy as the month accumulates.** Figure 9b below shows the error of the energy, for the same forecasts. It follows
the error of the energy delivered through each forecast day (the mean load over days 1 to *d*), averaged geometrically
over a fixed set of units. This is the quantity ANKYRA's level and daily path act on, and day 31 is the monthly energy
error. Like Figure 9, it was computed after scoring, as a description.

- **ANKYRA has the lowest error of the 21 forecasters** on 29 of the 31 days on GoiEner non-household, 25 on BDG2,
  19 on HEEW and 18 on Cambridge and EWELD. At day 31 it is first on four of the six test populations (GoiEner
  non-household 11.6% against 13.1% for the next forecaster; BDG2, HEEW, EWELD) and second on Cambridge.
- **From the second week it is below all four zero-shot foundation-model variants** on every day on BDG2, Cambridge
  and both GoiEner populations, and on 19 of the 24 days on HEEW and 16 on EWELD.
- **The error still grows on the building populations.** The foundation models' energy error grows as their level
  drifts: from the first week (days 1–7) to the fourth (days 22–31) TimesFM's and Chronos-2's grow by 51–72% on BDG2,
  Cambridge and HEEW and by 18–38% on EWELD and the two GoiEner populations. ANKYRA's grows too, by 31–37% on BDG2,
  Cambridge and HEEW and by 16% on EWELD. It stays flat only on the two GoiEner populations (+5% and −1%).
- On GoiEner households ANKYRA's energy error (11.5% at day 31) is a quarter to a third below the four
  foundation-model variants' (15.5–17.4%), but the per-unit ridge, three profile or naive forecasters and the LSTM are
  lower still (10.0–11.4%), so it ranks sixth there. On the Suzhou park (four series) covariate-conditioned TimesFM is
  lower from day 2 on.
- **The two figures answer different questions and do not conflict.** Figure 9 is the error of the hourly load, where
  the foundation models lead in the first days, and on most days on EWELD and the Spanish populations. Figure 9b is
  the error of the accumulated energy, where the historical anchor acts: from the second week ANKYRA is below the
  zero-shot variants on most days on all six test populations
  ([details](docs/EVALUATION.md#energy-as-the-month-accumulates)).
- **The four further panels.** ANKYRA has the lowest energy error to date of the 14 on 24 of the 31 days on HKUST
  but on 4 on UNICON (Chronos-2 is lower on 22 days) and on 4 on Helsinki (below TimesFM on 25 days, below Chronos-2-X
  on 6). On LCL it is below all four zero-shot variants on every day from the second week but ranks fifth to eleventh
  of 21: as on GoiEner
  households, trained, ridge and profile forecasters are lower.

![Energy error as the month accumulates](figures/fig9b_energy_by_day.png)

*Figure 9b. Energy error as the month accumulates: the eleven panels of Figure 9.*

**Where ANKYRA is strongest: monthly energy.** A month's energy error is 744 times the level error ([P3](theory/README.md)). ANKYRA's
design acts on that quantity: its level and daily path come from the unit's own history, while its within-day shape
starts from TimesFM's.

- On all seven populations ANKYRA is never resolvably worse than any of the 20 baselines on monthly energy error. It is
  resolvably better than 6–17 of them: 17 on GoiEner non-household, 14 on Cambridge, EWELD, BDG2 and households.
  The BDG2 count includes the micro-load rule: it was 4 under 2.0.0, and without the three near-zero meters it is 8
  (6 under 2.1, 5 under 2.0.0).
- On GoiEner households, where the zero-shot foundation models have the lower hourly error on every day, ANKYRA's
  monthly energy error is 23–28% lower than all four of them, each resolved.
- Against TimesFM, whose within-day shape it uses, the energy error is 4–26% lower on all seven populations, resolved
  on Cambridge and both GoiEner sets. On BDG2 it is 13% lower, not resolved, with or without the three near-zero
  meters; under 2.0.0 those meters made it 38.7% higher.
- The energy comparison was computed after scoring, as a description
  ([details](docs/EVALUATION.md#monthly-energy-error)).

![Monthly energy error against every baseline](figures/fig11_energy_error.png)

*Figure 11. Monthly energy error against every baseline.*

**Consistency across populations.** ANKYRA 2.2 is first of the 21 forecasters on five of the six test populations
and second on households. No other forecaster is in the top two on more than two of them. On the four preview
populations it is 1st (CINELDI), 1st (Suzhou park), 2nd (Drammen) and 3rd (Oslo); 1.x was 3rd, 1st, 7th and 5th.
Positions use the mean per-unit rank, the secondary summary.

![Position on every population](figures/fig12_consistency.png)

*Figure 12. Position on every population.*

**Rank tests.** The standard tests of the forecasting literature agree. On per-unit RMSE over the 1,762 units of the
six test populations, Friedman's test rejects equal ranks; ANKYRA's mean rank (5.86) is separated from every other
forecaster's by more than the Nemenyi critical difference (0.75; the next is the per-unit ridge at 7.08), and
Holm-corrected Wilcoxon tests put it ahead of all 20. Per population it is significantly better than 17–20 of the 20
baselines on the test populations. Three baselines are significantly better somewhere: the per-unit ridge on
households, GBT-T on Oslo and Chronos-2-X on Drammen ([details](docs/EVALUATION.md#rank-significance-tests)).

![Rank tests](figures/fig15_rank_tests.png)

*Figure 15. Rank tests.*

**Where the error sits.** Because the three blocks are orthogonal, each forecast's hourly MSE splits exactly into its
level, daily-path and within-day parts. On the late windows the within-day block carries 33–47% of the median unit's
error on the building populations (39% on EWELD) and 80–85% on the Spanish populations; ANKYRA's gain over TimesFM comes from the
level on every population, from the daily path on the buildings, and in 2.0 also from the within-day block
(`results/block_shares.csv`, Figure 14). On BDG2 the block contrasts with TimesFM include the micro-load rule (level
+13.2%, daily path +0.6%, within-day +1.6%); under 2.0.0 the near-zero meters made them −38.7%, −52.4% and +9.1%, so
for BDG2 the statement holds only with the rule.

![Block attribution](figures/fig14_block_attribution.png)

*Figure 14. Block attribution.*

**Where ANKYRA falls behind.** We report these as findings, not footnotes.

- **Norwegian schools** (Oslo; a preview population). GBT-T, a cross-unit trained model with calendar features, is
  still better, by 12.3% (1.x: 18%); iTransformer-X's lead (3.9%) is no longer resolved. On Drammen no model is
  resolvably better than 2.0.
  - Diagnostics point to the **activity level of individual days** (holidays, closure-like days, bridge days) rather
    than to the shape of the day.
  - Closure-like days are shared across units and recur from year to year.
  - The diagnosis rests on an oracle bound and on correlations. It narrows down the cause but does not identify the
    operating reasons.
- **Households.** Zero-shot TimesFM is better (see above). The within-day anchoring finds no reliable analog-day
  signal there (mean trust 0.08; 2.1: 0.07) and leaves the forecast as in 1.x.
  By per-unit rank the per-unit ridge is ahead of ANKYRA there, significantly so in a paired test; by block, the
  deficit to TimesFM sits in the daily path (−9%), not in the within-day shape.
- **Short histories.** With less than two years of history ANKYRA is not separated from the foundation model alone
  (−0.8% and +2.3% in the two shortest strata, pooled over ten populations, neither resolved; the second was −1.4%
  under 2.0.0, before the BDG2 micro-load windows were handed to the model); with two or more years it is 6–8% better,
  resolved ([details](docs/EVALUATION.md#history-length)).
- **A single large spike in the context.** A stress test on corrupted contexts shows ANKYRA at least as robust as the
  foundation model to gaps, zero-filled blocks and clock shifts, and exactly scale-equivariant under the tested
  rescalings (×0.5 and ×2 on Drammen windows). The off-state and micro-load thresholds are absolute values in kW, so
  the equivariance holds only as long as a rescaling does not move a record across a threshold; loads must be
  supplied in kW. One spike at ten times the context maximum raises the hourly error by 17% (TimesFM: 3%) and ruins
  the peak readout, which takes the largest recent excursion. A spike guard that removes the effect is described in
  the evaluation but is not part of the released forecaster
  ([details](docs/EVALUATION.md#robustness-to-corrupted-contexts)).
- **BDG2 and the near-zero meters.** Nine meters at one BDG2 site read 0.0002–0.0005 kW for months at a time, and
  three of them do so in every window. That is above the off-state threshold, so 2.0.0 kept its historical candidates
  in play and forecast the load of earlier months (0.35 kW on average where the meter stayed near zero). The primary
  estimand is a ratio, so the three meters dominated the unit means. They turned the point estimates against ANKYRA in
  the comparisons with TimesFM, Chronos-2, Chronos-2-X, MSTL and the previous-month profile (none resolved). 2.0.1
  hands such contexts to TimesFM by the micro-load rule (46 windows of the nine meters, 33 of them after the training
  cutoff). Improvement of ANKYRA over each model on the late windows (474 windows, 142 units; columns "without": 464
  windows, 139 units; positive = ANKYRA better; * = the 95% interval excludes zero; the 2.0.0 and 2.0.1 columns are
  in [`results/ankyra_2_0_1/`](results/ankyra_2_0_1/), the 2.1 columns in [`results/ankyra_2_1/`](results/ankyra_2_1/)):

  | Against | 2.0.0 | 2.0.1 | 2.0.1 without the three near-zero meters | 2.2 | 2.2 without the three near-zero meters |
  |---|---:|---:|---:|---:|---:|
  | TimesFM | −53.4% | +2.5% | +2.5% | +2.7% | +2.8% |
  | Chronos-2 | −54.9% | +1.5% | +6.8% | +1.8% | +7.1% |
  | Chronos-2-X | −38.3% | +12.0% | −2.1% | +12.3% | −1.8% |
  | MSTL | −86.4% | −18.6% | +18.7% | −18.2% | +18.9% |
  | previous-month profile | −90.3% | −21.1% | +23.2% | −20.7% | +23.4% |
  | TimesFM-X | +6.5% | +40.5% * | +6.8% * | +40.7% * | +7.0% * |
  | iTransformer-X | +4.4% | +39.2% * | +11.8% * (resolved only under 2.0.1) | +39.3% * | +12.1% * |
  | GBT-T | +15.9% * | +46.5% * | +8.8% | +46.7% * | +9.0% |
  | TiDE | +14.4% * | +45.6% * | +10.3% * | +45.7% * | +10.6% * |
  | per-unit ridge | +9.3% * | +42.3% * | +6.7% * | +42.5% * | +7.0% * |
  | resolved better than (of 20) | 10 | 15 | 14 (2.0.0: 11) | 15 | 14 |
  | resolved worse than | none | none | none | none | none |
  | position by mean per-unit rank | 1 | 1 | 1 | 1 | 1 |

  - **Window by window** ([`results/bdg2_micro_load_windows.csv`](results/bdg2_micro_load_windows.csv)).
    - In 41 of the 46 windows the meter stays near zero through the forecast month. There 2.0.0 forecast 0.35 kW on
      average against a realised 0.0003 kW (mean RMSE 0.38 kW). The TimesFM forecast, which 2.0.1 returns, reproduces
      the reading (RMSE 0.00 kW).
    - In the other 5 windows (five meters, all after the cutoff) the meter resumed during the forecast month, with
      realised peaks of 18–48 kW. Neither forecast anticipates the restart, and 2.0.0 is marginally better there (mean
      RMSE 5.82 against 5.87 kW; lower in four windows, equal in one), because its historical level is not zero. The
      rule cannot foresee a restart.
  - **How to read the 2.0.1 column.** With the rule ANKYRA's forecast on the near-zero meters is TimesFM's. The three
    meters that are near zero in every window (11 windows, 10 of them late) still dominate the BDG2 unit means, in
    three different ways:
    - against **TimesFM** they now contribute nothing: +2.5% with them, +2.5% without;
    - against forecasters that do better than TimesFM on them they still count **against** ANKYRA: MSTL (−18.6% with
      them, +18.7% without), the previous-month profile (−21.1% / +23.2%) and, slightly, Chronos-2 (+1.5% / +6.8%).
      None is resolved;
    - against forecasters that do worse than TimesFM on them they now count **for** ANKYRA: the trained baselines,
      TimesFM-X and the per-unit ridge rise by 29–36 points (zero-shot gradient boosting by 25, the last-year profile
      by 11), and Chronos-2-X stands at +12.0% with them against −2.1% without. That rise is not a gain in ANKYRA's
      own forecasting: on those meters its forecast is TimesFM's.
  - **The column without the three meters.** Its point estimates do not depend on the rule: 2.0.1 and 2.0.0 agree to
    0.01 points on the late windows and to 0.03 on all windows. Its intervals and its count do depend on it, because
    six further meters keep 23 late micro-load windows in that column.
    - Against TimesFM, Chronos-2, Chronos-2-X, MSTL and the previous-month profile the upper ends come down (TimesFM:
      +1.05 → +0.22 in log units).
    - Against the trained baselines, TimesFM-X and the per-unit ridge the lower ends extend, from between −0.13 and
      −0.35 to between −0.73 and −1.17 (ridge: [−0.134, −0.031] → [−0.987, −0.035]).
    - Three contrasts (iTransformer-X, iTransformer, PatchTST) are resolved there only under 2.0.1: 14 against 11.
    - The reading that does not involve the rule at all is 2.0.0 without the three meters: resolved better than 11 of
      20, worse than none, first by rank.
  - **What remains a limitation.** The near-zero meters were a failure of 2.0.0. 2.0.1 handles them with a rule
    written after the BDG2 result had been seen and untested elsewhere: no other scored population has a window on
    which it changes the forecast. The rule is a sufficient condition, not a derived boundary: a record slightly above
    the threshold is not covered. Its effect on BDG2 describes what the rule changes and is not a test of it. 2.0.1
    against 2.0.0 is +36.4% on the late windows (`results/ankyra_2_0_1/bdg2_near_zero_sensitivity.csv`), with an interval of [−1.323, +0.000] in log units (its upper end is
    at zero: not resolved), and +30.4% [−1.230, −0.001] on all windows. The BDG2 unit means are still dominated by
    three meters.
  - Rank-based summaries barely move: ANKYRA ranks first on BDG2 in every column, the pooled mean rank of the rank
    tests is 6.04 in both versions, and the six-population mean of the mean unit ranks goes from 5.51 to 5.49 (2.1: pooled 5.99, six-population mean 5.45; 2.2: 5.86 and 5.39; first on BDG2 in both).
  - The 2.0.0 results are kept in [`results/ankyra_2_0_0/`](results/ankyra_2_0_0/) and the 2.0.1 results in
    [`results/ankyra_2_0_1/`](results/ankyra_2_0_1/); 2.2, 2.1 (`ANKYRA-21`), 2.0.1 (`ANKYRA-201`) and 2.0.0 (`ANKYRA-200`), with and without
    the three meters, are in [`results/bdg2_near_zero_sensitivity.csv`](results/bdg2_near_zero_sensitivity.csv)
    ([details](docs/EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)).
- **Conventional metrics.** Over the full windows (14 forecasters), Chronos-2-X or the per-unit ridge has a slightly
  lower median unit CV(RMSE) (by 0.2–2.1 points) on four of ten populations (BDG2, EWELD, households, Oslo); 1.x was
  behind on nine of eleven populations. The late-window losses of all 21 forecasters are in the figure above.

Full tables for the ten populations and the evaluation protocol are in [docs/EVALUATION.md](docs/EVALUATION.md).

## LCL households and two changes not adopted

**Low Carbon London households (LCL, UK).** LCL was held out of the ten-population comparison: 1,215 windows of 965
households, 710 of them late. Its 1.x result had been seen earlier, so LCL is not an unexposed population. Its numbers
are not pooled into the tables above. It was first scored, once and without retuning, with the frozen 2.0.1; the
numbers below re-read the same targets with ANKYRA 2.2 (before that with 2.1), and every verdict is the same (the 2.0.1
files are in [`results/ankyra_2_0_1/`](results/ankyra_2_0_1/), the 2.1 files in [`results/ankyra_2_1/`](results/ankyra_2_1/)).

- Against 1.x on the same inputs, ANKYRA is 1.0% better on all windows and 1.3% better on the late windows, both
  resolved.
- Against TimesFM it is +1.6% on all windows and +1.7% on the late windows, neither resolved. The contrasts with
  Chronos-2, Chronos-2-X and TimesFM-X (+1.4% to +1.9%) are not resolved either.
- By mean per-unit rank on the late windows it is first of 21 (5.87; the per-unit ridge is next at 6.51). The
  contrast with the ridge is resolved on all windows (+2.3%) but not on the late windows (+1.6%).
- No same-information baseline, and not the per-unit ridge, is significantly better than ANKYRA (six one-sided tests
  with Holm correction). This does not show that ANKYRA is better than each of them.
- Two windows are off-state windows and none is a micro-load window, so LCL is not a test of the micro-load rule.
  The prediction interval was not scored on LCL.
- As an ablation, the single trust value of 2.1 against the per-block trust of 2.0.1 is +0.13%, interval
  [−0.0025, −0.0007] in log units ([`results/reevaluation_2_1.json`](results/reevaluation_2_1.json)); the gap
  tolerance of 2.2 against 2.1 is +0.21%, interval [−0.0039, −0.0004]
  ([`results/reevaluation_2_2.json`](results/reevaluation_2_2.json)).
- The per-day curves are the LCL panel of Figures 9 and 9b (`results/lcl_by_day.csv`).

**Two changes examined after 2.0.1, neither adopted.**

- *A ridge daily path.* The candidate mixed ANKYRA's centred daily path half and half with that of a per-unit ridge
  regression. The check fixed in advance required the ridge path alone to be at least as accurate as ANKYRA's on
  the 562 household design windows. It was 0.09% worse, so the mixture was not scored. This does not show that a
  mixture could not help.
- *A revised prediction interval.* It needs residuals of completed ANKYRA pseudo-forecasts. At least 742 of the
  7,676 design windows had none, so its coverage criteria, defined over all windows, could not be evaluated, and it
  was not scored. This is a lack of support, not a measured failure.

The forecaster is unchanged. Details are in [docs/LCL_AND_CLOSEOUT.md](docs/LCL_AND_CLOSEOUT.md#lcl-final-stage); the
files are `results/lcl_*` and `results/closeout_status.json` ([file list](results/README.md)).

## Three checks with the forecaster frozen

Each was run with the released forecaster and all its defaults, under a protocol written before the run (the first
two on 4 October 2026, the third on 5 October); the section also reports one post-hoc exploration (the Chronos-2-X
anchoring, 5 October), which had no criterion fixed in advance. None of them changes the forecaster or any table
above. All three were first run with the frozen 2.0.1; the numbers below re-read the same targets with ANKYRA 2.2
(before that with 2.1), and every verdict is the same except on HKUST, where the two borderline hourly contrasts are
resolved under 2.2 (below; the 2.0.1 files are in [`results/ankyra_2_0_1/`](results/ankyra_2_0_1/), the 2.1 files in
[`results/ankyra_2_1/`](results/ankyra_2_1/)). The three carrier-swap files were not recomputed for 2.2; they use
the anchoring of 2.1. Details, limits
and files: [docs/FROZEN_MODEL_CHECKS.md](docs/FROZEN_MODEL_CHECKS.md).

**One method, two foundation-model families, three configurations.** The method is carrier-agnostic:
`ankyra.forecast` takes the foundation model's forecasts as an argument, so the anchoring can be put on top of another
foundation model with nothing selected again. It was run three times: with TimesFM (the released forecaster), with
Chronos-2 (4 October, a pre-specified new arm, ten populations) and with the covariate-informed Chronos-2-X
(5 October, post hoc after the Helsinki result, all twelve populations). The table gives the gain of each anchored
version over its own foundation model, all scored on the same windows with the same bootstrap seed, with the anchoring
of 2.1 (gap tolerance off; the 2.0.1 runs, in `results/ankyra_2_0_1/`, give the same resolved cells). `*`: the 95%
unit-and-month interval excludes zero in favour of the anchored version; no interval excludes zero against it; `—`:
not run.

|Population|Windows|Hourly: TimesFM|Hourly: Chronos-2|Hourly: Chronos-2-X|Energy: TimesFM|Energy: Chronos-2|Energy: Chronos-2-X|
|---|---:|---:|---:|---:|---:|---:|---:|
|BDG2|934|+5.8%|+7.0%|+4.2%|+17.4%|+16.5%|+20.5%|
|Cambridge|1,456|+9.7%*|+11.5%*|+4.7%*|+15.7%*|+18.9%*|+8.9%*|
|HEEW|1,282|+4.5%*|+7.7%*|+4.8%*|+10.1%|+14.6%*|+12.2%*|
|EWELD|931|+3.3%*|+3.0%*|+3.8%*|+5.3%|+9.4%|+7.7%|
|GoiEner non-household|1,234|+4.4%|+4.4%|+3.3%|+16.6%*|+20.1%*|+19.5%*|
|GoiEner households|1,232|-0.0%|+0.3%|+0.1%|+29.7%*|+33.3%*|+31.1%*|
|Oslo|1,147|+11.3%*|+12.2%*|+6.3%*|+16.1%*|+17.9%*|+8.2%*|
|Drammen|1,375|+11.4%*|+9.9%*|+4.5%*|+20.1%*|+19.3%*|+9.0%*|
|CINELDI|929|+6.7%*|+6.0%*|+5.4%*|+17.1%*|+16.3%*|+16.4%*|
|Suzhou park|127|+11.9%*|+17.8%*|+14.6%*|+16.4%*|+22.9%*|+20.2%*|
|HKUST campus|120|+8.4%|—|+5.6%*|+37.9%*|—|+12.0%|
|Helsinki|1,165|+4.6%|—|+0.8%|+6.0%|—|+0.6%|

- **The anchoring transfers.** It improves hourly error resolvably on 7/12 populations with TimesFM,
  7/10 with Chronos-2 and 8/12 with Chronos-2-X, monthly energy on
  8/12, 8/10 and 8/12, and never makes its own foundation model
  resolvably worse. The weak spot is also shared: households, where no version improves the hourly error.
- **Against a covariate-informed foundation model.** Where ANKYRA's advantage over Chronos-2-X is small or reversed,
  the anchoring can be put on Chronos-2-X itself: ANKYRA-X is better than
  Chronos-2-X on 8 of 12 populations for hourly error and on 8 of 12 for monthly energy, each resolved, and never
  resolvably worse. On UNICON (a descriptive arm of the external test) it is 4.5% lower hourly and 10.2% lower for
  energy than Chronos-2-X (point estimates).
- **The finished forecaster's accuracy depends in part on the foundation model.** Anchored to Chronos-2, which is about as accurate as
  TimesFM, it is not separated from the TimesFM-anchored ANKYRA on any population on these windows (on all household
  windows, near-zero meters included, it is 2.8% worse). Anchored to the stronger Chronos-2-X it is
  resolvably better on Cambridge, Oslo, Drammen, Helsinki, and on Helsinki it closes the gap of the confirmation test
  (+6.4% hourly, +12.7% energy against the TimesFM-anchored version).
- **Limits.** Two foundation-model families in three configurations, not foundation models in general; the constants were selected under TimesFM; every population
  had been scored before, and the Chronos-2-X run is post hoc. The released forecaster stays TimesFM-anchored (2.2): choosing the
  foundation model after seeing every population would leave no untouched data to test the choice
  (`results/carrier_swap_combined.csv`, `results/carrier_swap.csv`, `results/carrier_swap_x.csv`;
  [details](docs/FROZEN_MODEL_CHECKS.md#another-foundation-model)).

**A blind test on a population never used before.** "Blind" here means that no rule or constant of ANKYRA was
chosen with this population in view, that the units and the scoring were fixed before any load value was opened, and
that inputs were truncated at each origin and the forecasts saved before any target loss was computed. It does not mean that the foundation models had never
seen the data: whether TimesFM or Chronos-2 was pretrained on it was not checked. The frozen forecaster had one original first read on the incomer meters of the HKUST campus
(Hong Kong; 134 windows, 33 units, 30 of them non-zero), a dataset the project had not read. Units were fixed from
the metadata before any load value was opened, and forecasts were saved before any target loss was computed. Comparators,
a carrier exploration and a correction of one constant (below) were added afterwards.

- Monthly energy error is 42.9% below TimesFM's (interval 10–62%), and the interval excludes zero.
- Hourly error is 8.8% below TimesFM's and 11.7% below Chronos-2's, intervals [−0.230, −0.007] and [−0.293, −0.001]
  in log units: **resolved under 2.2**. This reading changed with 2.2: under 2.0.1 and 2.1 (8.4% and 11.3%) both
  intervals ended at zero (upper ends −0.001 and +0.000), borderline and not counted as resolved. The meters are
  quantised at 10 or 100 kWh, and the hourly gain comes from the 19 finely metered units.
- Against naive and profile forecasts the hourly gain is 12–24% and resolved. Trained baselines were not run.
- The two covariate-informed foundation models were added afterwards: ANKYRA is **not separated** from Chronos-2-X
  (+4.0% hourly) or TimesFM-X (+5.5%).
- With three more baselines that need no training (Holt-Winters, MSTL, zero-shot GBT), also added afterwards, HKUST
  has the same 14 forecasters as the full-window comparison; ANKYRA has the first mean unit rank (3.30; next, the
  per-unit ridge, 4.27). Its per-day curves are the HKUST panel of Figures 9 and 9b: lowest of the 14 on 15 of 31
  days for hourly error and on 24 for the energy delivered to date.
- One small site: it is not merged into the tables above and does not show that the forecaster generalises
  (`results/hkust_first_read.csv`, `results/hkust_by_day.csv`).

![Two checks with the forecaster frozen](figures/fig17_frozen_checks.png)

*Figure 17. Two checks with the forecaster frozen, ANKYRA 2.2 (a: anchoring on either foundation model, ten
populations; b, c: HKUST, ANKYRA against each comparator).*

**A pre-registered confirmation test (Helsinki).** On 5 October 2026 the frozen forecaster was scored once on the
electricity of Helsinki's city service buildings (300 property codes drawn by hash; 201 units, 1,168 windows, eleven
origins from November 2025 to September 2026, after the public release of both foundation models). The success
criteria were written before any load value was parsed: monthly energy error resolvably below TimesFM's, and hourly
error not resolvably above it. **The confirmation was not established.**

- Monthly energy error is 6.2% below TimesFM's, but the interval crosses zero ([−0.168, +0.106] in log units): the
  primary criterion **failed**.
- Hourly error is 4.9% below TimesFM's, not resolved: the secondary criterion passed.
- **ANKYRA's errors are resolvably higher than Chronos-2-X's** on both: by 5.6% hourly and by 13.6% for monthly
  energy. In mean unit rank among the 14 forecasters Chronos-2-X is first (4.12) and ANKYRA second (4.17).
- Against the per-unit ridge, naive, profile and statistical forecasts and the zero-shot GBT, ANKYRA's hourly gain is
  5–28% and resolved against all of them except the four-week profile, as on the other populations.
- Per-day curves are the Helsinki panel of Figures 9 and 9b: ANKYRA is below TimesFM on 25 of 31 days for hourly
  error and on 25 for energy to date, below Chronos-2-X on 3 and 6.

Together with UNICON ([below](#external-test-of-the-frozen-21-unicon)) this is one of the two tests of the project
with criteria fixed in advance and enough units to resolve them. It does not confirm the energy advantage over
TimesFM seen on the ten populations and on HKUST
([details](docs/FROZEN_MODEL_CHECKS.md#a-pre-registered-confirmation-test-helsinki); `results/helsinki_confirmation.csv`,
`results/helsinki_criteria.json`, `results/helsinki_by_day.csv`).

## External test of the frozen 2.1 (UNICON)

On 6 October 2026 the frozen ANKYRA 2.1 (package 2.1.0) was scored once on UNICON: 64 building meters on the five
campuses of La Trobe University (Victoria, Australia), 15-minute readings from 2018 to 2022. It is the first test of
2.1 on data not read before. The numbers below re-read the same targets with ANKYRA 2.2, and both verdicts are the
same (the 2.1 files are in [`results/ankyra_2_1/`](results/ankyra_2_1/)). The data are licensed CC BY-NC-SA 4.0
(research use only) and are not redistributed here.

- **Protocol.** The sample, the window rules, the 14 forecasters of the full-window comparison, the estimand and the
  criteria (seed 20261006) were frozen before any reading was parsed. ANKYRA ran with all its defaults (category
  `Public`, `dst_region="none"`, a fixed UTC+10 grid). All forecasts were saved before any target was read, and the
  targets were scored once.
- **Amendment 01.** Under the frozen complete-window rule no window qualified: short gaps are dense. The amendment was
  written after the missingness had been seen and before any forecast. It fills gaps of at most 6 hours in the inputs
  causally: linear interpolation inside the context, never across an origin or pseudo-origin. Targets are never
  filled; at least 95% of the target hours must be observed. The result is **843 windows of 60 units** over 37 months.
- **Criteria.** Primary: monthly energy error against TimesFM 2.5, upper end of the 95% unit-and-month interval below
  zero. Secondary: hourly error, lower end at or below zero. **The test is not confirmed**: the primary criterion
  failed (4.4% lower, interval [−0.157, +0.116] in log units) and the secondary passed (2.4% lower, lower end −0.052).
  As on Helsinki, the primary criterion fails on monthly energy against TimesFM.

| ANKYRA 2.2 against | Hourly | Monthly energy |
|---|---|---|
| TimesFM 2.5 | +2.4% [−0.052, +0.011] | +4.4% [−0.157, +0.116] |
| Chronos-2 | +2.1% [−0.055, +0.018] | +2.7% [−0.147, +0.117] |
| Chronos-2-X | +5.8% * [−0.114, −0.003] | +11.7% [−0.294, +0.029] |
| TimesFM-X | +4.4% * [−0.080, −0.004] | +10.0% [−0.246, +0.044] |
| Per-unit ridge (674 windows) | +4.2% * [−0.095, −0.007] | −0.6% [−0.129, +0.138] |
| Holt-Winters, MSTL, zero-shot GBT | +14.6% to +25.7%, each * | +19.1% to +26.9%, each * |
| Naive and profile forecasters (five) | +6.5% to +34.3%, each * | +5.3% to +39.3%; * on two |

`*`: the interval (log units) excludes zero in favour of ANKYRA; no interval excludes zero against it.

- **Rank.** By mean unit rank among the 14 (on the 674 windows where the ridge is defined) ANKYRA is first (3.03),
  ahead of Chronos-2 (3.92), TimesFM (4.20), TimesFM-X (4.40), the per-unit ridge (4.88) and Chronos-2-X (5.10).
- **Reading.** On hourly error ANKYRA is resolvably better than Chronos-2-X, TimesFM-X, the per-unit ridge and every
  statistical, naive and profile method; against TimesFM and Chronos-2 it is about 2% better, not resolved. On monthly
  energy it is 3–12% better than every foundation model, none resolved.
- **Diagnostic** (written after the forecasts were frozen, before scoring). The dense gaps leave few complete
  pseudo-origin windows: ANKYRA 2.1 used on average 0.51 of its 6 pseudo-origin pairs, so its weights stayed close to
  their priors (with the gap tolerance of 2.2 it uses 3.49). This test measured the frozen 2.1 on gap-dense data where
  its error weighting barely acts. The descriptive arms do not separate: the 2.0.1 arm is −0.1% hourly and −2.5% for
  energy against 2.2 (2.1: +0.0%), and a single whole-window combination weight or a half-and-half average is not
  separated from ANKYRA (hourly −0.1% for both, energy −1.2% for both; 2.1: −0.0%, +0.0% and +1.2%), so UNICON
  cannot answer whether weighting by block matters ([below](#what-the-parts-buy)).
- **By origin year** (descriptive): against TimesFM ANKYRA is behind in 2020, the year of the pandemic closures
  (−4.0% hourly, −18.7% energy, not resolved), behind by 1.1% hourly and ahead by 0.8% for energy in 2021, and ahead
  in the other years.
- **Per-day curves** are the UNICON panel of Figures 9 and 9b: lowest of the 14 on 18 of 31 days for hourly error and
  on 4 for energy to date.
- **Southern hemisphere.** UNICON is the only evaluated population in the southern hemisphere; the annual temperature
  harmonic keeps its northern-hemisphere phase. Correcting the phase in a development copy (descriptive) changed the
  errors by about −0.01% hourly and −0.2% for monthly energy, which does not explain the failed test; the frozen
  package keeps the original behaviour ([when not to use it](#when-not-to-use-it)).

Files: [`results/unicon_external.csv`](results/unicon_external.csv) (all contrasts, including the descriptive arms),
[`results/unicon_criteria.json`](results/unicon_criteria.json) (criteria, ranks, years, diagnostic, licence note),
[`results/unicon_by_day.csv`](results/unicon_by_day.csv).

## How the handover works

![One test window](figures/fig6_example_window.png)

*Figure 6. One test window.*

In September a university building's load rises after the summer. TimesFM carries the recent level forward, while
ANKYRA's history-weighted level anticipates the rise. The balance between the two sources shifts with the lead time:

- Under a **fixed division** (history's level, the model's shape), the foundation model alone is better in the first
  week and worse later.
- ANKYRA estimates, for each unit, how much of the model's daily means to use (one weight for each forecast week).
  - The weights are fitted on the unit's completed pseudo-forecasts: the fixed division against TimesFM.
  - They are then applied to ANKYRA's history-side daily means, whose level also contains the model candidate
    ([details](docs/METHOD.md#week-by-week-handover)).
- On the three populations scored for the first time after the handover was fixed, ANKYRA's point estimate beats
  TimesFM in **every** forecast week.
- ANKYRA 2.2 improves on the fixed division on nine of the ten populations, each resolved: by 3.6–26.6% on
  eight, and on BDG2 by 36.7% with the micro-load rule (8.7% under 2.0.0). It is not resolvably different on the
  Suzhou park. The fixed division (F0) is a 1.x-era forecaster without the within-day anchoring, so part of this gain
  is the anchoring.
- **Which part matters.** An ablation fixed before it was run separates the pieces. On the six test populations:
  - mixing in the model's daily means at a fixed half weight already gives most of the gain (63–96% on five, 10% on
    Cambridge);
  - estimating the weight per unit adds 0.8–1.2%, resolved on three of the six and never resolvably worse;
  - separate weights for each week add nothing over one weight per unit and month (0.2% worse on GoiEner
    non-household).

  What carries the gain is per-unit, error-weighted mixing. The weekly weights describe how the balance shifts with
  lead time ([details](docs/EVALUATION.md#what-the-handover-contributes)).
- **Why error weights and an off-state rule.** Departures from normal operation become more likely to continue the
  longer they have lasted. This holds within units, on seven populations. The longer a departure has lasted at the
  origin, the more the model's recent information is worth over the whole month
  ([evidence](docs/EVALUATION.md#departures-from-normal-operation-persist)). Without the off-state rule, the shrinkage
  of the weights keeps the historical level in play for a meter that is off. The micro-load rule (2.0.1) extends this
  to a record that stays within 10⁻³ kW of zero through the whole context. It was written after the BDG2 result of
  2.0.0 had been seen ([definition](docs/METHOD.md#off-state-and-micro-load-rules);
  [status](#what-changed-in-20-201-21-and-22)).

![Ablation, handover granularity and lead-week profile](figures/fig4_handover_and_ablation.png)

*Figure 4. Ablation, handover granularity and lead-week profile.*

## Within-day anchoring (2.0)

The within-day shape is where the foundation model is strongest, and where 1.x added nothing. 2.0 gives the unit's
own history a say there, by the rule the other blocks already use:

- **Analog days.** For each horizon day, the unit's complete past days of the same calendar type within ±14 days of
  the same day of year and in the same daylight-saving state; up to eight, the closest in daily-mean temperature to
  the day's climatology. Their shapes, each divided by the scale of the 744 hours before it, are averaged and rescaled
  to the origin.
- **Trust.** $w=w^T+\omega\,(S-w^T)$, with $\omega$ the least-squares weight of the
  analog shape against the model's shape on the unit's three completed pseudo-origin windows, pooled over all 744 hours
  (since 2.1; 2.0–2.0.1 estimated one $\omega_k$ per lead block, days 1–7, 8–14, 15–21, 22–31), clipped to $[0,1]$,
  shrunk towards zero by $n/(n+2)$ and capped at ½. No evidence means the model's shape, i.e. the 1.x forecast.
- **What it leaves untouched.** Both shapes have zero daily means: the pre-projection daily means, and with them the
  level, the daily path, the energy readout and a peak readout computed from them, are identical to 1.x (the
  delivered trajectory max(·, 0), and a readout computed from it, can differ where the projection binds). The three pseudo-origin forecasts are among the six ANKYRA already computes. The micro-load
  windows of 2.0.1 are a different matter: there the whole trajectory is TimesFM's.
- **Where it acts.** On buildings with fixed schedules nearly every window is anchored (mean trust 0.20–0.33 under 2.0.0,
  0.20–0.34 under 2.1) and the hourly error falls by 0.8–4.2% (2.0.0 against 1.x; 1.0–4.6% for 2.1), growing with lead
  time; on households the trust stays near zero (0.08; 2.1: 0.07) and the forecast is unchanged.
- **How it was chosen, and how strong the evidence is.** The rule is the sixth version of a similar-day idea. The first
  four did not meet their no-harm criterion on the development data, and the fifth did not meet it on the test
  populations. The sixth was selected from a family written down in advance, on nine design sets (three development
  populations and the pre-cutoff windows of the six test populations), validated on CINELDI and the Suzhou park, and
  evaluated once on the post-cutoff test windows under a frozen protocol. A further round that tried six
  pseudo-origins, an analog daily-path candidate and finer handover blocks adopted nothing. 2.1 later pooled the four
  trust values into one after all twelve populations had been scored with 2.0.1: in a simplification study with a
  non-inferiority margin fixed before scoring, one value was non-inferior on all twelve (hourly error +0.01% to +0.45%
  against 2.0.1 on all windows; largest upper end +0.0048 log units). This is a re-evaluation, not a test. The full
  account, with the criteria and their values, is in [docs/EVALUATION.md](docs/EVALUATION.md#within-day-anchoring-20).

## What the parts buy

[`results/component_contributions.csv`](results/component_contributions.csv) lists, for each of the ten populations,
the hourly gain of each step from the fixed division (F0) to ANKYRA 2.1 (all windows; positive = the step, or the
first-named variant in the last two rows, lowers the error). All of it is a re-evaluation of windows read before.

| Step | Hourly gain over the ten populations |
|---|---|
| handover of the daily means (F0 → F1) | −1.8% (Suzhou park) to +14.8% (EWELD); negative also on Oslo |
| off-state rule (F1 → 1.x) | EWELD +13.2%, GoiEner households +4.3%, GoiEner non-household +1.8%; 0 elsewhere |
| within-day anchoring (1.x → 2.0.0) | −0.05% (GoiEner households) to +4.2% (Oslo) |
| micro-load rule (2.0.0 → 2.0.1) | BDG2 +30.4% (rule written after that result was seen); 0 elsewhere |
| one within-day trust value (2.0.1 → 2.1) | +0.01% to +0.45%; resolved on Oslo and Drammen |
| all steps (F0 → 2.1) | +1.2% (Suzhou park, not resolved) to +36.5% (BDG2); resolved on nine |
| weekly instead of monthly handover weights | −0.34% to +0.80%; never resolved in favour of weekly weights, resolved against them on the two GoiEner populations |
| block-wise weights instead of one whole-window weight (B2) | −1.8% to +1.5%; see below |

The first four rows are differences of two contrasts (point estimates, no interval); the others are direct contrasts
with intervals.

**Block-wise weighting against a plain combination.** B2 combines the same two forecasts as ANKYRA (the history side
and TimesFM) with one combination weight per unit for the whole window, set from the unit's own pseudo-origin errors.
On the twelve populations it is within ±2% of ANKYRA in hourly error, and block-wise weighting was not shown to add
accuracy: on hourly error ANKYRA is resolvably better only on GoiEner
households (1.5%), B2 is resolvably better on Cambridge (1.2%) and Oslo (1.8%), and the other nine are not separated;
on monthly energy no population is separated. A half-and-half average of the two forecasts (B1) is weaker: ANKYRA is
resolvably better than it on three populations for hourly error and on two for energy. Read honestly:

- the measurable gain comes from the history-side forecast itself (level candidates, daily path, analog-day shape and
  the foundation model's window mean as a level candidate) and from weighting by the unit's own pseudo-forecast
  errors;
- splitting the weights by block adds nothing measurable on these populations, consistent with weekly handover
  weights being no better than monthly ones and with one within-day trust value being no worse than four;
- the block decomposition remains the exact identity used for interpretation, the readouts and diagnosis
  ([theory](#theory-exact-properties)).

B2 is a simpler special case of ANKYRA (one weight per window). It has not been adopted: these numbers re-evaluate
data read before. On UNICON, where B2 was a pre-specified descriptive arm, it is not separated from ANKYRA either
([above](#external-test-of-the-frozen-21-unicon)).

**Constants.** [`results/constants.csv`](results/constants.csv) lists every constant of the forecaster (20 rows) in seven groups: fixed by the
problem definition (context, horizon, weekly handover split), the evidence window (numbers of pseudo-origins), shrinkage
(the five design choices that weight the unit's own errors), the analog shape and peak readout, numerical safeguards,
data-state rules (off-state, micro-load, short-gap) and the frozen historical estimator (climatology). It gives each
constant's value, where it was fixed (before any evaluation, on development data, in the 2.0 design, or by an earlier component) and,
where measured, its sensitivity. For the five constants that were varied one at a time on the nine design sets (the
number of pseudo-origins for the handover and for the within-day trust, the shrinkage of the handover weights and of
the trust, the cap of the trust), the mean log ratio over the nine sets moves by at most 0.0034 over the values tried
([`results/constants_sensitivity.csv`](results/constants_sensitivity.csv)). None was set on the post-cutoff test
windows; the micro-load threshold reuses the scale floor, and the rule itself was written after the BDG2 2.0.0 result.

## Readouts: peak and prediction interval

Energy is read from the level (744 × the level). The peak and the interval have their own operators; the calls are
shown in [`examples/quickstart.py`](examples/quickstart.py).

### Peak

The monthly peak is read separately from the trajectory. The estimate is ANKYRA's daily means plus the largest recent
excursion of the same day type:

$$U=\max_d(\hat L_d+A_{\tau_d}).$$

Because maxima commute, this equals an hour-wise envelope. It satisfies $U\ge\max_d\hat L_d\ge\bar F$ and has an exact
median property under a stated working distribution. Its error splits into level, daily-path, amplitude and selection
terms, so ANKYRA's level gains carry into the peak.

- Against the maximum of the same trajectory, it reduces peak error by **18–66% on all ten populations**.
- Against last month's observed peak, it is better on regularly operated buildings (Drammen, Oslo, HEEW: 12–16%) and
  worse on CINELDI's industrial customers and on EWELD.

![Peak operator](figures/fig5_peak_operator.png)

*Figure 5. Peak operator.*

### Prediction intervals

On GoiEner households the pseudo-origin interval around ANKYRA covers **79.7%** of hours at
the nominal 80% level and 88.4% at 90%. It is the only interval close to its nominal level: TimesFM's native 0.1–0.9
band covers 36.1% and Chronos-2's native 80% band 68.8%. On the Winkler score the ANKYRA interval beats TimesFM's band by
7.7% and the same interval around the fixed division by 4.6%, both resolved. It ties with Chronos-2's band (0.4%
behind, unresolved). Intervals were scored on this one population.

![Prediction intervals on households](figures/fig13_intervals.png)

*Figure 13. Prediction intervals on households.*

Applied afterwards to all ten populations, the same interval covers **75.7–82.2%** of hours at the nominal 80%
level and 84.6–89.2% at 90%, against 65–79% for Chronos-2's native 80% band and 35–57% for TimesFM's. It is not sharper
than Chronos-2's quantiles: on the Winkler score ANKYRA is resolvably better than TimesFM's band on eight populations
(in 2.0.0, 2.0.1 and 2.1) but not separated from Chronos-2's on six and resolvably worse on four (HEEW, EWELD, GoiEner
non-household and CINELDI). Under 2.0.0 it was resolvably worse on five: BDG2 sat just beyond the boundary and now sits
just inside it ([`results/intervals_winkler_contrasts.csv`](results/intervals_winkler_contrasts.csv)). Its coverage
also falls with lead time (first week 80–87%, fourth week 72–79%), because the residuals are pooled over the whole
window, and it should not be used for units that switch off, where its width explodes
([details](docs/EVALUATION.md#readouts)).

![Interval coverage on ten populations](figures/fig16_intervals_ten_populations.png)

*Figure 16. Interval coverage on ten populations.*

## When anchoring is expected to help

Every forecast carries two statistics of the unit's own record on the monthly level, computed before the forecast and
not used by it (`anchoring_record`, 2.2): the weight the level block gives the foundation model's window mean
(`carrier_level_weight`) and the log ratio of the best historical candidate's pseudo-origin RMS error to the foundation
model's (`history_vs_carrier_log_ratio`; negative means the unit's history beat the model at its earlier origins). On
the fourteen populations of this repository (the ten above, the development store, HKUST, Helsinki and UNICON; 14,177
windows, 14,006 where the log ratio is defined) the realised gain of ANKYRA over TimesFM falls with both. Deciles are global over all windows; gains are the
unit-equal log RMS ratio with its 95% unit-and-month interval ([`results/anchoring_gain_deciles.csv`](results/anchoring_gain_deciles.csv)).

| `history_vs_carrier_log_ratio` decile | range | monthly-energy gain over TimesFM | hourly gain over TimesFM |
|---|---|---|---|
| 1 (history far better than the model at the pseudo-origins) | below -1.15 | +32% [-0.502, -0.211] | +3% [-0.069, -0.010] |
| 2–5 | -1.15 to -0.30 | +25%, +18%, +17%, +9% | +3%, +3%, +2%, -0% |
| 6–8 (history about as good as the model) | -0.30 to 0 | -1%, -6%, -3% | +0%, -7%, -4% [-0.002, +0.123] |
| 9–10 (the model better at the pseudo-origins) | above 0 | +1%, +5% | -1%, -1% |

By `carrier_level_weight` the picture is the same: the energy gain goes from +29% and +25% in the two lowest
deciles (weight below 0.10) to -2% in the highest (weight above 0.34), where the hourly error is -5%
[-0.000, +0.165], unresolved (the interval reaches zero).

How to read it. The relation holds *between* populations and units: the two populations on which pre-registered tests
failed (Helsinki, UNICON) sit in the lower-gain half. Within one population the
correlation is weak (Spearman 0.1–0.3 on most, about zero on Helsinki), so the statistics say where anchoring is likely
to pay, not which window will. A value of `history_vs_carrier_log_ratio` near or above zero, or a carrier weight above
about 0.2, means the unit's own record gives no reason to expect a gain over the foundation model alone. The forecaster
does not act on these statistics: a per-window shrinkage rule built on them improved the development store and failed
the validation populations ([P20](theory/README.md)); the weights stay as they are and the statistics are reported.

## Long-context foundation models and generic combinations

Two descriptive experiments on ANKYRA 2.2, run under a protocol fixed before anything was scored (no pass line, one
implementation each, nothing tuned). Every population had been read before: the numbers are re-evaluations, not
tests. 95% unit-and-month intervals, seed 20261007.

**A year of context for the foundation model.** TimesFM 2.5 with an 8,736-hour context (`TimesFM-8736`), Chronos-2 with
8,192 hours (its limit) and the unchanged package anchored to TimesFM-8736 (`ANKYRA-T8736`), on the late windows of the
ten populations ([`results/long_context_carriers.csv`](results/long_context_carriers.csv)). Counts of ten: point
estimate better / resolved better / resolved worse for the first-named forecaster.

| Contrast | Hourly | Monthly energy |
|---|---|---|
| ANKYRA vs TimesFM-8736 | 8 / 4 / 1 | 9 / 4 / 0 |
| ANKYRA vs Chronos-2-8192 | 9 / 6 / 1 | 10 / 6 / 0 |
| ANKYRA-T8736 vs TimesFM-8736 | 9 / 5 / 1 | 9 / 6 / 0 |
| TimesFM-8736 vs TimesFM-1344 | 9 / 4 / 0 | 8 / 2 / 0 |

The longer context helps TimesFM somewhat, but anchoring still lowers the error on the one-year-context carrier, and
the monthly-energy gain is no smaller than with 1,344 hours; the exception is the GoiEner households on hourly error,
the single resolved-worse population in every ANKYRA row.

**Generic combination partners.** B2(X) is the B2 combination ([above](#what-the-parts-buy)) with the history-side
forecast H replaced by a generic local forecast X (weekly seasonal naive, 4-week profile, last-year profile); EW(X) is
the half-and-half average of TimesFM and X (X also the per-unit ridge or MSTL where saved). Twelve populations, all
windows ([`results/generic_combinations.csv`](results/generic_combinations.csv)). Counts of twelve: first-named better /
worse / not resolved.

| Contrast | Hourly | Monthly energy |
|---|---|---|
| B2(H) vs B2(seasonal naive, week) | 8 / 0 / 4 | 7 / 0 / 5 |
| B2(H) vs B2(4-week profile) | 8 / 0 / 4 | 7 / 0 / 5 |
| B2(H) vs B2(last-year profile) | 3 / 0 / 9 | 1 / 1 / 10 |
| B2(H) vs best B2(X) | 2 / 0 / 10 | 0 / 1 / 11 |
| B2(H) vs best equal-weight average | 4 / 0 / 8 | 1 / 1 / 10 |
| ANKYRA vs best generic combination | 0 / 0 / 12 | 0 / 1 / 11 |

"Best" was picked after scoring, per population and error, which favours the generic side; the best B2(X) is the
last-year profile on ten of twelve populations, and the one resolved-worse energy row is Oslo. The gain comes from the
per-unit, error-weighted combination with a long-memory history forecast. The history side was not separated from
the last-year profile as a partner on most populations, so no advantage over it is established; it was resolvably
better than the short-memory partners on eight of twelve populations.

**Three candidate changes, none adopted.** Under the same protocol three changes to the forecaster were tested on the
ten populations against criteria written before scoring: a seasonal-phase climatology (the annual temperature harmonic
may take a negative amplitude, i.e. the southern-hemisphere phase) together with a prior temperature curve for the
Commercial group; prediction-interval residuals taken from combined pseudo-forecasts; and a one-weight (B2) point
forecast. None met its criteria, so none was adopted and the package stays 2.2. On UNICON (descriptive only) the
phase-corrected climatology changed the errors by −0.01% hourly and −0.2% on monthly energy, so the northern-hemisphere
phase does not explain the UNICON result.

## Theory: exact properties

![Exact properties on a test window](figures/fig7_operators.png)

*Figure 7. Exact properties on a test window.*

The construction is auditable because each step has a stated property. These mathematical contributions sit beside the
forecaster in their own folder, [theory/](theory/), which the forecaster does not import:

- [theory/README.md](theory/README.md) lists P1–P20 with the condition under which each holds, what ANKYRA uses it for,
  its code and its check;
- [theory/PROOFS.md](theory/PROOFS.md) gives the proofs, the counterexamples and, where the earlier study measured them,
  their consequences on data. The *earlier study* is the first version of this model, evaluated on Spanish supply
  points and BDG2;
- [theory/operators.py](theory/operators.py) writes each property as a function, and
  [theory/test_operators.py](theory/test_operators.py) checks every one numerically.

- **Replacement is exact (P4).** Replacing a block changes the MSE by exactly that block's change. Any division of
  labour between two forecasters can therefore be scored from block losses. A level-only correction can reduce the MSE
  by at most the level's share.
  - In the earlier study, replacing DLinear's level and daily path improved it by 5.0%; for PatchTST the effect was
    unresolved.
- **Why a fixed division is not enough (P5).** For one unit, a division's gain is bounded by $\tfrac12\log(1-\pi)$,
  while its loss is unbounded. A division that is optimal on pooled error can therefore lose for the typical unit.
  ANKYRA's per-unit weights and weekly handover answer this.
- **How much history the weights need (P7–P9).** A record of $m$ hours yields $\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$
  completed errors. Below two errors the weights are equal, and the annual candidate needs 10,248 h.
  - Shrinkage bounds how far the weights can move from equal. Deleting a candidate at the origin can break that bound.
  - In the earlier study, restricting history to 12, 9 and 6 months worsened the level by 6.2%, 14.2% and 20.6%.
- **Energy (P11–P12).** Clipping at zero cannot increase any hour's error. No map can keep the energy, return
  nonnegative load and never increase error, all at once. Energy is therefore read from the level.
- **Peak (P15–P17).** The peak readout has a scalar form, satisfies $U\ge\max_d\hat L_d\ge\bar F$, and has a four-term
  error decomposition and a finite-support median property. Counterexamples mark where each stops.
- **Estimands (P19).** Pooled and unit-equal summaries can disagree in sign for an algebraic reason, so the evaluation
  reports both, with the mean rank and conventional metrics.
- **Evidence bound (P20).** Seven level candidates judged on at most six pseudo-origin errors cannot be told apart
  reliably (the known minimax rates of aggregation, Nemirovski 2000 and Tsybakov 2003, are a sizeable fraction of the
  error variance at six pseudo-origins; the measured hit rate of the selected candidate is 19–29% against a chance of
  17%). The weights are shrunk for this reason, and the record statistics that indicate, between populations, where
  anchoring pays are reported with each forecast ([`anchoring_record`](#what-comes-out)).

Each is written as a function in `theory/operators.py` or carried by the forecaster's own functions (P1, P3, P15, P19),
and checked by `python -m unittest discover -s theory -t .`.

## Reproducibility

- The **reference implementation reproduces the evaluated forecasts**: on 484 windows of seven populations, among
  them all 263 micro-load windows of BDG2 and of the EWELD post-cutoff windows, the 2.1 mode (`gap_tolerance=False`)
  matches the scored 2.1 forecasts to the precision of their float32 storage (largest relative difference 7.4×10⁻⁸);
  their level and daily means are bit-identical to 2.0.1 and the trust is one value. The default 2.2 forecast is
  bit-identical to the 2.1 mode on the 92 windows whose whole history is complete and differs from it on 53 of the
  other 392. The 2.0.1 mode (`gap_tolerance=False, single_trust=False`) matches the scored
  2.0.1 forecasts (6.6×10⁻⁸). The 2.0.0 mode (`gap_tolerance=False, single_trust=False, micro_load_rule=False`) matches the stored forecasts
  of the 2.0.0 evaluation (5.7×10⁻⁸) and, compared directly, the scored 2.0.0 arm of the panel (6.6×10⁻⁸). The 1.x
  mode (`gap_tolerance=False, within_anchor=False, micro_load_rule=False`) matches the evaluated 1.x forecasts exactly (largest difference 3.4×10⁻¹³ kW). On micro-load windows 2.1 and
  2.0.1 are bit-identical to the TimesFM forecast; elsewhere 2.0.1 is bit-identical to the 2.0.0 mode. The TimesFM
  adapter, the peak operator and the interval functions are unchanged and were exact in the 1.x record.
  The current record ([results/REPRODUCTION_CHECK.json](results/REPRODUCTION_CHECK.json)) was taken on the code of
  this release (package 2.2.0); the record of package 2.1.0 is kept as
  [results/ankyra_2_1/REPRODUCTION_CHECK.json](results/ankyra_2_1/REPRODUCTION_CHECK.json), the record of package 2.0.3 as
  [results/ankyra_2_0_1/REPRODUCTION_CHECK.json](results/ankyra_2_0_1/REPRODUCTION_CHECK.json), and the record of the
  2.0.1 package is
  [results/REPRODUCTION_CHECK_2_0_1.json](results/REPRODUCTION_CHECK_2_0_1.json); the 2.0.0 and 1.x records are
  [results/ankyra_2_0_0/REPRODUCTION_CHECK.json](results/ankyra_2_0_0/REPRODUCTION_CHECK.json) and
  [results/ankyra_1x/REPRODUCTION_CHECK.json](results/ankyra_1x/REPRODUCTION_CHECK.json).
- `results/` holds every scored statistic behind the figures and tables. Most files are ANKYRA 2.2; files not re-exported for 2.2 keep the version they were measured on: the three carrier-swap files (`carrier_swap.csv`, `carrier_swap_x.csv`, `carrier_swap_combined.csv`), `component_contributions.csv`, `constants_sensitivity.csv`, `robustness.csv` and `intervals_winkler_contrasts.csv` were measured with 2.1 (gap tolerance off), `cost_per_window.csv` with 2.0.0 and `handover_granularity.csv` with 1.x, and `bdg2_micro_load_windows.csv` compares 2.0.0 with 2.0.1. The two experiments added afterwards (`long_context_carriers.csv`, `generic_combinations.csv`) use 2.2. Each file's entry in [results/README.md](results/README.md) names its version. The LCL (`lcl_*`), HKUST
  (`hkust_*`), Helsinki (`helsinki_*`) and UNICON (`unicon_*`) files are 2.2 re-reads; the first three were first scored with
  2.0.1, whose files are in `results/ankyra_2_0_1/` (with `lcl_audit.json`, moved there), UNICON with 2.1, whose files
  are in `results/ankyra_2_1/` with every other 2.1 file;
  [`reevaluation_2_1.json`](results/reevaluation_2_1.json) summarises the 2.1 re-reads and
  [`reevaluation_2_2.json`](results/reevaluation_2_2.json) the 2.2 re-reads. `pip install -e ".[figures]"`
  and then `python figures/make_figures.py` regenerate all figures from it. The 2.0.1 result files are kept in
  `results/ankyra_2_0_1/` (in `ablation.csv`, `conventional_metrics*.csv` and `bdg2_near_zero_sensitivity.csv` 2.0.1 is
  also a row, `ANKYRA-201`), the 2.0.0 files in `results/ankyra_2_0_0/`, the 1.x files in `results/ankyra_1x/`.
  Files added after 2.1.0: [`unicon_external.csv`](results/unicon_external.csv),
  [`unicon_criteria.json`](results/unicon_criteria.json) and [`unicon_by_day.csv`](results/unicon_by_day.csv) (the
  UNICON external test), [`lcl_by_day.csv`](results/lcl_by_day.csv) (the LCL panel of Figures 9 and 9b),
  [`component_contributions.csv`](results/component_contributions.csv) and [`constants.csv`](results/constants.csv)
  ([what the parts buy](#what-the-parts-buy)). Two files are new in 2.0.1:
  [`bdg2_micro_load_windows.csv`](results/bdg2_micro_load_windows.csv), the 46 windows the micro-load rule changes,
  one by one, and [`intervals_winkler_contrasts.csv`](results/intervals_winkler_contrasts.csv), the Winkler contrasts
  with their intervals (now for 2.1, 2.0.1 and 2.0.0) ([file list](results/README.md)).
- **Check a number.** Every number of the tables is a row of a file in `results/`. The Cambridge row of the test
  table, for example:

  ```python
  import csv
  rows = [r for r in csv.DictReader(open("results/benchmark_pairwise.csv", encoding="utf-8"))
          if r["set"] == "Cambridge" and r["subset"] == "late"]
  print(sum(float(r["um_high"]) < 0 for r in rows), "of", len(rows))      # 17 of 20 resolved better
  ```
- Two test suites:
  - `python -m unittest discover -s tests -t .` runs the forecaster's tests and those of the evaluation module. The
    forecaster's tests check that no information from after the origin reaches the forecast, the weights, the analog
    shapes or the interval; the handover's limits, the off-state rule and the micro-load rule; the within-day
    anchoring's bounds and invariances, the single trust value of 2.1 and `single_trust=False` giving the 2.0.1 form;
    the readouts; and the reference estimator's documented values;
  - `python -m unittest discover -s theory -t .` runs the 29 checks of the exact properties
    ([theory/](theory/README.md)), with their counterexamples.
- **Integrity hashes.** The hashes in `ankyra/history/provenance.json` and
  `results/ankyra_1x/REPRODUCTION_CHECK.json` were taken on a Windows working copy with CRLF line endings. The
  repository stores LF, so they match a checkout only after its line endings are converted to CRLF.
- [`evaluation/`](evaluation/) holds the scoring behind the result tables (pairwise contrasts with bootstrap
  intervals, ranks, conventional metrics, rank tests, scaled errors). Run on the study's saved forecasts, it
  reproduces the released tables of BDG2, Cambridge, GoiEner households and the Suzhou park. Those forecasts and the
  code of the trained baselines are not in the repository, so the tables cannot be regenerated from the repository
  alone. `python -m evaluation.run_example` shows the data flow on twelve artificial buildings with a stand-in model
  (under a minute); its numbers mean nothing.

## What changed in 2.0, 2.0.1, 2.1 and 2.2

- **2.2: gap tolerance.** In the pseudo-origin bookkeeping only, gaps of at most 6 hours inside one 744-hour block are
  interpolated between their neighbours, and a pseudo-origin's target month qualifies when 90% of its hours are
  observed. Candidates, weights, constants, readouts and the origin context's completeness requirement are unchanged;
  a record without gaps gives the 2.1 forecast bit for bit (`gap_tolerance=False` reproduces 2.1). On the ten
  populations 2.2 differs from 2.1 within ±0.5% hourly (none resolved); on UNICON the completed pseudo-origin pairs
  rise from 0.51 to 3.49 per window; on LCL the hourly error falls by 0.2% (resolved). Every 2.2 number is a
  re-evaluation, not a test ([version history](#version-history)).
- **2.1: one within-day trust value.** The trust on the analog shape is estimated once per window, from sums over the
  four lead blocks, instead of once per block; the shrinkage n/(n+2), the cap ½, the three pseudo-origins and the
  analog shapes are unchanged. Level, daily path, handover, daily means, energy readout and the off-state and
  micro-load rules are bit-identical to 2.0.1; only the within-day block and quantities read from the delivered
  trajectory (hourly errors, ranks, the peak readout, intervals, delivered energy where the projection binds) change.
  Evidence: chosen after all twelve populations had been scored with 2.0.1; non-inferior on all twelve under a margin
  fixed before scoring (hourly error +0.01% to +0.45% against 2.0.1 on all windows, resolved better on Oslo, Drammen
  and HKUST, never resolved worse). Every 2.1 number is a re-evaluation, not a test.
- **Within-day anchoring.** 1.x took the foundation model's within-day shape unchanged, although that block carries
  36–50% of the hourly squared error on buildings. 2.0 lets the unit's own analog days (same calendar type, within
  ±14 days of the same day of year, same daylight-saving state; up to eight, chosen by temperature) correct it, by the
  same error-weighted rule the other blocks use. Level, daily path and energy readout are unchanged, and so is the
  peak readout computed from the pre-projection daily means.
- **Effect** (post-cutoff test windows, 2.0.0 against 1.x, the contrast that isolates the within-day anchoring):
  Cambridge +2.9%, GoiEner non-household +3.8%, BDG2 +0.9%, HEEW +0.8% (all resolved), EWELD +0.4%, households −0.1%
  (not resolved); Oslo +4.2%, Drammen +3.3%, CINELDI +2.0%, Suzhou park +2.9% on all windows (all resolved). No extra
  foundation-model call.
- **2.0.1: micro-load rule.** If all 1,344 hours of the context are within 10⁻³ kW of zero (max |load| ≤ 10⁻³ kW), the
  TimesFM forecast is returned unchanged. This is the same action as the off-state rule, which fires when the last 168
  hours are at most 10⁻⁶ kW ([definition](docs/METHOD.md#off-state-and-micro-load-rules)).
  - **Why this threshold.** It reuses the value of the floor of the normalisation scale; it is not a new constant. A
    record that stays inside that floor for eight weeks is treated as switched off, like a record that reads zero. The
    off-state rule does not catch it, because its readings are small but not zero.
  - **What it corrects.** On the meters that prompted it the context read 0.0002–0.0005 kW, yet 2.0.0 forecast 0.35 kW
    on average. The historical candidates still carried the load of earlier months, and the shrinkage of the weights
    kept them in play, as for a meter that is off.
  - **What it does not do.** It is a sufficient condition chosen after that failure was seen, not a derived boundary: a
    record slightly above the threshold is not covered. It cannot foresee a restart: in 5 of the 46 windows it
    changes, the meter resumed during the forecast month, and there 2.0.0 was marginally better.
  - **Where it acts.** On the ten populations the rule changes 46 windows of nine meters at one BDG2 site (13
    before and 33 after the training cutoff of the trained baselines). On EWELD all 339 micro-load windows are already
    off-state windows, and no window of the other eight populations qualifies. Nine populations are bit-identical
    between 2.0.0 and 2.0.1; only BDG2 changes.
  - **Status.** Written after the BDG2 test result of 2.0.0 had been seen, and not evaluated on any other data (see
    the evidence status below and the BDG2 item under *Where ANKYRA falls behind*).
- **Evidence status.** The 2.0 rule was developed after the test populations had been scored for 1.x, selected on the
  three development populations and on the pre-cutoff windows of the test populations, and evaluated once on the
  post-cutoff windows under a frozen protocol. Those windows had been read before; the 2.0 test numbers are a
  re-evaluation, not a first read ([details](docs/EVALUATION.md#within-day-anchoring-20)). The micro-load rule was
  written after the BDG2 test result of 2.0.0 had been seen, in response to it. Its effect on BDG2 describes what the
  rule changes; it is not a test of the rule. No other scored population has a window on which the rule changes the
  forecast, so the rule has not been evaluated on data it was not written for. It came out of a round of four
  candidates specified after the 2.0.0 evaluation. It was the only one that changed no forecast on the design sets
  other than BDG2; the other three (a block-wise handover, a peak-estimate competition and a spike guard) were not
  adopted. The 2.0.0 results are kept beside the 2.0.1 results ([`results/ankyra_2_0_0/`](results/ankyra_2_0_0/)). LCL
  had not been read in those rounds. It was scored once afterwards, with the frozen 2.0.1
  ([result](#lcl-households-and-two-changes-not-adopted)); it has no micro-load window.
- `forecast(..., gap_tolerance=False)` reproduces 2.1, `forecast(..., gap_tolerance=False, single_trust=False)`
  reproduces 2.0.1, `forecast(..., gap_tolerance=False, single_trust=False, micro_load_rule=False)` reproduces 2.0.0,
  and `forecast(..., gap_tolerance=False, within_anchor=False, micro_load_rule=False)` reproduces 1.x exactly.
  `foundation=None` gives the history-only configuration, a reduced configuration for ablation and offline use; it is
  not a released version. The 2.0.1, 2.0.0 and 1.x result files are kept in
  [`results/ankyra_2_0_1/`](results/ankyra_2_0_1/), [`results/ankyra_2_0_0/`](results/ankyra_2_0_0/) and
  [`results/ankyra_1x/`](results/ankyra_1x/).

## Version history

Each entry describes its release as it was. A switch named in an entry reproduced the earlier version with that
package; with package 2.2.0 add `gap_tolerance=False` (the commands for 2.2.0 are under
[What changed](#what-changed-in-20-201-21-and-22)).

- **2.2.0 (6 October 2026)** — model ANKYRA 2.2: gap tolerance in the pseudo-origin bookkeeping (`ankyra/core.py`
  `fill_short_gaps`, `forecast(..., gap_tolerance=True)`; `ankyra/history/api.py`): gaps of at most 6 hours inside one
  744-hour block are interpolated between their neighbours, and a pseudo-origin's target month qualifies when 90% of
  its hours are observed (its truth is the mean over the observed hours; days with fewer than 12 observed hours leave
  the handover sums). Candidates, weights, constants, readouts and the origin context's completeness requirement are
  unchanged; a record without gaps gives the 2.1 forecast bit for bit (reproduction check v7). New output field
  `anchoring_record` and the table `results/anchoring_gain_deciles.csv` behind it. Result files and figures re-made
  with 2.2, except the files not re-exported for 2.2, whose entries in `results/README.md` name the version they were
  measured on (among them the three carrier-swap files, measured with 2.1); the 2.1 files are in `results/ankyra_2_1/`. On the ten populations 2.2 differs from 2.1 within
  ±0.5% (none resolved); on UNICON the completed pseudo-origins rise from 0.5 to 3.5 per window; on LCL the hourly
  error falls by 0.2% (resolved).
- **Results and documentation after v2.1.0 (6 October 2026; forecaster and package version unchanged, still
  2.1.0)** — HKUST, Helsinki and LCL are presented with ANKYRA 2.1: their result files are re-reads of the same
  targets with 2.1, with the same verdicts; the 2.0.1 files, which were the first scoring, are in
  `results/ankyra_2_0_1/` (`lcl_audit.json` moved there). New external test of the frozen 2.1 on UNICON (La Trobe
  University; 843 windows, 60 units; primary criterion failed, not confirmed;
  [section](#external-test-of-the-frozen-21-unicon)). New [What the parts buy](#what-the-parts-buy):
  `results/component_contributions.csv`, `results/constants.csv` and the comparison of block-wise weighting with one
  whole-window combination weight. Figures 9 and 9b have eleven panels (LCL, HKUST, Helsinki and UNICON added);
  Figure 18 is removed, its content being in Figures 9 and 9b; Figure 17 b, c show HKUST under 2.1.
- **2.1.0 (6 October 2026)** — model ANKYRA 2.1: the within-day trust is estimated as one value per window, pooled
  over the four lead blocks (days 1–7, 8–14, 15–21, 22–31), instead of one value per block (`ankyra/analog.py`,
  `within_trust(..., single=True)`; `forecast(..., single_trust=True)`). Shrinkage n/(n+2), cap ½, three pseudo-origins
  and analog shapes unchanged; level, daily path, handover, daily means, energy readout (744 × level), off-state and
  micro-load rules bit-identical to 2.0.1. `forecast(..., single_trust=False)` reproduces 2.0.1 (with
  `micro_load_rule=False` as well, 2.0.0); the output field `within_trust` now holds one value repeated four times.
  Evidence: the change was chosen after all twelve populations had been scored with 2.0.1, in a simplification study
  whose non-inferiority criterion was fixed before scoring; one trust value was non-inferior on all twelve (hourly
  error +0.01% to +0.45% against 2.0.1 on all windows, resolved better on Oslo, Drammen and HKUST, never resolved
  worse; largest upper end +0.0048 log units). Every 2.1 number is a re-evaluation of data read before, not a test.
  Results and figures re-exported for 2.1; the 2.0.1 result files kept in `results/ankyra_2_0_1/`; the frozen-model
  checks (HKUST, Helsinki, LCL) keep their 2.0.1 results as the tests, with 2.1 re-evaluations in
  `results/reevaluation_2_1.json`; two tests added; reproduction check re-run on package 2.1.0 (PASS,
  `results/REPRODUCTION_CHECK.json`).
- **2.0.3 (5 October 2026)** — documentation and records only; the code is that of 2.0.2 and every forecast is
  identical. The reproduction check was re-run on the current code (`results/REPRODUCTION_CHECK.json`; the record of
  the 2.0.1 package is kept as `results/REPRODUCTION_CHECK_2_0_1.json`). Version statement, data licences
  ([docs/DATA.md](docs/DATA.md#what-is-and-is-not-in-this-repository)), the framing of the frozen-model checks and the
  peak-readout statement (pre-projection daily means) corrected.
- **2.0.2 (5 October 2026)** — input-contract fix: a load value marked `observed=False` reached the foundation-model
  contexts, the off-state and micro-load rules and the analog days, while the historical estimator ignored it, so a
  finite placeholder at an unobserved hour could change the forecast. `forecast()` now masks the record once and every
  part reads the same masked record; a malformed mask is rejected. New test
  `test_values_at_unobserved_hours_do_not_reach_the_forecast`. Forecasts are unchanged whenever `observed` is omitted or
  equals the finite values, as in every evaluation of the study; the reproduction check gives the same numbers as for
  2.0.1. HKUST: the temperature scale is now fitted on the days before the first origin (it had included 24 hours after
  the origin of four windows); every HKUST forecast was recomputed, `results/hkust_*`, `results/carrier_swap_*` and
  the figures come from the recomputed forecasts, and no decision changed (largest change 0.001 percentage points).
- **Post-hoc exploration (5 October 2026; forecaster unchanged)** — ANKYRA anchored to the covariate-informed
  Chronos-2-X on twelve populations, with no criterion fixed in advance; with TimesFM and Chronos-2, two
  foundation-model families in three configurations on the same windows (`results/carrier_swap_x.csv`,
  `results/carrier_swap_combined.csv`;
  [docs/FROZEN_MODEL_CHECKS.md](docs/FROZEN_MODEL_CHECKS.md#a-post-hoc-exploration-ankyra-anchored-to-chronos-2-x)).
- **Pre-registered confirmation test (5 October 2026; forecaster unchanged)** — Helsinki city service buildings,
  201 units, scored with the frozen 2.0.1: monthly energy vs TimesFM +6.0%, interval crosses zero (primary criterion failed); hourly +4.3%, not
  resolved (secondary passed); ANKYRA's errors resolvably higher than Chronos-2-X's on both. Not confirmed
  ([docs/FROZEN_MODEL_CHECKS.md](docs/FROZEN_MODEL_CHECKS.md#a-pre-registered-confirmation-test-helsinki)).
- **HKUST comparators added (4–5 October 2026; forecaster unchanged)** — Chronos-2-X and TimesFM-X, then Holt-Winters,
  MSTL and the zero-shot GBT, scored against the frozen ANKYRA forecasts; per-day curves (`results/hkust_by_day.csv`,
  now the HKUST panel of Figures 9 and 9b).
- **Two checks with the forecaster frozen (4 October 2026; forecaster unchanged)** — with Chronos-2 in place of TimesFM,
  anchoring improves the foundation model resolvably on seven of ten populations and is never resolvably worse; on
  a campus dataset never used before (HKUST, 33 units, 134 windows) monthly energy error is 38% below TimesFM's and
  the hourly gain of 8% is borderline ([docs/FROZEN_MODEL_CHECKS.md](docs/FROZEN_MODEL_CHECKS.md),
  `results/carrier_swap.csv`, `results/hkust_first_read.csv`).
- **After the `v2.0.1` tag (4 October 2026; forecaster unchanged)** — LCL households scored once with the frozen 2.0.1
  forecaster (`results/lcl_*`), and two further changes examined and not adopted
  ([docs/LCL_AND_CLOSEOUT.md](docs/LCL_AND_CLOSEOUT.md), `results/closeout_status.json`); sources and preparation of the
  data ([docs/DATA.md](docs/DATA.md)); the scoring module [`evaluation/`](evaluation/) with a runnable example and its
  tests. The tag `v2.0.1` marks the forecaster; these files were added after it.
- **2.0.1 (3 October 2026)** — micro-load rule (`ankyra/core.py`, `MICRO_KW = 1e-3`): a context whose 1,344 hours all
  stay within 10⁻³ kW of zero is handed to the foundation model, as the off-state rule does for a unit that is off;
  `micro_load_rule` argument (`False` reproduces 2.0.0; with `within_anchor=False` as well, 1.x) and `micro_load` output
  field. On the ten scored populations the rule changes 46 windows of nine BDG2 meters; the other nine populations are
  bit-identical. The rule was written after the BDG2 test result of 2.0.0 had been seen: its effect there describes what
  it changes and is not a test of it. It was one of four candidates of a round specified after the 2.0.0 evaluation; the
  other three were not adopted. Results, figures and documents re-exported for 2.0.1; the 2.0.0 files kept in
  `results/ankyra_2_0_0/`; new result files `bdg2_micro_load_windows.csv` and `intervals_winkler_contrasts.csv`; 10
  tests of the rule. Figure numbering swapped back: Figure 9 is again the hourly loss by forecast day, and the energy
  figure, which the 2.0.0 addenda had made Figure 9, is Figure 9b; both are shown in this README.
- **2.0.0, results addenda (3 October 2026; forecaster unchanged)** — energy error by forecast day (Figure 9; the hourly
  loss by day is now Figure 9b), block attribution (14), rank tests (15), intervals on ten populations (16), scaled
  errors, history length, robustness to corrupted contexts, sensitivity to the constants; the lead-week file recomputed
  for 2.0; the shared information set tabulated in this README.
- **2.0.0 (2 October 2026)** — within-day anchoring (`ankyra/analog.py`): the unit's analog-day shape competes with the
  foundation model's shape, weighted by the unit's pseudo-origin errors; `dst_region` input; history-only configuration
  (`foundation=None`); `within_anchor=False` for 1.x. Results, figures and documents re-exported for 2.0; the 1.x files
  kept in `results/ankyra_1x/`. Test evidence of the new block: a frozen-protocol re-evaluation of the post-cutoff test
  windows, not a first read.
- **1.2.1 (29 September 2026)** — corrected GBT-T baseline, results and figures re-exported, deterministic figure
  output.
- **1.2.0 (29 September 2026)** — exact properties in `theory/`, loss metrics, loss by forecast day, monthly energy
  error, consistency and intervals (figures 8–13).
- **1.1.1 (29 September 2026)** — handover granularity ablation, cost per window, BDG2 sensitivity.
- **1.1.0 (29 September 2026)** — exact properties P1–P19 as tested operators, no-future-information tests, Figure 7.
- **1.0.0 (29 September 2026)** — reference implementation, test-set benchmark, figures and documentation.

## License and acknowledgements

The code is released under the MIT license. TimesFM 2.5 is © Google (Apache-2.0) and is not redistributed. The
evaluation used public datasets from GoiEner, the COFACTOR projects (Drammen, Oslo), EWELD, the University of Cambridge
estate archive, CINELDI, HEEW, the Building Data Genome Project 2, the Suzhou industrial-park dataset and the London
Low Carbon London project; see [docs/EVALUATION.md](docs/EVALUATION.md) for references. The external test used
UNICON (La Trobe University; CC BY-NC-SA 4.0, research use only), which is not redistributed. The example window in `results/`
is from the University of Cambridge estate archive (CC BY 4.0).

To cite the software, use [CITATION.cff](CITATION.cff) (package 2.2.0, tag `v2.2.0`); an archive DOI has not been
assigned yet.

Questions and bug reports: the [issue tracker](https://github.com/XinanQ/Building_load_ANKYRA/issues).
