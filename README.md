# ANKYRA

**Anchoring a time-series foundation model to each unit's own history for month-ahead load forecasting**

[中文说明](README.zh-CN.md) · [Method](docs/METHOD.md) · [Exact properties](docs/THEORY.md) · [Evaluation](docs/EVALUATION.md) · [Results data](results/)

![ANKYRA architecture](figures/fig1_architecture.png)

Pretrained time-series foundation models reproduce the shape of a day well, but over a 31-day horizon their monthly
level follows the last few days and drifts. A supply point's own history anchors the month, but reacts slowly and cannot
represent a load that has switched off. **ANKYRA** (Greek *ἄγκυρα*, anchor) uses each source where it is reliable, and
lets the unit's own forecast record decide where that is.

- A 744-hour forecast splits exactly into a **level**, a **centred daily path** and a **within-day shape**. The blocks are
  orthogonal, so their squared errors add.
- The within-day shape comes from **TimesFM 2.5** (zero-shot).
- The level and daily path come from six historical candidates plus the foundation model's own level. Each unit's
  errors at earlier pseudo-origins weight them, and the **same errors decide how much of the month to hand over** to
  the foundation model.
- A unit that has been **off for a week** is handed to the foundation model entirely.
- **Nothing is trained on the target series.** Every weight is a function of the unit's completed pseudo-forecasts.
- Three **readout operators** reuse the same computation:
  - energy from the level;
  - a monthly peak from a historical excursion envelope;
  - a prediction interval from pseudo-forecast residuals.
- The design choices and their limits are explained by **exact properties**: identities, bounds and the counterexamples
  that mark where they stop. Each is implemented and tested ([docs/THEORY.md](docs/THEORY.md)).

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
  - The six test populations were scored once, after the model was fixed, and nothing was tuned on them.

**What the tests show, and what they do not.** The tests establish input isolation in the implementation: nothing
recorded after the origin reaches the computation. They do not by themselves show that the inputs are free of later
information. Three sources lie outside the implementation:

- the providers' data preparation, such as gap filling (imputed or zero-filled hours are masked where documented);
- weather archives, whose past values may have been quality-controlled later;
- the pretraining corpora of TimesFM 2.5 and Chronos-2, which may contain some evaluation series (seven BDG2 sites are
  listed in them). This could favour every forecaster built on these models, ANKYRA included
  ([limitations](docs/EVALUATION.md#limitations)).

The information set is detailed in [docs/METHOD.md](docs/METHOD.md#information-at-the-origin).

## Results on six test populations

Five of the 20 baselines were given **ANKYRA's information set**: past load and temperature, climatological future
temperature, the load one year earlier, calendar features and unit category. They are per-population trained TiDE,
iTransformer-X and a gradient-boosting model (GBT-T), and covariate-conditioned Chronos-2 and TimesFM.

Each uses the part its architecture accepts:

- iTransformer-X takes no future covariates;
- Chronos-2-X takes no static features;
- TimesFM-X uses the covariates through a linear regression;
- GBT-T receives 21 features derived from the set.

PatchTST is channel-independent, so its forecast is the same with or without these inputs. The six test populations
were scored **once, after the model had been fixed**.

**Primary estimand.** The primary estimand is the unit-equal log RMS ratio, with 95% intervals from resampling units
and months. A contrast is *resolved* when its interval excludes zero. The mean per-unit rank is a secondary summary: it
stays defined when some units have zero error, but it does not replace the ratio.

| Test population | Country | Units / windows | Resolved better than (of 20) | …of them, same-information (of 5) | Resolved worse than | Rank among 21 |
|---|---|---:|:---:|:---:|:---:|:---:|
| BDG2 2017 (commercial and institutional meters) | USA / Europe | 142 / 474 | 10 | 2 | — | 1 |
| University of Cambridge estate | UK | 108 / 730 | 16 | 2 | — | 2 |
| HEEW, Arizona State University campus | USA | 138 / 658 | 15 | 2 | — | 1 |
| EWELD industrial and commercial meters | China | 197 / 523 | 18 | 5 | — | 1 |
| GoiEner non-household supply points | Spain | 481 / 890 | 15 | 3 | — | 1 |
| GoiEner households | Spain | 696 / 696 | 16 | 3 | TimesFM (3.8%) | 2 |

Windows are those after each population's training cutoff, where all 21 forecasters are available.

- On the test populations **ANKYRA is never resolvably worse than any baseline given its information set**.
- Among those five baselines, it is resolvably better than:
  - TiDE on all six populations;
  - GBT-T on four;
  - iTransformer-X and TimesFM-X on three;
  - Chronos-2-X on one (EWELD).
- Among the load-only statistical models, it is resolvably better than Holt–Winters on all six and MSTL on five.
- Its only resolved deficit on a test population is against zero-shot **TimesFM on households** (3.8%).
- Mean per-unit rank over the six populations: **5.94**. Next are the per-unit ridge (7.21), Chronos-2-X (7.72) and
  iTransformer-X (8.06).

![Test-set ranks and head-to-head](figures/fig2_test_ranks.png)

![Pairwise improvements with intervals](figures/fig3_test_pairwise.png)

**Where ANKYRA falls behind.** We report these as findings, not footnotes.

- **Norwegian schools and municipal buildings** (Oslo, Drammen; preview populations). Cross-unit trained models with
  calendar features are better: GBT-T by 18%, iTransformer-X by 9%.
  - Diagnostics point to the **activity level of individual days** (holidays, closure-like days, bridge days) rather
    than to the shape of the day.
  - Closure-like days are shared across units and recur from year to year.
  - The diagnosis rests on an oracle bound and on correlations. It narrows down the cause but does not identify the
    operating reasons.
- **Households.** Zero-shot TimesFM is better (see above).
- **BDG2.** Three meters read about 0.0002 kW, above the off-state threshold, and dominate the unit-mean ratios. The
  full result is kept, with a sensitivity analysis alongside:
  - with the three meters, ANKYRA's point estimate against TimesFM is −54.8% (late windows);
  - without them (11 windows), it is +1.6%;
  - either way the interval stays wide, because other low-load units also carry extreme ratios;
  - the median unit favours ANKYRA against each of the nine models in the figure above (59–92% of units);
  - ANKYRA ranks first with and without the three meters.
- **Conventional metrics.** On median unit CV(RMSE), Chronos-2-X or the per-unit ridge is slightly lower (by 0.2–2.2
  points) on nine of eleven populations. ANKYRA's advantage is on average over units and in rank, not at the median unit.

Full tables, all 11 populations and the evaluation protocol are in [docs/EVALUATION.md](docs/EVALUATION.md).

## How the handover works

![One test window](figures/fig6_example_window.png)

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
- The handover improves on the fixed division on seven of eleven populations (1.7–26.1%) and is never resolvably
  worse.
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
  ([evidence](docs/EVALUATION.md#departures-from-normal-operation-persist)).

![Ablation, handover granularity and lead-week profile](figures/fig4_handover_and_ablation.png)

## Peak operator

The monthly peak is read separately from the trajectory. The estimate is ANKYRA's daily means plus the largest recent
excursion of the same day type:

$$U=\max_d(\hat L_d+A_{\tau_d}).$$

Because maxima commute, this equals an hour-wise envelope. It satisfies $U\ge\max_d\hat L_d\ge\bar F$ and has an exact
median property under a stated working distribution. Its error splits into level, daily-path, amplitude and selection
terms, so ANKYRA's level gains carry into the peak.

- Against the maximum of the same trajectory, it reduces peak error by **22–77% on all eleven populations**.
- Against last month's observed peak, it is better on regularly operated buildings (Drammen, Oslo, HEEW: 12–16%) and
  worse on CINELDI's industrial customers.

![Peak operator](figures/fig5_peak_operator.png)

On GoiEner households the pseudo-origin interval around ANKYRA covers **79.2%** of hours at the nominal 80% level.
TimesFM's native 0.1–0.9 band covers 36.1%.

## Exact properties

![Exact properties on a test window](figures/fig7_operators.png)

The construction is auditable because each step has a stated property. They are numbered P1–P19 in
[docs/THEORY.md](docs/THEORY.md), which gives proofs, counterexamples and, where the earlier study measured them, their
consequences on data.

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
  - Restricting history to 12, 9 and 6 months worsened the level by 6.2%, 14.2% and 20.6%.
- **Energy (P11–P12).** Clipping at zero cannot increase any hour's error. No map can keep the energy, return
  nonnegative load and never increase error, all at once. Energy is therefore read from the level.
- **Peak (P15–P17).** The peak readout has a scalar form, satisfies $U\ge\max_d\hat L_d\ge\bar F$, and has a four-term
  error decomposition and a finite-support median property. Counterexamples mark where each stops.
- **Estimands (P19).** Pooled and unit-equal summaries can disagree in sign for an algebraic reason, so the evaluation
  reports both, with the mean rank and conventional metrics.

All 19 are implemented in `ankyra/operators.py` and checked by `tests/test_operators.py`.

## Cost

Timed per 744-hour window on one laptop: RTX 5060 Laptop GPU and Ryzen 9 8940HX, with one CPU thread for the history
side.

| Forecaster | First run | Pseudo-origins reused |
|---|---:|---:|
| TimesFM alone | 15 ms | — |
| ANKYRA | 0.50 s | 0.11 s |
| Chronos-2-X | 55 ms | — |
| Per-unit ridge (CPU) | 97 ms | — |

- **Where ANKYRA spends its time.** Most of it goes to the historical estimator at six pseudo-origins (0.30 s), not to
  the foundation model (seven calls, 0.10 s).
- **Reuse.** When forecasts are issued every 744 hours, those pseudo-origin results come from earlier runs.
- **TimesFM configuration.** The study ran TimesFM with its default per-core batch of 1, which takes 0.50 s per call. A
  per-core batch of 64 gives the same forecasts to within 3×10⁻⁵ kW.

Full timings are in [`results/cost_per_window.csv`](results/cost_per_window.csv).

## Install and run

Requires Python ≥ 3.10.

```bash
pip install -e .
python examples/quickstart.py
```

The quickstart runs on an artificial building with a stand-in forecaster and needs no data and no downloads. To use
TimesFM 2.5 (Apache-2.0; the checkpoint is downloaded from Hugging Face):

```bash
pip install -e ".[timesfm]"
python examples/quickstart.py --timesfm
```

```python
import ankyra
from ankyra.timesfm_adapter import load_timesfm, timesfm_forecaster

history = ankyra.History(load_kw=load_before_origin, temperature_c=temp_before_origin,
                         day_types=calendar_through_horizon, start_timestamp="2019-01-01T00:00:00+00:00")
f = ankyra.forecast(history, group="Office", temp_sigma_std=0.25,
                    foundation=timesfm_forecaster(load_timesfm()))
f.trajectory_kw, f.energy_kwh, f.lead_week_weights, f.level_weights
```

The inputs are:

- `load_kw` and `temperature_c`: hourly values up to the origin;
- `day_types`: Monday = 0 … Sunday = 6, holiday = 7, for the history plus the 744 forecast hours;
- `group`: selects the temperature-signature prior;
- `temp_sigma_std`: a fixed temperature-anomaly scale estimated before the first origin.

See [docs/METHOD.md](docs/METHOD.md) for the equations and all constants.

## Reproducibility

- The **reference implementation reproduces the evaluated forecasts exactly**: 613 test windows, maximum absolute
  difference 0.0 kW, including every off-state window. The TimesFM adapter, the peak operator and the interval
  functions are also exact.
  See [results/REPRODUCTION_CHECK.json](results/REPRODUCTION_CHECK.json).
- `results/` holds every scored statistic behind the figures and tables, and `python figures/make_figures.py`
  regenerates all figures from it.
- `python -m unittest discover -s tests -t .` runs 53 tests. They check:
  - that no information from after the origin reaches the forecast, the weights or the interval;
  - the 19 exact properties of [docs/THEORY.md](docs/THEORY.md), with their counterexamples;
  - the handover's limits and the off-state rule;
  - the reference estimator's documented values.
- Raw data are not redistributed. The evaluation populations are public; sources are listed in
  [docs/EVALUATION.md](docs/EVALUATION.md).

```
ankyra/              the forecaster
  core.py            model level candidate, week-by-week handover, off-state rule, forecast()
  history/           frozen reference estimator of the historical level and daily path
  readouts.py        energy, peak envelope operator, pseudo-origin interval
  blocks.py          orthogonal block decomposition
  operators.py       the exact properties P1–P19 as operators (replacement, support, shrinkage, projection, peak)
  metrics.py         unit-equal log RMS ratio, unit-and-month bootstrap, mean per-unit rank, pooled decomposition
  timesfm_adapter.py TimesFM 2.5 as configured in the study
examples/            quickstart on an artificial building
figures/             make_figures.py and the figures (PDF and PNG)
results/             scored results (CSV / JSON) and the reproduction record
docs/                METHOD.md, THEORY.md (exact properties), EVALUATION.md
tests/               unit tests
```

## Citation

The paper is in preparation. Until then, please cite the software ([CITATION.cff](CITATION.cff)):

> Qin, X. (2026). *ANKYRA: anchoring a time-series foundation model to each unit's own history for month-ahead load
> forecasting* (software, version 1.1.1). https://github.com/XinanQ/Building_load_ANKYRA

## License and acknowledgements

The code is released under the MIT license. TimesFM 2.5 is © Google (Apache-2.0) and is not redistributed. The
evaluation used public datasets from GoiEner, the COFACTOR projects (Drammen, Oslo), EWELD, the University of Cambridge
estate archive, CINELDI, HEEW, the Building Data Genome Project 2, the Suzhou industrial-park dataset and the London
Low Carbon London project; see [docs/EVALUATION.md](docs/EVALUATION.md) for references. The example window in `results/`
is from the University of Cambridge estate archive (CC BY 4.0).
