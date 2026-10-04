# ANKYRA

**Month-ahead hourly load forecasts that anchor a time-series foundation model to each unit's own history**

[中文说明](README.zh-CN.md) · [Install and run](#install-and-run) · [Your own data](#forecast-your-own-unit) · [Method](docs/METHOD.md) · [Theory](theory/) · [Evaluation](docs/EVALUATION.md) · [Data](docs/DATA.md) · [Scoring code](evaluation/) · [Results data](results/)

ANKYRA forecasts the hourly electricity load of one unit (a building, a meter or a supply point) for the next 31 days
(744 hours); it is meant for researchers and practitioners who need month-ahead load or energy forecasts for many units
without training a model on each of them. It combines the zero-shot forecast of a pretrained foundation model,
TimesFM 2.5, with estimates from the unit's own past load, outdoor temperature and calendar, and weights the two by how
well each has forecast the unit's own earlier months.

Current version: **2.0.1** ([what changed](#what-changed-in-20-and-201) · [version history](#version-history)).

![ANKYRA architecture](figures/fig1_architecture.png)

*Figure 1. Architecture.*

Pretrained time-series foundation models reproduce the shape of a day well, but over a 31-day horizon their monthly
level follows the last few days and drifts. A unit's own history anchors the month, but reacts slowly and cannot
represent a load that has switched off. **ANKYRA** (Greek *ἄγκυρα*, anchor) uses each source where it is reliable, and
lets the unit's own forecast record decide where that is. The terms used below (pseudo-origin, block, handover and
others) are defined in [Terms used on this page](#terms-used-on-this-page).

- A 744-hour forecast splits exactly into a **level**, a **centred daily path** and a **within-day shape**. The blocks are
  orthogonal, so their squared errors add.
- The level and daily path come from six historical candidates plus the foundation model's own level. Each unit's
  errors at earlier pseudo-origins weight them, and the **same errors decide how much of the month to hand over** to
  the foundation model.
- The within-day shape starts from **TimesFM 2.5** (zero-shot). Since **2.0** it is anchored too: the unit's own
  analog-day shape competes with the model's, with a weight set by the unit's errors at three completed pseudo-origins,
  shrunk towards the model and capped at one half. All three blocks are now anchored the same way.
- A unit that has been **off for a week** is handed to the foundation model entirely. Since **2.0.1** so is a unit
  whose whole 1,344-hour context stays within 10⁻³ kW of zero: a record that stays inside the floor of the
  normalisation scale for eight weeks is treated as switched off.
- **Nothing is trained on the target series.** Every weight is a function of the unit's completed pseudo-forecasts.
- Three **readout operators** reuse the same computation:
  - energy from the level;
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
  [LCL households and two changes not adopted](#lcl-households-and-two-changes-not-adopted)
- **How it works:** [Handover](#how-the-handover-works) · [Within-day anchoring](#within-day-anchoring-20) ·
  [Readouts](#readouts-peak-and-prediction-interval) · [Theory](#theory-exact-properties)
- **Check it:** [Reproducibility](#reproducibility) · [What changed in 2.0 and 2.0.1](#what-changed-in-20-and-201) ·
  [Version history](#version-history) · [License and acknowledgements](#license-and-acknowledgements)

## What is in this repository

```
ankyra/              the forecaster
  core.py            forecast(): model level candidate, week-by-week handover, within-day anchoring, off-state and
                     micro-load rules
  analog.py          analog-day shapes and the error-weighted within-day trust (2.0)
  history/           frozen reference estimator of the historical level and daily path
  readouts.py        energy, peak envelope operator, pseudo-origin interval
  blocks.py          orthogonal block decomposition
  metrics.py         unit-equal log RMS ratio, unit-and-month bootstrap, mean per-unit rank, pooled decomposition
  synthetic.py       artificial building history and stand-in forecaster for the quickstart and the tests
  timesfm_adapter.py TimesFM 2.5 as configured in the study
examples/            quickstart on an artificial building
tests/               tests of the forecaster, including the no-future-information tests, and of the evaluation module
theory/              the exact properties P1–P19, apart from the forecaster
  README.md          index: condition, use, code and check of each property
  PROOFS.md          statements, proofs, counterexamples and measured consequences
  operators.py       the properties as operators (replacement, support, shrinkage, projection, peak)
  test_operators.py  numerical checks, counterexamples included
evaluation/          scoring of a population from forecasts and realised load; a runnable example
results/             scored statistics (CSV / JSON) and the reproduction record; 2.0.0 and 1.x in subfolders
figures/             make_figures.py and the figures (PDF and PNG)
docs/                METHOD.md (equations and constants), EVALUATION.md (protocol and full tables),
                     DATA.md (sources and preparation), LCL_AND_CLOSEOUT.md (LCL households; two changes not adopted)
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
grid first: the forecaster does no resampling, no gap filling and no time-zone or daylight-saving conversion
([details](docs/DATA.md#the-input-format-the-forecaster-expects)). An input that breaks the contract below raises an
error; nothing is repaired silently.

### The inputs

The record, `ankyra.History`:

| Input | What to supply |
|---|---|
| `load_kw` | Hourly mean load in kW (the off-state and micro-load thresholds are absolute values in kW). Index 0 is 1 January 00:00 of the year in which the record starts; the last value is the hour before the forecast starts. The last 1,344 hours must be complete; earlier gaps are NaN. A record that starts later in the year is padded back to 1 January with NaN. Aggregate sub-hourly readings first (four 15-minute kWh readings sum to the hour's mean kW). |
| `temperature_c` | Hourly outdoor air temperature in °C for the same hours, finite everywhere, the padded hours included. The annual temperature harmonic is fitted on all of them, so use archive temperature for the padded hours if you can; a fixed value there also runs (the study's LCL preparation used 15 °C). Where load is observed the series must vary: if the daily mean temperature is constant over a year, the temperature signature cannot be fitted and `forecast` raises an error. A nearby weather station or a reanalysis series is enough. No future temperature is needed. |
| `day_types` | One integer per hour for the history plus the 744 forecast hours (length `len(load_kw) + 744`, integer dtype): Monday = 0 … Sunday = 6 from the date, 7 on a public holiday; constant within each day. |
| `start_timestamp` | The time of index 0. It must be 1 January 00:00 written with a `+00:00` offset (or `Z`), for example `"2019-01-01T00:00:00+00:00"`. The offset is a label and no conversion is made: use a fixed-offset grid (UTC or local standard time, without daylight-saving jumps). |
| `observed` (optional) | Boolean mask of the load. Default: the finite values. |

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
  3. take the standard deviation of that anomaly, pooled over the units of the population, on the first 244 days of
     the record (15 days are dropped at each end).

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
  ([definition](docs/METHOD.md#off-state-and-micro-load-rules)). `False` reproduces the 2.0.0 forecast.
- `within_anchor` (default `True`): the within-day anchoring of 2.0. `within_anchor=False` together with
  `micro_load_rule=False` reproduces the 1.x forecast.

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
| `within_day_trust_on_analog_shape` | `within_trust` | The weight on the unit's own analog-day shape in the same four parts of the month, between 0 and ½. 0 leaves the foundation model's shape. |
| `within_day_pseudo_origin_triples` | `within_pseudo_pairs` | The number of completed pseudo-origins behind the trust (at most 3). |
| `analog_shape_kept` | `analog_kept` | `False` when the analog shape was implausibly large (more than three times the largest context value) and the model's shape was used for the whole window. |
| `off_state`, `micro_load` | same names | `True` when the off-state or the micro-load rule fired. The foundation model's forecast is then returned unchanged, without setting negative hours to zero. |

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
  0.11 s on the same machine, within the benchmark's run-to-run spread.
- **Once per session.** Loading TimesFM takes 2.3 s. The interval readout, when requested, adds 0.56 s per window.

Full timings are in [`results/cost_per_window.csv`](results/cost_per_window.csv) and
[docs/EVALUATION.md](docs/EVALUATION.md#cost).

### When not to use it

Use ANKYRA for hourly, month-ahead forecasts of buildings and non-household supply points with two or more years of
history, above all when the monthly energy or the later weeks of the month matter. On the evidence of this page it is
not the better choice in these cases:

- **Households.** On GoiEner households zero-shot TimesFM has the lower hourly error (3.9%, resolved); on LCL
  households the two are not separated. ANKYRA's monthly energy error is still lower.
- **The first days of the month.** On day 1 the zero-shot foundation models are lower on every population.
- **Less than two years of history.** ANKYRA is not separated from TimesFM alone.
- **Buildings ruled by closure days.** On Norwegian schools a trained cross-unit model with calendar features is
  12.8% better.
- **A context with a single large spike.** The hourly error rises and the peak readout, which takes the largest
  recent excursion, is ruined.
- **Units that switch off.** The prediction interval should not be used for them; its width explodes.
- **Data that are not hourly, or not in kW.** The off-state and micro-load thresholds are absolute values in kW.
- **Sites in the southern hemisphere.** The annual temperature harmonic has a fixed phase, with its coldest day in
  January, and a nonnegative amplitude. Every evaluated population is in the northern hemisphere.

The evidence for the first six points is in the results sections below. The last two follow from the code.

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
- **Trust**: the weight on the unit's own analog-day shape in the within-day block, between 0 and ½.
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
([below](#lcl-households-and-two-changes-not-adopted)). The three *development populations* on which rules were
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
were scored **once, after the model had been fixed**, for 1.x; the numbers below are those of 2.0.1. On five
populations they are identical to the 2.0.0 numbers, the re-evaluation described above. The BDG2 row (†) also includes
the micro-load rule, which was written after that population's 2.0.0 result had been seen.

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
| GoiEner households | Spain | 696 / 696 | 16 | 3 | TimesFM (3.9%) | 2 |

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
- Its only resolved deficit on a test population is against zero-shot **TimesFM on households** (3.9%), where the
  within-day anchoring does not act.
- Mean per-unit rank over the six populations: **5.49** (2.0.0: 5.51; 1.x: 6.00). Next are the per-unit ridge (7.30),
  Chronos-2-X (7.84) and iTransformer-X (8.17).

![Test-set ranks and head-to-head](figures/fig2_test_ranks.png)

*Figure 2. Test-set ranks and head-to-head comparison.*

![Pairwise improvements with intervals](figures/fig3_test_pairwise.png)

*Figure 3. Pairwise improvements with intervals.*

**Loss metrics against every baseline.** The figure below gives the conventional losses of all 21 forecasters on the
same late windows, for the six test populations and the Suzhou industrial park (a preview population with four
aggregate series). The ordering depends on the metric:

- **RMSE** (mean over units): ANKYRA is lowest on BDG2 and the Suzhou park and second on the other five. The lower
  ones are iTransformer-X (Cambridge), GBT-T (HEEW), Chronos-2 (EWELD), Chronos-2-X (GoiEner non-household) and the
  per-unit ridge (households, by 0.1%).
- **MAE and WAPE** are minimised by the median of the predictive distribution, squared-error metrics by its mean. On
  them, zero-shot Chronos-2 or TimesFM variants are lower than ANKYRA on EWELD and on both GoiEner populations, where
  ANKYRA ranks second to fifth.
- **CV(RMSE) at the median unit**: ANKYRA is lowest on EWELD and second on the other six.
- Across the four metrics and seven populations ANKYRA ranks between first and fifth of 21, and no baseline is lower on
  all of them. These metrics weight units differently from the primary estimand
  ([details](docs/EVALUATION.md#loss-metrics-of-every-forecaster)).

![Loss metrics of all 21 forecasters](figures/fig8_loss_metrics.png)

*Figure 8. Loss metrics of all 21 forecasters.*

**Loss by forecast day.** Figure 9 below shows the error of the hourly load forecast. It splits the same late-window
forecasts of all 21 forecasters by forecast day, 1 to 31. The loss is each day's CV(RMSE) over its 24 hours, averaged
geometrically over a fixed set of units, the scale of the primary estimand. The split was made after scoring; it is a
description.

- On every forecast day of every population in the figure ANKYRA is among the six forecasters with the lowest loss
  of 21. It is the lowest on 9 of the 31 days on BDG2, 16 on Cambridge, 12 on HEEW and 13 on the Suzhou park, but
  only on 2 on EWELD and on none on the two GoiEner populations.
- **The zero-shot foundation models are lower in the first days.** On day 1 TimesFM and Chronos-2 are below ANKYRA on
  every population, and ANKYRA ranks third to fifth of 21. On BDG2, HEEW and the Suzhou park at least two of the four
  zero-shot variants stay below it through day 3.
- From the second week ANKYRA is lowest or second-lowest on 17–21 of the 24 days on BDG2, Cambridge, HEEW and the
  Suzhou park, and on 8 on EWELD. From the first week (days 1–7) to the fourth (days 22–31) its loss grows by
  ×1.19–1.55, less than TimesFM's (×1.24–1.68) and Chronos-2's (×1.25–1.80) on all seven populations.
- On GoiEner households all four zero-shot variants are lower on every day. On GoiEner non-household ANKYRA is below
  TimesFM on 19 days, but Chronos-2-X is lower on every day and Chronos-2 on 27. On EWELD at least one variant is
  lower on 29 days.
- The hourly error is dominated by the within-day shape, which is still mostly the foundation model's. The micro-load
  rule moves the BDG2 curve by at most 0.012 points on any day. The curves use a fixed set of units whose daily errors
  are nonzero for all 21 forecasters (132 of 142 on BDG2), and the three meters that are near zero in every window are
  not in it. The day-by-day comparison, the same curves relative to ANKYRA ([Figure 10](figures/fig10_loss_by_day_relative.png)) and the exact relation to the
  monthly estimand are in [docs/EVALUATION.md](docs/EVALUATION.md#loss-by-forecast-day).

![Loss by forecast day](figures/fig9_loss_by_day.png)

*Figure 9. Hourly loss by forecast day.*

**Energy as the month accumulates.** Figure 9b below shows the error of the energy, for the same forecasts. It follows
the error of the energy delivered through each forecast day (the mean load over days 1 to *d*), averaged geometrically
over a fixed set of units. This is the quantity ANKYRA's level and daily path act on, and day 31 is the monthly energy
error. Like Figure 9, it was computed after scoring, as a description.

- **ANKYRA has the lowest error of the 21 forecasters** on 29 of the 31 days on GoiEner non-household, 25 on BDG2,
  20 on EWELD, 19 on Cambridge and 18 on HEEW. At day 31 it is first on four of the six test populations (GoiEner
  non-household 11.5% against 13.1% for the next forecaster; BDG2, HEEW, EWELD) and second on Cambridge.
- **From the second week it is below all four zero-shot foundation-model variants** on every day on Cambridge and on
  both GoiEner populations, and on 18–22 of the 24 days on BDG2, HEEW and EWELD.
- **The error still grows on the building populations.** The foundation models' energy error grows as their level
  drifts: from the first week (days 1–7) to the fourth (days 22–31) TimesFM's and Chronos-2's grow by 51–72% on BDG2,
  Cambridge and HEEW and by 18–38% on EWELD and the two GoiEner populations. ANKYRA's grows too, by 33–37% on BDG2,
  Cambridge and HEEW and by 11% on EWELD. It stays flat only on the two GoiEner populations (+5% and 0%).
- On GoiEner households ANKYRA's energy error (11.7% at day 31) is a quarter to a third below the four
  foundation-model variants' (15.5–17.4%), but the per-unit ridge, three profile or naive forecasters and the LSTM are
  lower still (10.0–11.4%), so it ranks sixth there. On the Suzhou park (four series) covariate-conditioned TimesFM is
  lower from day 2 on.
- **The two figures answer different questions and do not conflict.** Figure 9 is the error of the hourly load, where
  the foundation models lead in the first days, and on most days on EWELD and the Spanish populations. Figure 9b is
  the error of the accumulated energy, where the historical anchor acts: from the second week ANKYRA is below the
  zero-shot variants on most days on all six test populations
  ([details](docs/EVALUATION.md#energy-as-the-month-accumulates)).

![Energy error as the month accumulates](figures/fig9b_energy_by_day.png)

*Figure 9b. Energy error as the month accumulates.*

**Where ANKYRA is strongest: monthly energy.** A month's energy error is 744 times the level error ([P3](theory/README.md)). ANKYRA's
design acts on that quantity: its level and daily path come from the unit's own history, while its within-day shape
starts from TimesFM's.

- On all seven populations ANKYRA is never resolvably worse than any of the 20 baselines on monthly energy error. It is
  resolvably better than 6–17 of them: 17 on GoiEner non-household, 14 on Cambridge, EWELD and BDG2, 11 on households.
  The BDG2 count includes the micro-load rule: it was 4 under 2.0.0, and without the three near-zero meters it is 6
  (5 under 2.0.0).
- On GoiEner households, where the zero-shot foundation models have the lower hourly error on every day, ANKYRA's
  monthly energy error is 22–27% lower than all four of them, each resolved.
- Against TimesFM, whose within-day shape it uses, the energy error is 4–25% lower on all seven populations, resolved
  on Cambridge and both GoiEner sets. On BDG2 it is 12% lower, not resolved, with or without the three near-zero
  meters; under 2.0.0 those meters made it 38.7% higher.
- The energy comparison was computed after scoring, as a description
  ([details](docs/EVALUATION.md#monthly-energy-error)).

![Monthly energy error against every baseline](figures/fig11_energy_error.png)

*Figure 11. Monthly energy error against every baseline.*

**Consistency across populations.** ANKYRA 2.0.1 is first of the 21 forecasters on five of the six test populations
and second on households. No other forecaster is in the top two on more than two of them. On the four preview
populations it is 1st (CINELDI), 1st (Suzhou park), 2nd (Drammen) and 3rd (Oslo); 1.x was 3rd, 1st, 7th and 5th.
Positions use the mean per-unit rank, the secondary summary.

![Position on every population](figures/fig12_consistency.png)

*Figure 12. Position on every population.*

**Rank tests.** The standard tests of the forecasting literature agree. On per-unit RMSE over the 1,762 units of the
six test populations, Friedman's test rejects equal ranks; ANKYRA's mean rank (6.04) is separated from every other
forecaster's by more than the Nemenyi critical difference (0.75; the next is the per-unit ridge at 7.07), and
Holm-corrected Wilcoxon tests put it ahead of all 20. Per population it is significantly better than 17–20 of the 20
baselines on the test populations. Three baselines are significantly better somewhere: the per-unit ridge on
households, GBT-T on Oslo and Chronos-2-X on Drammen ([details](docs/EVALUATION.md#rank-significance-tests)).

![Rank tests](figures/fig15_rank_tests.png)

*Figure 15. Rank tests.*

**Where the error sits.** Because the three blocks are orthogonal, each forecast's hourly MSE splits exactly into its
level, daily-path and within-day parts. On the late windows the within-day block carries 33–48% of the median unit's
error on the building populations (38% on EWELD) and 80–85% on the Spanish populations; ANKYRA's gain over TimesFM comes from the
level on every population, from the daily path on the buildings, and in 2.0 also from the within-day block
(`results/block_shares.csv`, Figure 14). On BDG2 the block contrasts with TimesFM include the micro-load rule (level
+11.9%, daily path +0.6%, within-day +1.4%); under 2.0.0 the near-zero meters made them −38.7%, −52.4% and +9.1%, so
for BDG2 the statement holds only with the rule.

![Block attribution](figures/fig14_block_attribution.png)

*Figure 14. Block attribution.*

**Where ANKYRA falls behind.** We report these as findings, not footnotes.

- **Norwegian schools** (Oslo; a preview population). GBT-T, a cross-unit trained model with calendar features, is
  still better, by 12.8% (1.x: 18%); iTransformer-X's lead (4.4%) is no longer resolved. On Drammen no model is
  resolvably better than 2.0.
  - Diagnostics point to the **activity level of individual days** (holidays, closure-like days, bridge days) rather
    than to the shape of the day.
  - Closure-like days are shared across units and recur from year to year.
  - The diagnosis rests on an oracle bound and on correlations. It narrows down the cause but does not identify the
    operating reasons.
- **Households.** Zero-shot TimesFM is better (see above). The within-day anchoring finds no reliable analog-day
  signal there (mean trust 0.08) and leaves the forecast as in 1.x.
  By per-unit rank the per-unit ridge is ahead of ANKYRA there, significantly so in a paired test; by block, the
  deficit to TimesFM sits in the daily path (−9%), not in the within-day shape.
- **Short histories.** With less than two years of history ANKYRA is not separated from the foundation model alone
  (−0.8% and +2.0% in the two shortest strata, pooled over ten populations, neither resolved; the second was −1.4%
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
  cutoff). Improvement of ANKYRA over each model on the late windows (474 windows, 142 units; last column: 464
  windows, 139 units; positive = ANKYRA better; * = the 95% interval excludes zero):

  | Against | 2.0.0 | 2.0.1 | 2.0.1 without the three near-zero meters |
  |---|---:|---:|---:|
  | TimesFM | −53.4% | +2.5% | +2.5% |
  | Chronos-2 | −54.9% | +1.5% | +6.8% |
  | Chronos-2-X | −38.3% | +12.0% | −2.1% |
  | MSTL | −86.4% | −18.6% | +18.7% |
  | previous-month profile | −90.3% | −21.1% | +23.2% |
  | TimesFM-X | +6.5% | +40.5% * | +6.8% * |
  | iTransformer-X | +4.4% | +39.2% * | +11.8% * (resolved only under 2.0.1) |
  | GBT-T | +15.9% * | +46.5% * | +8.8% |
  | TiDE | +14.4% * | +45.6% * | +10.3% * |
  | per-unit ridge | +9.3% * | +42.3% * | +6.7% * |
  | resolved better than (of 20) | 10 | 15 | 14 (2.0.0: 11) |
  | resolved worse than | none | none | none |
  | position by mean per-unit rank | 1 | 1 | 1 |

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
    against 2.0.0 is +36.4% on the late windows, with an interval of [−1.323, +0.000] in log units (its upper end is
    at zero: not resolved), and +30.4% [−1.230, −0.001] on all windows. The BDG2 unit means are still dominated by
    three meters.
  - Rank-based summaries barely move: ANKYRA ranks first on BDG2 in every column, the pooled mean rank of the rank
    tests is 6.04 in both versions, and the six-population mean of the mean unit ranks goes from 5.51 to 5.49.
  - The 2.0.0 results are kept in [`results/ankyra_2_0_0/`](results/ankyra_2_0_0/); both versions, with and without
    the three meters, are in [`results/bdg2_near_zero_sensitivity.csv`](results/bdg2_near_zero_sensitivity.csv)
    ([details](docs/EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)).
- **Conventional metrics.** Over the full windows (14 forecasters), Chronos-2-X or the per-unit ridge has a slightly
  lower median unit CV(RMSE) (by 0.4–2.0 points) on four of ten populations (BDG2, EWELD, households, Oslo); 1.x was
  behind on nine of eleven populations. The late-window losses of all 21 forecasters are in the figure above.

Full tables for the ten populations and the evaluation protocol are in [docs/EVALUATION.md](docs/EVALUATION.md).

## LCL households and two changes not adopted

**Low Carbon London households (LCL, UK).** LCL was held out of the ten-population comparison. It was scored once
with the frozen 2.0.1 forecaster, without retuning: 1,215 windows of 965 households, 710 of them late. Its 1.x result
had been seen earlier, so LCL is not an unexposed population. Its numbers are not pooled into the tables above.

- Against 1.x on the same inputs, 2.0.1 is 0.7% better on all windows and 0.9% better on the late windows, both
  resolved.
- Against TimesFM it is +1.2% on all windows and +1.3% on the late windows, neither resolved. The contrasts with
  Chronos-2, Chronos-2-X and TimesFM-X (+1.0% to +1.5%) are not resolved either.
- By mean per-unit rank on the late windows it is first of 21 (6.25; the per-unit ridge is next at 6.48). The
  contrast with the ridge is resolved on all windows (+1.9%) but not on the late windows (+1.2%).
- No same-information baseline, and not the per-unit ridge, is significantly better than ANKYRA (six one-sided tests
  with Holm correction). This does not show that ANKYRA is better than each of them.
- Two windows are off-state windows and none is a micro-load window, so LCL is not a test of the micro-load rule.
  The prediction interval was not scored on LCL for 2.0.1.

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
- ANKYRA 2.0.1 improves on the fixed division on nine of the ten populations, each resolved: by 3.3–26.4% on
  eight, and on BDG2 by 36.5% with the micro-load rule (8.7% under 2.0.0). It is not resolvably different on the
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
  [status](#what-changed-in-20-and-201)).

![Ablation, handover granularity and lead-week profile](figures/fig4_handover_and_ablation.png)

*Figure 4. Ablation, handover granularity and lead-week profile.*

## Within-day anchoring (2.0)

The within-day shape is where the foundation model is strongest, and where 1.x added nothing. 2.0 gives the unit's
own history a say there, by the rule the other blocks already use:

- **Analog days.** For each horizon day, the unit's complete past days of the same calendar type within ±14 days of
  the same day of year and in the same daylight-saving state; up to eight, the closest in daily-mean temperature to
  the day's climatology. Their shapes, each divided by the scale of the 744 hours before it, are averaged and rescaled
  to the origin.
- **Trust.** $w=w^T+\omega_k\,(S-w^T)$ per lead block of the month, with $\omega_k$ the least-squares weight of the
  analog shape against the model's shape on the unit's three completed pseudo-origin windows, clipped to $[0,1]$,
  shrunk towards zero by $n/(n+2)$ and capped at ½. No evidence means the model's shape, i.e. the 1.x forecast.
- **What it leaves untouched.** Both shapes have zero daily means: level, daily path, energy readout and peak readout
  are identical to 1.x. The three pseudo-origin forecasts are among the six ANKYRA already computes. The micro-load
  windows of 2.0.1 are a different matter: there the whole trajectory is TimesFM's.
- **Where it acts.** On buildings with fixed schedules nearly every window is anchored (mean trust 0.20–0.33) and the
  hourly error falls by 0.8–4.2% (2.0.0 against 1.x), growing with lead time; on households the trust stays near zero
  (0.08) and the forecast is unchanged.
- **How it was chosen, and how strong the evidence is.** The rule is the sixth version of a similar-day idea. The first
  four did not meet their no-harm criterion on the development data, and the fifth did not meet it on the test
  populations. The sixth was selected from a family written down in advance, on nine design sets (three development
  populations and the pre-cutoff windows of the six test populations), validated on CINELDI and the Suzhou park, and
  evaluated once on the post-cutoff test windows under a frozen protocol. A further round that tried six
  pseudo-origins, an analog daily-path candidate and finer handover blocks adopted nothing. The full account, with the
  criteria and their values, is in [docs/EVALUATION.md](docs/EVALUATION.md#within-day-anchoring-20).

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

- Against the maximum of the same trajectory, it reduces peak error by **18–65% on all ten populations**.
- Against last month's observed peak, it is better on regularly operated buildings (Drammen, Oslo, HEEW: 12–16%) and
  worse on CINELDI's industrial customers and on EWELD.

![Peak operator](figures/fig5_peak_operator.png)

*Figure 5. Peak operator.*

### Prediction intervals

On GoiEner households the pseudo-origin interval around ANKYRA covers **79.4%** of hours at
the nominal 80% level and 88.2% at 90%. It is the only interval close to its nominal level: TimesFM's native 0.1–0.9
band covers 36.1% and Chronos-2's native 80% band 68.8%. On the Winkler score the ANKYRA interval beats TimesFM's band by
7.5% and the same interval around the fixed division by 4.4%, both resolved. It ties with Chronos-2's band (0.5%
behind, unresolved). Intervals were scored on this one population.

![Prediction intervals on households](figures/fig13_intervals.png)

*Figure 13. Prediction intervals on households.*

Applied afterwards to all ten populations, the same interval covers **75.6–82.2%** of hours at the nominal 80%
level and 84.5–89.1% at 90%, against 65–79% for Chronos-2's native 80% band and 35–57% for TimesFM's. It is not sharper
than Chronos-2's quantiles: on the Winkler score ANKYRA is resolvably better than TimesFM's band on eight populations
(in both versions) but not separated from Chronos-2's on six and resolvably worse on four (HEEW, EWELD, GoiEner
non-household and CINELDI). Under 2.0.0 it was resolvably worse on five: BDG2 sat just beyond the boundary and now sits
just inside it ([`results/intervals_winkler_contrasts.csv`](results/intervals_winkler_contrasts.csv)). Its coverage
also falls with lead time (first week 80–87%, fourth week 72–79%), because the residuals are pooled over the whole
window, and it should not be used for units that switch off, where its width explodes
([details](docs/EVALUATION.md#readouts)).

![Interval coverage on ten populations](figures/fig16_intervals_ten_populations.png)

*Figure 16. Interval coverage on ten populations.*

## Theory: exact properties

![Exact properties on a test window](figures/fig7_operators.png)

*Figure 7. Exact properties on a test window.*

The construction is auditable because each step has a stated property. These mathematical contributions sit beside the
forecaster in their own folder, [theory/](theory/), which the forecaster does not import:

- [theory/README.md](theory/README.md) lists P1–P19 with the condition under which each holds, what ANKYRA uses it for,
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

Each is written as a function in `theory/operators.py` or carried by the forecaster's own functions (P1, P3, P15, P19),
and checked by `python -m unittest discover -s theory -t .`.

## Reproducibility

- The **reference implementation reproduces the evaluated forecasts**: on 484 windows of seven populations, among
  them all 263 micro-load windows of BDG2 and of the EWELD post-cutoff windows, the 2.0.1 forecasts match the scored
  ones to the precision of their float32 storage (largest relative difference 6.6×10⁻⁸). The 2.0.0 mode
  (`micro_load_rule=False`) matches the stored forecasts of the 2.0.0 evaluation (5.7×10⁻⁸) and, compared directly,
  the scored 2.0.0 arm of the panel (6.6×10⁻⁸). The 1.x mode matches the evaluated 1.x forecasts exactly (largest
  difference 3.4×10⁻¹³ kW). On micro-load windows the forecast is bit-identical to the TimesFM forecast, elsewhere to
  the 2.0.0 mode. The TimesFM adapter, the peak operator and the interval functions are unchanged and were exact in
  the 1.x record.
  See [results/REPRODUCTION_CHECK.json](results/REPRODUCTION_CHECK.json); the 2.0.0 and 1.x records are
  [results/ankyra_2_0_0/REPRODUCTION_CHECK.json](results/ankyra_2_0_0/REPRODUCTION_CHECK.json) and
  [results/ankyra_1x/REPRODUCTION_CHECK.json](results/ankyra_1x/REPRODUCTION_CHECK.json).
- `results/` holds every scored statistic behind the figures and tables, for 2.0.1. `pip install -e ".[figures]"`
  and then `python figures/make_figures.py` regenerate all figures from it. The 2.0.0 result files are kept in
  `results/ankyra_2_0_0/`, the 1.x files in `results/ankyra_1x/`. Two files are new in 2.0.1:
  [`bdg2_micro_load_windows.csv`](results/bdg2_micro_load_windows.csv), the 46 windows the micro-load rule changes,
  one by one, and [`intervals_winkler_contrasts.csv`](results/intervals_winkler_contrasts.csv), the Winkler contrasts
  with their intervals for 2.0.1 and 2.0.0 ([file list](results/README.md)).
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
    anchoring's bounds and invariances; the readouts; and the reference estimator's documented values;
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

## What changed in 2.0 and 2.0.1

- **Within-day anchoring.** 1.x took the foundation model's within-day shape unchanged, although that block carries
  36–50% of the hourly squared error on buildings. 2.0 lets the unit's own analog days (same calendar type, within
  ±14 days of the same day of year, same daylight-saving state; up to eight, chosen by temperature) correct it, by the
  same error-weighted rule the other blocks use. Level, daily path, energy and peak readouts are unchanged.
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
- `forecast(..., micro_load_rule=False)` reproduces 2.0.0 exactly, and
  `forecast(..., within_anchor=False, micro_load_rule=False)` reproduces 1.x exactly; `foundation=None` gives a
  history-only configuration. The 2.0.0 and 1.x result files are kept in
  [`results/ankyra_2_0_0/`](results/ankyra_2_0_0/) and [`results/ankyra_1x/`](results/ankyra_1x/).

## Version history

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
Low Carbon London project; see [docs/EVALUATION.md](docs/EVALUATION.md) for references. The example window in `results/`
is from the University of Cambridge estate archive (CC BY 4.0).

Questions and bug reports: the [issue tracker](https://github.com/XinanQ/Building_load_ANKYRA/issues).
