# ANKYRA

**Anchoring a time-series foundation model to each unit's own history for month-ahead load forecasting**

[中文说明](README.zh-CN.md) · [Method](docs/METHOD.md) · [Evaluation](docs/EVALUATION.md) · [Results data](results/)

![ANKYRA architecture](figures/fig1_architecture.png)

Pretrained time-series foundation models reproduce the shape of a day well, but over a 31-day horizon their monthly
level follows the last few days and drifts. A supply point's own history anchors the month, but reacts slowly and cannot
represent a load that has switched off. **ANKYRA** (Greek *ἄγκυρα*, anchor) uses each source where it is reliable, and
lets the unit's own forecast record decide where that is.

- A 744-hour forecast splits exactly into a **level**, a **centred daily path** and a **within-day shape**. The blocks are
  orthogonal, so their squared errors add.
- The within-day shape comes from **TimesFM 2.5** (zero-shot).
- The level and daily path come from six historical candidates plus the foundation model's own level. Each unit's
  errors at earlier pseudo-origins weight them, and the **same errors decide, week by week, how much to hand over** to
  the foundation model.
- A unit that has been **off for a week** is handed to the foundation model entirely.
- **Nothing is trained on the target series.** Every weight is a function of the unit's completed pseudo-forecasts.
- Three **readout operators** reuse the same computation:
  - energy from the level;
  - a monthly peak from a historical excursion envelope;
  - a prediction interval from pseudo-forecast residuals.

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

![Test-set ranks and head-to-head](figures/fig2_test_ranks.png)

| Test population | Country | Units / windows | ANKYRA rank among 21 |
|---|---|---:|:---:|
| BDG2 2017 (commercial and institutional meters) | USA / Europe | 142 / 474 | **1** |
| University of Cambridge estate | UK | 108 / 730 | 2 |
| HEEW, Arizona State University campus | USA | 138 / 658 | **1** |
| EWELD industrial and commercial meters | China | 197 / 523 | **1** |
| GoiEner non-household supply points | Spain | 481 / 890 | **1** |
| GoiEner households | Spain | 696 / 696 | 2 |
| **Mean per-unit rank** | | | **5.94** (next: per-unit ridge 7.21, Chronos-2-X 7.72, iTransformer-X 8.06) |

Windows are those after each population's training cutoff, where all 21 forecasters are available.

- On the test populations **ANKYRA is never significantly worse than any baseline given its information set**.
- Among those five baselines, it is significantly better than:
  - TiDE on all six populations;
  - GBT-T on four;
  - iTransformer-X and TimesFM-X on three;
  - Chronos-2-X on one (EWELD).
- Among the load-only statistical models, it is significantly better than Holt–Winters on all six and MSTL on five.
- Its only significant deficit on a test population is against zero-shot **TimesFM on households** (3.8%).

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
- **BDG2.** Three meters read about 0.0002 kW, above the off-state threshold, and pull the unit-mean ratios. The
  median unit favours ANKYRA against each of the nine models in the figure above (59–92% of units).
- **Conventional metrics.** On median unit CV(RMSE), Chronos-2-X or the per-unit ridge is slightly lower (by 0.2–2.2
  points) on nine of eleven populations. ANKYRA's advantage is on average over units and in rank, not at the median unit.

Full tables, all 11 populations and the evaluation protocol are in [docs/EVALUATION.md](docs/EVALUATION.md).

## How the handover works

![One test window](figures/fig6_example_window.png)

In September a university building's load rises after the summer. TimesFM carries the recent level forward, while
ANKYRA's history-weighted level anticipates the rise. The handover follows the lead time:

- Under a **fixed division** (history's level, the model's shape), the foundation model alone is better in the first
  week and worse later.
- ANKYRA estimates, for each unit, how much of the model's daily means to use in each week.
  - The weights are fitted on the unit's completed pseudo-forecasts: the fixed division against TimesFM.
  - They are then applied to ANKYRA's history-side daily means, whose level also contains the model candidate
    ([details](docs/METHOD.md#week-by-week-handover)).
- On the three populations scored for the first time after the handover was fixed, ANKYRA's point estimate beats
  TimesFM in **every** forecast week.
- The handover improves on the fixed division on seven of eleven populations (1.7–26.1%) and is never significantly
  worse.

![Ablation and lead-week profile](figures/fig4_handover_and_ablation.png)

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
- `python -m unittest discover -s tests -t .` checks:
  - the block identity;
  - the scalar form and bounds of the peak operator;
  - the projection property;
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
  metrics.py         unit-equal log RMS ratio, unit-and-month bootstrap, mean per-unit rank
  timesfm_adapter.py TimesFM 2.5 as configured in the study
examples/            quickstart on an artificial building
figures/             make_figures.py and the figures (PDF and PNG)
results/             scored results (CSV / JSON) and the reproduction record
docs/                method and evaluation
tests/               unit tests
```

## Citation

The paper is in preparation. Until then, please cite the software ([CITATION.cff](CITATION.cff)):

> Qin, X. (2026). *ANKYRA: anchoring a time-series foundation model to each unit's own history for month-ahead load
> forecasting* (software, version 1.0.0). https://github.com/XinanQ/Building_load_ANKYRA

## License and acknowledgements

The code is released under the MIT license. TimesFM 2.5 is © Google (Apache-2.0) and is not redistributed. The
evaluation used public datasets from GoiEner, the COFACTOR projects (Drammen, Oslo), EWELD, the University of Cambridge
estate archive, CINELDI, HEEW, the Building Data Genome Project 2, the Suzhou industrial-park dataset and the London
Low Carbon London project; see [docs/EVALUATION.md](docs/EVALUATION.md) for references. The example window in `results/`
is from the University of Cambridge estate archive (CC BY 4.0).
