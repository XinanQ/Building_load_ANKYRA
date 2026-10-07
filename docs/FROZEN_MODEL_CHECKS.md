# Checks with the forecaster frozen (4–6 October 2026)

Every check was run with the public package and all its defaults, the forecaster frozen. None changes the forecaster
or the result tables of the ten populations. The HKUST, Helsinki, LCL and UNICON numbers on this page are those of **ANKYRA 2.2** (one within-day trust
per window, with gap tolerance in the pseudo-origin bookkeeping); the carrier-swap tables are those of ANKYRA 2.1.

- **HKUST, Helsinki and LCL** ([LCL_AND_CLOSEOUT.md](LCL_AND_CLOSEOUT.md)) were first scored with the frozen ANKYRA
  2.0.1, before 2.1 and 2.2 were adopted on 6 October 2026; the same targets were then read again with 2.1 and 2.2, so
  their 2.2 numbers are re-evaluations, not first reads. The verdicts are the same under all versions, with two
  exceptions noted below (on HKUST the hourly contrast against Chronos-2 and the energy contrast against GBT are
  resolved under 2.2, not before); the
  2.0.1 files are in [`results/ankyra_2_0_1/`](../results/ankyra_2_0_1/) and the 2.1 files in
  [`results/ankyra_2_1/`](../results/ankyra_2_1/).
- **UNICON** is the external test of the frozen 2.1, a first read of a population the project had never used; the
  same targets were then read again with 2.2, with the same decisions and verdicts (the 2.1 files are in
  `results/ankyra_2_1/`).
- The carrier-swap tables use the anchoring of 2.1 (the 2.0.1 runs are in `results/ankyra_2_0_1/`, with the same
  resolved counts).

The first four items each had a protocol written before the run; the fifth is a post-hoc exploration with no
criterion fixed in advance.

- [Another foundation model](#another-foundation-model): Chronos-2 in place of TimesFM; with the Chronos-2-X run, two foundation-model families in three configurations on the same windows.
- [A population never used before](#a-population-never-used-before): the HKUST campus; one original first read, then added comparators, a carrier exploration and a causal correction.
- [A pre-registered confirmation test (Helsinki)](#a-pre-registered-confirmation-test-helsinki): criteria fixed in advance; not confirmed.
- [An external test of ANKYRA 2.1 (UNICON)](#an-external-test-of-ankyra-21-unicon): five university campuses in Australia; criteria fixed in advance; not confirmed on the primary criterion.
- [A post-hoc exploration: ANKYRA anchored to Chronos-2-X](#a-post-hoc-exploration-ankyra-anchored-to-chronos-2-x): twelve populations; not a test.

Numbers are improvements in the unit-equal log RMS ratio (positive = the first model has the lower error) with the
95% unit-and-month bootstrap interval of the log ratio (an interval below zero = resolved in favour of the first
model). See [EVALUATION.md](EVALUATION.md) for the estimand.

![Two checks with the forecaster frozen](../figures/fig17_frozen_checks.png)

*Figure 17. a: anchoring gain with either foundation model (ten populations, all windows). b, c: HKUST campus, ANKYRA 2.2 against each of ten comparators (`results/hkust_first_read.csv`; first scored with 2.0.1, same verdicts except the hourly contrast against Chronos-2, resolved under 2.2). Filled markers: the 95% interval excludes zero; diamonds: borderline. The per-day curves of HKUST, Helsinki, LCL and UNICON are panels of Figures 9 and 9b ([EVALUATION.md](EVALUATION.md#loss-by-forecast-day)).*

## Another foundation model

**Question.** Does the gain from anchoring depend on TimesFM?

**What was done.** `ankyra.forecast` takes the foundation model's forecasts as an argument. They were replaced by
Chronos-2 point forecasts at the origin and at the six pseudo-origins; nothing else changed and no constant was
chosen again. The result is called ANKYRA-C here. All windows of the ten populations were scored. These populations
had been scored before, so this is a re-evaluation with a pre-specified new arm. It is a descriptive table: the
released forecaster stays the TimesFM-based one. The table shows the anchoring of ANKYRA 2.1; it was first run with
2.0.1 (`results/ankyra_2_0_1/carrier_swap.csv`), with the same resolved counts.

| Population | Windows | ANKYRA-C vs Chronos-2 (hourly) | ANKYRA vs TimesFM (hourly) | ANKYRA-C vs ANKYRA (hourly) | ANKYRA-C vs Chronos-2 (monthly energy) |
|---|---|---|---|---|---|
| GoiEner non-household | 1,237 | +4.4% [-0.071, +0.017] | +4.3% [-0.073, +0.014] | +1.2% [-0.047, +0.012] | +20.0% [-0.440, -0.099] |
| GoiEner households | 1,258 | -0.8% [-0.011, +0.068] | -2.5% [-0.004, +0.109] | -2.8% [+0.005, +0.075] | +31.9% [-0.518, -0.207] |
| EWELD | 1,023 | +2.6% [-0.044, -0.006] | +3.2% [-0.051, -0.007] | -1.7% [-0.031, +0.131] | +8.3% [-0.199, +0.017] |
| BDG2 2017 | 934 | +7.0% [-0.091, +0.241] | +5.8% [-0.079, +0.223] | +1.9% [-0.127, +0.027] | +16.5% [-0.266, +0.117] |
| Cambridge | 1,456 | +11.5% [-0.142, -0.090] | +9.7% [-0.123, -0.072] | -1.6% [-0.005, +0.035] | +18.9% [-0.278, -0.147] |
| Arizona (HEEW) | 1,282 | +7.7% [-0.105, -0.030] | +4.5% [-0.066, +0.000] | -1.9% [-0.001, +0.042] | +14.6% [-0.248, -0.028] |
| Oslo | 1,147 | +12.2% [-0.160, -0.097] | +11.3% [-0.147, -0.092] | +0.2% [-0.027, +0.023] | +17.9% [-0.266, -0.090] |
| Drammen | 1,375 | +9.9% [-0.139, -0.070] | +11.4% [-0.159, -0.088] | +1.7% [-0.041, +0.008] | +19.3% [-0.327, -0.126] |
| CINELDI | 929 | +6.0% [-0.087, -0.034] | +6.7% [-0.099, -0.037] | +1.5% [-0.037, +0.003] | +16.3% [-0.271, -0.081] |
| Suzhou park | 127 | +17.8% [-0.305, -0.087] | +11.9% [-0.209, -0.045] | -2.6% [-0.021, +0.064] | +22.9% [-0.472, -0.112] |

**Reading.**

- Anchoring improves Chronos-2 in the same pattern as TimesFM: resolved on 7 of ten populations
  (TimesFM: 6), never resolvably worse, and negative only on households, as with TimesFM.
- On the windows after each population's training cutoff the count is 5 of ten for both foundation models.
- Monthly energy error improves resolvably on 8 of ten.
- The two finished forecasters are not separated on nine populations. On households the Chronos-2-based one is
  2.8% worse; Chronos-2 itself is 4.6% worse than TimesFM there.
- Limits: two foundation-model families were tested (three configurations with the Chronos-2-X run below), not
  foundation models in general; the constants were selected under
  TimesFM; the populations were not new. The ANKYRA-vs-TimesFM column is recomputed with this experiment's bootstrap
  seed, so its intervals can differ in the third decimal from `benchmark_pairwise.csv`.

File: [`results/carrier_swap.csv`](../results/carrier_swap.csv) (all windows and late windows, hourly and energy).

### Two families, three configurations on the same windows

The Chronos-2 run above and the post-hoc Chronos-2-X run
([below](#a-post-hoc-exploration-ankyra-anchored-to-chronos-2-x)) re-scored together with the released TimesFM-anchored forecaster
on one set of windows (units with mean load of at least 10⁻⁶ kW) with one bootstrap seed (20261005). Gain of each anchored version
over its own foundation model; `*` resolved in its favour; none resolved against it; `—` not run. On these windows the TimesFM count
is 7 of 12 hourly (6 of ten in the table above, whose EWELD windows include near-zero meters).

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

File: [`results/carrier_swap_combined.csv`](../results/carrier_swap_combined.csv) (intervals included, plus the finished forecasters
against each other).

**The method does not depend on its carrier.** Anchoring improves each of the three foundation-model configurations
over the model alone, and is never resolvably worse. This bears on the closest competitor of the ten-population
comparison, the covariate-informed Chronos-2-X: anchored to Chronos-2-X (ANKYRA-X), the method is resolvably better than
Chronos-2-X on 8 of 12 populations for hourly error and on 8 of 12 for monthly energy error. The anchoring is the
method; TimesFM is the carrier of the released forecaster.

## A population never used before

**Question.** What does the frozen forecaster do on data the project had never read? This is a blind test in the
following sense: no rule or constant of ANKYRA was chosen with this population in view, the units and the scoring
plan were fixed before any load value was opened, inputs were truncated at each origin, and the forecasts were saved
before any target loss was computed. It is not blind for the foundation models, whose pretraining data were not checked.

**Data.** The smart-meter database of the Hong Kong University of Science and Technology campus (Li, Wang, Qu, Chui and Leung-Shea, *Scientific Data* 11, 1284, 2024, doi:10.1038/s41597-024-04106-1; data on Dryad,
doi:10.5061/dryad.k3j9kd5h6, CC0; 1 January 2022 to 27 May 2024). Units are the meters of the incomer circuit
breakers named in the dataset's Brick metadata - the metering points closest to the total of a supply zone. 46 are
named, 38 have cleaned files. The files hold cumulative readings; hourly energy is their difference. Temperature is
ERA5 reanalysis for the campus; Hong Kong general holidays are day type 7; the category is `Public`.

**Procedure.** The unit definition and the scoring plan were written before any load value was opened. Forecasts
were saved with a hash before any target loss was computed, and the first read was one scoring pass, with the frozen
ANKYRA 2.0.1. Comparators, a carrier exploration and a correction of the temperature scale were added afterwards
(below). The numbers on this page are ANKYRA 2.2 on the recomputed forecasts: the same targets read again, a
re-evaluation and not a second blind test. Every verdict is the same as for 2.0.1 (files in `results/ankyra_2_0_1/`)
and 2.1 (`results/ankyra_2_1/`), except that the hourly contrast against Chronos-2, borderline under 2.0.1 and 2.1,
is resolved under 2.2. The usual eligibility rule
(complete load for the context, the six pseudo-origins and the target) leaves **134 windows on 33 units in 19
months**. Three incomers read zero throughout; there the off-state and micro-load rules return TimesFM, both errors
are zero, and the units drop out of the ratio (30 effective units). 125 windows have less than two years of history.

| ANKYRA against | Hourly error | Monthly energy error |
|---|---|---|
| Chronos-2-X (added afterwards) | +4.0% [-0.129, +0.013] | +11.6% [-0.720, +0.601] |
| TimesFM-X (added afterwards) | +5.5% [-0.180, +0.027] | +33.4% [-0.785, +0.068] |
| TimesFM 2.5 | +8.8% [-0.230, -0.007] | +42.9% [-0.955, -0.105] |
| Chronos-2 | +11.7% [-0.293, -0.001] | +46.8% [-1.090, +0.089] |
| Seasonal naive (day) | +23.6% [-0.423, -0.152] | +43.3% [-1.201, +0.206] |
| Seasonal naive (week) | +24.4% [-0.442, -0.171] | +45.5% [-1.108, +0.203] |
| Four-week profile | +12.8% [-0.228, -0.069] | +45.4% [-0.972, +0.137] |
| Previous-month profile | +12.4% [-0.228, -0.056] | +43.7% [-0.933, +0.032] |
| Last-year profile | +19.3% [-0.380, -0.114] | +31.7% [-0.750, +0.177] |
| Per-unit ridge | +16.6% [-0.714, +0.018] | +29.8% [-0.826, +0.066] |

Mean unit rank among the eight models first scored on all windows: ANKYRA 2.03, TimesFM 3.45; among ten, with the two
added models: ANKYRA 2.52, TimesFM-X 4.03, TimesFM 4.58, Chronos-2-X 4.76.
The per-unit ridge is defined on 123 windows of 32 units. Baselines that must be trained on the population were not fitted.

**The two covariate-informed foundation models** (Chronos-2-X and TimesFM-X, which receive the same information as
ANKYRA) were run afterwards on the same windows, with the features and calls of the ten-population comparison. ANKYRA's
forecasts were already frozen and scored, so this completes the comparison and is not a second blind test. ANKYRA is
not separated from either, on hourly or energy error, under any of six bootstrap seeds; its mean unit rank stays
first. This matches the ten populations, where Chronos-2-X is the closest competitor.

**Three more baselines and the per-day curves** (Holt-Winters, MSTL and the zero-shot GBT, which need no training on
the population) were then run the same way, again against the frozen forecasts and again not a blind test. With them
the HKUST comparison has the same 14 forecasters as the full-window comparison of the ten populations. ANKYRA's hourly
error is 15.7%, 22.6% and 57.2% lower than theirs, each resolved under every seed; on monthly energy it is resolved
against MSTL (53.9%) and GBT (59.2%, upper end −0.011; not resolved under 2.0.1 and 2.1). Mean unit rank among the 14 on
the 123 ridge-defined windows: ANKYRA 3.30, per-unit ridge 4.27, TimesFM-X 5.28, TimesFM 5.73. The per-day curves, with the definitions of Figures 9 and 9b, are the HKUST panel of
those figures ([`results/hkust_by_day.csv`](../results/hkust_by_day.csv); quantised readings flatten the hourly curves):
ANKYRA has the lowest hourly error of the 14 on 15 of 31 days and the lowest energy error to date on 24.

**Reading - weaker than the table looks.**

- Every point estimate favours ANKYRA, but the two hourly intervals against the foundation models end close to zero
  (upper ends −0.007 against TimesFM and −0.001 against Chronos-2 under 2.2; under 2.0.1 and 2.1 they ended at zero
  and, recomputed with five further bootstrap seeds, the interval excluded zero once against TimesFM and four times
  against Chronos-2). Both are borderline.
- The meters are coarsely quantised (steps of 10 or 100 kWh). In the 2.0.1 first read, on the 11 units whose step is
  at least a quarter of their mean load, ANKYRA and TimesFM were level (mean log ratio -0.007) and the hourly gain was
  in the other 19 (-0.129); this split was not recomputed for 2.1 or 2.2.
- Monthly energy error, which quantisation does not affect, is 42.9% below TimesFM's, with an interval that excludes
  zero under every seed tried. Against the other comparators except MSTL and GBT the energy intervals include zero.
- The sample is small and uneven: 1 to 17 windows per unit, 59 of the 134 windows in two months.
- One constant, the temperature scale, was first computed from the first 244 days as planned, which for the four
  windows issued on 1 September 2022 included 24 hours after the origin. It was then refitted on the 243 days before
  the first origin and every ANKYRA forecast on HKUST was run again: forecasts change by at most 4.4 × 10⁻⁵ of their
  peak, every result changes by at most 0.001 percentage points and no decision changes. The result files
  (`results/hkust_*`, `results/carrier_swap_*`), Figure 17 and the HKUST panels of Figures 9 and 9b come from the
  recomputed forecasts. No forecaster and no constant uses information after its origin.
- Whether TimesFM or Chronos-2 was pretrained on this dataset (published 2024) was not checked.

This is one population with one original first read, followed by added comparators, a carrier exploration and a causal correction. It is not merged into the ten-population tables and it does not show that the
forecaster generalises; it shows that the frozen forecaster did not fail on first contact with an unseen estate.

Files: [`results/hkust_first_read.csv`](../results/hkust_first_read.csv) and
[`results/hkust_by_day.csv`](../results/hkust_by_day.csv) (2.2; the 2.0.1 and 2.1 versions are in `results/ankyra_2_0_1/`
and `results/ankyra_2_1/`). The
column `resolved_at_seed_20261004` is the reading under one bootstrap seed; see the first bullet above.
`units_better_strict` counts units with a strictly lower summed error and so includes the three all-zero units for
Chronos-2 (25 of the 30 non-zero units are better).

## A pre-registered confirmation test (Helsinki)

**Question.** Does the frozen forecaster's advantage hold on a new, large population under criteria written before
any load value is read?

**Data.** Energy consumption of the City of Helsinki's service properties, Nuuka Open API (City of Helsinki, Urban
Environment Division; licence listed as CC BY 4.0 in the regional and national open-data catalogues). Hourly electricity,
2023-01-01 to 2026-10-03, pulled on 5 October 2026 and not redistributed. Preparation: [DATA.md](DATA.md).

**Procedure.** The protocol fixed the sample (300 property codes drawn by SHA-256 of the code, after excluding three
properties looked at during a format check), the units (one electricity series each), the grid (fixed UTC+2; the
provider's two-hour autumn record split evenly and flagged), the window rules of the ten populations, eleven origins
(2025-11 to 2026-09, after the public release of TimesFM 2.5 and Chronos-2), the 14 forecasters of the full-window
comparison, the estimand and the criteria. It was frozen with the hashes of all 978 raw files before any load value
was parsed. Inputs were truncated at each origin and all 14 forecasts were saved with a hash before any target loss was computed;
the targets were scored once, with the frozen ANKYRA 2.0.1. A
first scoring attempt stopped while loading the targets (memory) before any statistic was computed; this is recorded.
The numbers below are ANKYRA 2.2 on the same targets (a re-evaluation, not a second confirmation); the decisions are
the same as under 2.0.1 and 2.1, whose files are in `results/ankyra_2_0_1/` and `results/ankyra_2_1/`.

**Criteria (seed 20261005).** Primary: monthly energy error, ANKYRA against TimesFM 2.5, upper end of the 95%
unit-and-month interval below zero. Secondary: hourly error, lower end at or below zero. Confirmation needs both.

**Result: not confirmed.**

| Criterion | Improvement | Interval of the log ratio | Outcome |
|---|---|---|---|
| Monthly energy vs TimesFM | 6.2% | [−0.168, +0.106] | failed |
| Hourly vs TimesFM | 4.9% | [−0.109, +0.018] | passed |

Five further bootstrap seeds give the same decisions (for 2.0.1 an independent recomputation, own code and another
seed, also did).

| ANKYRA against | Hourly | Monthly energy |
|---|---|---|
| TimesFM 2.5 | +4.9% | +6.2% |
| Chronos-2 | +2.6% | +2.0% |
| Chronos-2-X | **−5.6% (resolved against)** | **−13.6% (resolved against)** |
| TimesFM-X | +5.2% | +6.3% |
| Per-unit ridge | +5.2% * | +4.0% |
| GBT (zero-shot) | +14.7% * | +3.1% |
| Holt-Winters | +8.2% * | +3.8% |
| MSTL | +10.4% * | +8.3% |
| Seasonal naive (day / week) | +28.3% * / +11.6% * | +27.6% * / +5.8% |
| Four-week / previous-month / last-year profile | +5.7% / +12.0% * / +22.1% * | +0.3% / +3.1% / +24.5% * |

\* resolved in ANKYRA's favour. 200 units with non-zero load, 1,165 windows. Mean unit rank among the 14: Chronos-2-X
4.12, ANKYRA 4.17, Chronos-2 4.92, TimesFM-X 5.93, TimesFM 6.09. Per-day curves: the Helsinki panels of Figures 9 and
9b (ANKYRA below TimesFM on 25 of 31 days on both curves, below Chronos-2-X on 3 and 6). Files:
`results/helsinki_confirmation.csv`, `results/helsinki_criteria.json`, `results/helsinki_by_day.csv`.

**Reading.** On a new country with long, finely metered histories, the frozen forecaster is not separated from
TimesFM on either error and is resolvably worse than the covariate-conditioned Chronos-2-X. The energy advantage seen
on the ten populations and on HKUST is therefore not confirmed. Post-hoc descriptions locate, but do not explain, the
difference. The exact block split was computed on the 2.0.1 forecasts only; its level block is bit-identical in 2.1,
its within-day block is not, and the split was not recomputed for 2.1 or 2.2. In it, ANKYRA's error is higher than Chronos-2-X's mainly in the
monthly level (by 13.9%, resolved; the largest block of the error) and by 4.2% in the within-day block (resolved);
against its own carrier TimesFM, ANKYRA's within-day error is 6.1% lower (resolved). The temperature-sensitivity measures tested did not support that explanation: the share of daily-load variance that temperature
explains beyond the calendar is 0.10 at the median Helsinki unit, inside the range of the ten populations
(0.05–0.70), unrelated to the gap to Chronos-2-X across them, and the gap is similar in the least and most
temperature-sensitive thirds of the Helsinki units. Boundary of use: on a new population, a covariate-informed
foundation model can forecast the monthly level better than ANKYRA's history-weighted level. The anchoring itself does
not depend on TimesFM: anchored to Chronos-2-X, it is level with Chronos-2-X on Helsinki (+0.8% hourly, +0.6% energy,
neither resolved) and resolvably better than the TimesFM-anchored ANKYRA
([below](#a-post-hoc-exploration-ankyra-anchored-to-chronos-2-x)).

## An external test of ANKYRA 2.1 (UNICON)

**Question.** Does the frozen ANKYRA 2.1 keep its advantage on a population the project had never used, under
criteria written before any load value is read? This is the first and only frozen-model test of 2.1; HKUST, Helsinki
and LCL tested 2.0.1.

**Data.** UNICON, the electricity data of La Trobe University's campuses in Victoria, Australia (Moraliyage et al.,
HSI 2022, doi:10.1109/HSI55341.2022.9869498; Kaggle `cdaclab/unicon`, version 1; licence CC BY-NC-SA 4.0, research use
only; the data are not redistributed here). Five campuses: Bundoora, Albury-Wodonga, Bendigo, Mildura and Shepparton.
Units are the 64 building meters of `building_consumption.csv` (15-minute readings), all included; category `Public`.
Temperature is ERA5 at one point per campus; Victorian public holidays are day type 7. Preparation:
[DATA.md](DATA.md#14-unicon-la-trobe-university-campuses-australia).

**Procedure.** The protocol fixed the model (package 2.1.0, defaults), the units, the grid, the eligibility rule, the
14 forecasters of the Helsinki test, four descriptive arms, the estimand and the criteria. It was frozen with the
hashes of the raw files after only the metadata and the timestamp and identifier columns had been read; no
consumption value had been parsed. All forecasts were saved with a hash before any target was read, and the targets
were scored once, with the frozen ANKYRA 2.1. The numbers below are ANKYRA 2.2 on the same targets (a re-evaluation,
not a second test); the decisions and every verdict are the same as under 2.1, whose files are in
`results/ankyra_2_1/`.

**Amendment 01, and why.** Under the frozen eligibility rule (complete load from six pseudo-origins before the origin
to the end of the target month) **no window qualified**: the meters have dense short gaps. The amendment was written
after the missingness had been seen and before any forecast was made; it changes only the handling of gaps in the
inputs and the eligibility rule. Each window gets its own series, set missing at and after its origin. Inside each
1,344-hour context (at the origin or a pseudo-origin) gaps of at most 6 hours are filled by linear interpolation
between the two neighbouring observations, only when the gap lies wholly inside one of the two 744-hour and 600-hour
segments split at the pseudo-origin 744 hours earlier; no filled value uses data at or after any origin or
pseudo-origin. Target values are never filled: missing target hours are left out of the hourly loss, and the monthly
energy is taken over the observed target hours, the same hours for forecast and load. A window is eligible when its
filled 1,344-hour context is complete, at least 95% of its target is observed and the unit's mean load is at least
10⁻⁶ kW. A pseudo-origin is used only if its own filled context is complete. Model, comparators, criteria and scoring
are unchanged.

**Windows.** 843 windows of 60 units in 37 target months, with origins from 2018 to 2022 (month-start origins from
September 2018 to March 2022 were possible). Filled values are 12,352 context hours, about 1.1% of the context hours. 1,363 records off the 15-minute grid were dropped and 8,026
negative readings, on two meters, were set missing. No window triggers the off-state or the micro-load rule. The
per-unit ridge is defined on 674 windows.

**Criteria (seed 20261006).** As for Helsinki. Primary: monthly energy error, ANKYRA against TimesFM 2.5, upper end of
the 95% unit-and-month interval below zero. Secondary: hourly error, lower end at or below zero. Confirmation needs
both.

**Result: not confirmed on the primary criterion.**

| Criterion | Improvement | Interval of the log ratio | Outcome |
|---|---|---|---|
| Monthly energy vs TimesFM | 4.4% | [−0.157, +0.116] | failed |
| Hourly vs TimesFM | 2.4% | [−0.052, +0.011] | passed |

Under the five further seeds the upper end of the primary interval stays above zero. As on Helsinki, the test fails on
monthly energy against TimesFM.

| ANKYRA 2.2 against | Hourly | Monthly energy |
|---|---|---|
| TimesFM 2.5 | +2.4% [−0.052, +0.011] | +4.4% [−0.157, +0.116] |
| Chronos-2 | +2.1% [−0.055, +0.018] | +2.7% [−0.147, +0.117] |
| Chronos-2-X | +5.8% \* [−0.114, −0.003] | +11.7% [−0.294, +0.029] |
| TimesFM-X | +4.4% \* [−0.080, −0.004] | +10.0% [−0.246, +0.044] |
| Per-unit ridge (674 windows) | +4.2% \* [−0.095, −0.007] | −0.6% [−0.129, +0.138] |
| GBT (zero-shot) | +25.7% \* [−0.369, −0.215] | +19.8% \* [−0.377, −0.038] |
| Holt-Winters | +14.6% \* [−0.210, −0.102] | +26.9% \* [−0.456, −0.162] |
| MSTL | +15.1% \* [−0.209, −0.117] | +19.1% \* [−0.392, −0.046] |
| Seasonal naive (day) | +34.3% \* [−0.531, −0.330] | +39.3% \* [−0.738, −0.330] |
| Seasonal naive (week) | +15.8% \* [−0.215, −0.128] | +6.6% [−0.192, +0.071] |
| Four-week profile | +6.5% \* [−0.113, −0.020] | +5.3% [−0.190, +0.101] |
| Previous-month profile | +17.2% \* [−0.248, −0.142] | +9.4% [−0.226, +0.038] |
| Last-year profile | +20.2% \* [−0.296, −0.168] | +18.9% \* [−0.350, −0.043] |
| *Descriptive arms:* ANKYRA 2.0.1 (trust per lead block) | −0.1% [−0.011, +0.013] | −2.5% [−0.020, +0.065] |
| ANKYRA anchored to Chronos-2-X (ANKYRA-X) | +1.4% [−0.052, +0.023] | +1.7% [−0.135, +0.077] |
| Half history, half TimesFM (B1) | −0.1% [−0.012, +0.012] | −1.2% [−0.041, +0.104] |
| One combination weight per unit (B2) | −0.1% [−0.011, +0.013] | −1.2% [−0.039, +0.101] |

\* resolved in ANKYRA's favour; no contrast is resolved against it. 843 windows, 60 units.

- **Hourly.** Resolved in ANKYRA's favour against 11 of the 13 comparators, including both covariate-informed
  foundation models (Chronos-2-X 5.8%, TimesFM-X 4.4%) and the per-unit ridge. Against TimesFM and Chronos-2 it is
  about 2% better, not resolved.
- **Monthly energy.** 3–12% better than every foundation-model variant, none resolved (against Chronos-2-X the upper
  end is +0.029); resolved against five simple or statistical baselines.
- **Rank.** Mean unit rank among the 14 on the 674 windows where the ridge is defined: ANKYRA 3.03, Chronos-2 3.92,
  TimesFM 4.20, TimesFM-X 4.40, per-unit ridge 4.88, Chronos-2-X 5.10; ANKYRA is first.
- **Per day.** In the UNICON panels of Figures 9 and 9b (674 windows, 60 units) ANKYRA is the lowest of the 14 on 18 of
  31 days for hourly error and on 4 for energy to date ([`results/unicon_by_day.csv`](../results/unicon_by_day.csv)).

**By year of origin** (against TimesFM; descriptive, not part of the decision; point estimates from
`results/unicon_criteria.json`, intervals not exported for 2.2):

| Year | Windows | Hourly | Monthly energy |
|---|---:|---|---|
| 2018 | 130 | +1.6% | +3.4% |
| 2019 | 323 | +4.0% | +15.9% |
| 2020 | 205 | −4.0% | −18.7% |
| 2021 | 161 | −1.1% | +0.8% |
| 2022 | 24 | +8.1% | +22.0% |

In 2020, the year the campuses closed under COVID-19 restrictions, ANKYRA is behind TimesFM; in 2021 it is level
(−1.1% hourly, +0.8% energy); in the other years it is ahead.

**Diagnostic** (written after the forecasts were frozen and before scoring, under the 2.1 bookkeeping). The dense gaps leave few complete
pseudo-origin windows: of the 3,378 pseudo-origin contexts needed, 1,966 were complete, and ANKYRA 2.1 used on average
0.51 of its 6 pseudo-origin pairs, so its weights stayed close to their priors. This test therefore measures what
ANKYRA does on gappy data, where its error-based weighting has almost nothing to work with. For the same reason 2.1
and 2.0.1 are practically identical here, and the combination baselines B1 and B2 are level with ANKYRA (B2's weight
on TimesFM has median 0.5): UNICON cannot tell block-wise from whole-window weighting
([EVALUATION.md](EVALUATION.md#what-the-parts-buy)). Anchored to Chronos-2-X, the method is better than Chronos-2-X by
4.5% hourly and 10.2% on monthly energy, both resolved (study record; not in the exported file).

**Limits.** One university, five campuses. The amendment was made after the missingness had been seen (but before any
forecast or error). The target months precede the release of TimesFM 2.5 and Chronos-2; whether UNICON is in their
pretraining corpora could not be checked. The meters' reading unit is not documented; the readings were taken as kWh
per 15 minutes. Ratios do not depend on that choice; only the absolute off-state and micro-load thresholds would, and
neither fires here.

Files: [`results/unicon_external.csv`](../results/unicon_external.csv) (every contrast, both errors, with intervals),
[`results/unicon_criteria.json`](../results/unicon_criteria.json) (criteria, outcome, mean unit ranks, results by year,
licence note, diagnostic), [`results/unicon_by_day.csv`](../results/unicon_by_day.csv) (per-day curves).

## A post-hoc exploration: ANKYRA anchored to Chronos-2-X

**Status.** Requested after the Helsinki result; no criterion fixed in advance; all twelve populations scored before (Helsinki for
the fourth time); no constant of ANKYRA changed (constants selected with TimesFM). The table below uses the anchoring
of ANKYRA 2.1; the run was first made with 2.0.1 (`results/ankyra_2_0_1/carrier_swap_x.csv`), with the same resolved
counts. An exploration, not a test.

**Procedure.** `ankyra.forecast` received Chronos-2-X point forecasts as its foundation forecasts: at the origin the forecasts already
scored, at the pseudo-origins k = 1..6 new forecasts with the covariates of the equal-information set built at each pseudo-origin from
data before it (about 60,000 contexts). Unit-equal log RMS ratio, 95% unit-and-month interval (seed 20261005), all windows.

|Population|Windows|vs Chronos-2-X, hourly|vs Chronos-2-X, energy|vs ANKYRA, hourly|vs ANKYRA, energy|
|---|---:|---:|---:|---:|---:|
|BDG2|934|+4.2%|+20.5%|-10.4%|+0.5%|
|Cambridge|1,456|+4.7%*|+8.9%*|+5.4%*|+8.9%*|
|HEEW|1,282|+4.8%*|+12.2%*|+1.3%|+3.6%|
|EWELD|931|+3.8%*|+7.7%|-0.2%|-8.1%|
|GoiEner non-household|1,234|+3.3%|+19.5%*|+0.6%|+4.9%|
|GoiEner households|1,232|+0.1%|+31.1%*|-0.2%|+2.5%|
|Oslo|1,147|+6.3%*|+8.2%*|+6.1%*|+11.5%*|
|Drammen|1,375|+4.5%*|+9.0%*|+4.5%*|+9.4%|
|CINELDI|929|+5.4%*|+16.4%*|+2.3%|+4.0%|
|Suzhou park|127|+14.6%*|+20.2%*|+1.7%|+4.2%|
|HKUST campus|120|+5.6%*|+12.0%|+2.2%|+8.4%|
|Helsinki|1,165|+0.8%|+0.6%|+6.4%*|+12.7%*|

`*` resolved in favour of ANKYRA-X; no interval excludes zero against it. The BDG2 hourly contrast against ANKYRA (−10.4%) has a wide
interval and is driven by the near-zero meters. File: `results/carrier_swap_x.csv` (intervals included).
