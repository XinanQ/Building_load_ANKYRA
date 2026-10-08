# Results data

Most files describe **ANKYRA 2.2** (2.1 with gap tolerance in the pseudo-origin bookkeeping; the 2.1 files are in [`ankyra_2_1/`](ankyra_2_1/)),
including the files of the frozen-model checks. Files not re-exported for 2.2 keep the version they were measured on:
the three carrier-swap files (`carrier_swap.csv`, `carrier_swap_x.csv`, `carrier_swap_combined.csv`),
`component_contributions.csv`, `constants_sensitivity.csv`, `robustness.csv` and `intervals_winkler_contrasts.csv` were
measured with 2.1 (gap tolerance off; the Winkler file also has 2.0.1 and 2.0.0 rows), `cost_per_window.csv` with
2.0.0 and `handover_granularity.csv` with 1.x, and `bdg2_micro_load_windows.csv` compares 2.0.0 with 2.0.1. The two
experiments added afterwards, `long_context_carriers.csv` and `generic_combinations.csv`, use 2.2. `hkust_*`, `helsinki_*` and `lcl_*` were first scored with the frozen
2.0.1; the files here re-read the same targets with 2.2 (re-evaluations; the verdicts are those of the first scoring,
except two HKUST contrasts noted in its entry), the 2.1 re-readings are in [`ankyra_2_1/`](ankyra_2_1/) and the 2.0.1
versions in [`ankyra_2_0_1/`](ankyra_2_0_1/). `unicon_*` was the external test of the frozen 2.1 (those files are in
`ankyra_2_1/`); the files here re-read the same targets with 2.2, with the same verdicts. Where a file also
carries 2.0.1, 2.0.0 or 1.x, or was measured on an earlier version, its entry says so. Earlier versions, scored on the
same windows, are kept unchanged: the full 2.0.1 result set (including the reproduction record of package 2.0.3 and
the LCL arithmetic re-check `lcl_audit.json`) in [`ankyra_2_0_1/`](ankyra_2_0_1/), 2.0.0 in
[`ankyra_2_0_0/`](ankyra_2_0_0/) and 1.x in [`ankyra_1x/`](ankyra_1x/).

**Changed on 6 October 2026.** The CSV and JSON files in this directory were re-exported for ANKYRA 2.2 (gap
tolerance in the pseudo-origin bookkeeping; the forecaster is otherwise 2.1), except the files listed above as
measured on an earlier version and two version-free files (`datasets.csv`, `closeout_status.json`); those were not
re-exported and are identical to their copies in `ankyra_2_1/`, where the 2.1 versions of all files are kept. Each
entry below says which version a file was measured on. New summary: `reevaluation_2_2.json`. Earlier the same day: new
`unicon_external.csv`, `unicon_criteria.json`, `unicon_by_day.csv`,
`lcl_by_day.csv`, `component_contributions.csv`, `constants.csv`. Then 2.1 (2.0.1 versions in `ankyra_2_0_1/`):
`hkust_first_read.csv`, `hkust_by_day.csv`, `helsinki_confirmation.csv`, `helsinki_criteria.json`,
`helsinki_by_day.csv` and the `lcl_*` files (`lcl_metric_definitions.json` is version-free and unchanged). Moved:
`lcl_audit.json`, a record of the 2.0.1 scoring, to `ankyra_2_0_1/`. Figure 18 no longer exists: its per-day curves of
HKUST and Helsinki are panels of Figures 9 and 9b, with LCL and UNICON. **Added afterwards** (ANKYRA 2.2):
`long_context_carriers.csv` and `generic_combinations.csv`
([below](#long-context-foundation-models-and-generic-combinations)).

- **What differs from 2.0.1.** The within-day block and everything computed from the delivered trajectory: hourly
  errors, ranks, intervals, the trajectory peak, and delivered energy where the projection onto nonnegative load binds.
  Level, daily means, handover, energy readout and the off-state and micro-load rules are bit-identical. The single
  trust was chosen after all twelve populations had been scored with 2.0.1, so every 2.1 number is a re-evaluation.
- **What 2.0.1 changed from 2.0.0.** Only rows of BDG2 and aggregates that include BDG2. The micro-load rule returns the
  TimesFM forecast when the whole 1,344-hour context stays within 10⁻³ kW of zero. It changes 46 windows of nine
  meters at one BDG2 site and no forecast of the other nine populations.
- **Status of the BDG2 rows.** The rule was written after the BDG2 test result of 2.0.0 had been seen. The BDG2 rows
  describe what the rule changes; they are not a test of it
  ([details](../docs/EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)).

The files hold the scored statistics behind the figures and tables. They were exported from the study's evaluation
outputs. Raw data, saved forecasts, model weights and the code of the trained baselines are not in the repository.

- Three changes were made to the forecaster after the test populations were first scored (for 1.x): the within-day
  anchoring of 2.0, whose numbers are a re-evaluation under a frozen protocol, the micro-load rule above, and the
  single within-day trust of 2.1, chosen after all populations had been scored with 2.0.1
  ([details](../docs/EVALUATION.md#populations-and-tiers)).
- Nothing was tuned on the exported statistics.
- Files marked *descriptive* were computed after scoring, from the scored forecasts.
- GBT-T appears in its corrected implementation, re-scored after a defect in its scaling was found
  ([details](../docs/EVALUATION.md#correction-of-the-gbt-t-baseline)).
- The LCL households are a separate family of files (`lcl_*`, [below](#lcl-households)). They are not part of the
  ten-population tables or ranks; their per-day curves (`lcl_by_day.csv`) are a panel of Figures 9 and 9b, as are
  those of HKUST, Helsinki and UNICON ([below](#checks-with-the-forecaster-frozen)).

## Words used in every file

| Column or word | Meaning |
|---|---|
| `set` | Population, named as in `datasets.csv`. |
| `tier` | `test`, `preview` or `reserved`; defined under [Populations](#populations). |
| window | One forecast: 744 hours (31 days) after an origin, made from the 1,344 hours (8 weeks) before it. |
| unit | One meter, building, household or aggregate series. |
| `subset` | `full`: all windows. `late`: windows whose origin lies after the training cutoff of the trained baselines; only there do all 21 forecasters exist. In `bdg2_micro_load_windows.csv` the values are `early` (origin before the cutoff) and `late`. |
| `windows`, `units` | Number of windows and units scored in the row. |
| `model`, `model_label`, `model_class` | Key, readable name and class of a forecaster; see [Forecasters](#forecasters). |
| `log_ratio` | Unit-equal log RMS ratio: the mean over units of log(RMS error of ANKYRA / RMS error of the other forecaster), each RMS taken over the unit's hourly errors. Negative favours ANKYRA. A few files compare other pairs; their entries say which. |
| `um_low`, `um_high` | 95% interval of `log_ratio` from 2,000 bootstrap draws that resample units and target months independently. A contrast is *resolved* when the interval excludes zero. |
| `improvement_pct` | `100[1 − exp(log_ratio)]`. Positive favours ANKYRA. |
| `pooled_mse_ratio` | Ratio of the two mean squared errors over all windows. Units with large loads weigh more; it can differ in sign from `log_ratio`. |
| `unit_set` | BDG2 only. `all units`, or `without the three near-zero meters`: three meters that read near zero in every window and dominate the BDG2 unit means. |
| pseudo-origin | An earlier origin, 744 hours or a multiple before the real one, at which the forecaster is run on past data to measure its own error. |
| handover | The weight, per unit and forecast week, between TimesFM's daily means and those of the unit's history ([Method](../docs/METHOD.md#week-by-week-handover)). |
| level, daily path, within-day | The three blocks of a forecast: its monthly mean, the daily means minus that mean, and the hours minus their daily mean ([Method](../docs/METHOD.md#three-orthogonal-blocks)). |

### Forecasters

| `model` | Forecaster | `model_class` |
|---|---|---|
| `ANKYRA` | ANKYRA 2.2 | blank |
| `ANKYRA-21` | ANKYRA 2.1 (no gap tolerance) | `ANKYRA 2.1, earlier version` |
| `ANKYRA-201` | ANKYRA 2.0.1 (within-day trust per lead block) | `ANKYRA 2.0.1, earlier version` |
| `ANKYRA-200` | ANKYRA 2.0.0 (no micro-load rule) | `ANKYRA 2.0.0, earlier version` |
| `ANKYRA-1x` (`ANKYRA 1.x` in `block_shares.csv`) | ANKYRA 1.x (no within-day anchoring, no micro-load rule) | `ANKYRA 1.x, earlier version` |
| `F1` | The 1.x forecaster without the off-state rule | — |
| `F0` | The fixed division of labour: historical level and daily path with the TimesFM within-day shape; no handover, no off-state rule | — |
| `TiDE`, `iTransformer-X`, `GBT-T` | Trained per population (`GBT-T`: trained gradient boosting) | `same information, trained` |
| `Chronos-2-X`, `TimesFM-X` | Foundation models with covariates, used without training (zero-shot) | `same information, zero-shot foundation model` |
| `TimesFM`, `Chronos-2` | TimesFM 2.5 and Chronos-2 on load alone, zero-shot | `load only, zero-shot foundation model` |
| `DLinear`, `PatchTST`, `iTransformer`, `LSTM` | Trained per population | `load only, trained` |
| `Holt-Winters`, `MSTL` | Statistical models | `load only, statistical` |
| `RIDGE-L` | Per-unit ridge regression on the calendar and climatological temperature, refitted at every origin | `per-unit regression` |
| `GBT` | A zero-shot gradient-boosting model | `zero-shot gradient boosting` |
| `SP-profile`, `LYR-profile`, `WeekProf4` | Previous-month, last-year and 4-week profiles | `profile` |
| `SN-day`, `SN-week` | Seasonal naive forecasts with a period of one day and one week | `naive` |

- `same information`: the model is given ANKYRA's 11 past, 10 future and 6 static features, and uses the part its
  architecture accepts.
- `load only`: the model receives the 1,344-hour load context only.
- The 21 forecasters of the late windows are ANKYRA and the 20 baselines of the last nine rows.
- The off-state rule returns the TimesFM forecast when the last 168 hours before the origin are all at most 10⁻⁶ kW
  ([Method](../docs/METHOD.md#off-state-and-micro-load-rules)).

## Populations

**`datasets.csv`** lists the eleven populations.

- `set`, `country`, `population` (kind of unit).
- `tier`:
  - `test`: six populations, scored once after all model development for 1.x had ended;
  - `preview`: four populations scored earlier and used for diagnosis;
  - `reserved`: the LCL households. They were held out of the ten-population comparison and scored once afterwards
    with the frozen 2.0.1 forecaster (the `lcl_*` files).
- `ankyra_design_status`:
  - `seen`: results of the population were known when some component of ANKYRA was specified;
  - `first read`: the population was scored for the first time after the handover had been fixed.
- `units`, `windows`: all windows. `units_late`, `windows_late`: late windows. For LCL the late counts are the 710
  windows on which all trained baselines have a forecast.

BDG2 is a test population for the 2.0.0 forecaster. Its 2.0.1 and 2.1 rows include the micro-load rule, written after
its result was seen. The 1.x result on LCL was known before 2.0.1 was scored there, so LCL is `seen` and is not an
unexposed population. The three populations of the frozen-model checks (HKUST, Helsinki, UNICON) are not in
`datasets.csv`; they are described in [DATA.md](../docs/DATA.md#populations-scored-with-the-forecaster-frozen).

## The main comparison

**`benchmark_pairwise.csv`** — ANKYRA against each of the 20 baselines, per population and `subset`. Columns: `set`,
`tier`, `subset`, `windows`, `units`, `model`, `model_label`, `model_class`, `log_ratio`, `um_low`, `um_high`,
`improvement_pct`, `pooled_mse_ratio`. Figures 2 and 3.

**`benchmark_mean_unit_rank.csv`** — Mean per-unit rank of ANKYRA and each baseline. Forecasters are ranked within each
unit by RMSE, with each RMSE rounded to 12 decimals and tied ranks averaged; `mean_unit_rank` is the mean over units.
`n_models` is the number of forecasters ranked: 21 on `late`, 13 or 14 on `full`, where the trained models have no
forecast. Columns: `set`, `tier`, `subset`, `model`, `model_label`, `mean_unit_rank`, `n_models`. Figures 2, 8, 11
and 12.

**`rank_tests.csv`** — Rank tests on the per-unit RMSE of the 21 forecasters, late windows, per population and for
the six test populations pooled. Descriptive. Figure 15.

- `units`: number of units (the blocks of the test).
- `mean_rank`: mean per-unit rank.
- `friedman_p`: p-value of Friedman's test of equal ranks. `0` means smaller than the smallest number the format can
  hold (below 10⁻³⁰⁰).
- `nemenyi_cd`: Nemenyi critical difference of mean ranks at 5%.
- `wilcoxon_holm_p_vs_ankyra`: Holm-corrected p-value of the paired Wilcoxon signed-rank test of ANKYRA against the
  forecaster; blank on the ANKYRA row.
- **`mean_rank` here and `mean_unit_rank` in `benchmark_mean_unit_rank.csv` handle ties differently.** This file ranks
  the unrounded RMSE values; the other file rounds them to 12 decimals first. The two agree to rounding on nine
  populations. On BDG2 they differ for nine baselines by up to 0.06 (MSTL: 14.053 here, 13.993 there). On the
  near-zero meters several baselines have errors that are equal after rounding but not exactly, so they share a rank
  in one file and not in the other. ANKYRA's rank agrees to rounding in both (4.408 and 4.4085).

**`conventional_metrics.csv`** — Conventional errors on all windows for ANKYRA, 2.1 (`ANKYRA-21`), 2.0.1 (`ANKYRA-201`), 2.0.0
(`ANKYRA-200`), 1.x (`ANKYRA-1x`) and the forecasters that exist on all windows. Columns: `set`, `tier`, `model`, `RMSE_kW` and `MAE_kW`
(mean over units, kW), `CV_RMSE_pct`, `NMBE_pct` and `WAPE_pct` (median over units, %), `WAPE_pooled_pct` (pooled over
all windows, %).

**`conventional_metrics_late.csv`** — The same metrics on the late windows for all 21 forecasters, with 2.1, 2.0.1, 2.0.0 and 1.x
as extra rows. Additional columns: `windows`, `units`, `model_label`, `model_class`, and `units_excluded`, the number
of units with a mean load below 10⁻⁶ kW, which are left out of the ratio metrics. Figure 8.

**`scaled_errors.csv`** — RMSSE and MASE of the 21 forecasters on the late windows. Each window's error is divided by
the in-sample error of the weekly seasonal-naive forecast (lag 168 h) over its 1,344-hour context. Descriptive.

- `RMSSE_median_unit`, `RMSSE_geo_mean`, `MASE_median_unit`, `MASE_geo_mean`: median and geometric mean over units.
- `units`: units with at least one window whose scale is not zero. Windows with a zero scale are left out, which
  removes 8 of 142 units on BDG2 and 47 of 197 on EWELD.
- `units_below_1_share`: share of those units whose RMSSE is below 1.

## Error by forecast day and energy

All files of this section are descriptive and cover the late windows.

**`lead_day_metrics.csv`** — Hourly error by forecast day (1–31) for all 21 forecasters on the six test sets and the
Suzhou park. Pooled over the month it gives back the scored metrics. Figures 9 and 10.

- `RMSE_kW`, `MAE_kW`: mean over units, kW. `CV_RMSE_pct`, `nMAE_pct`: median over units, % of the unit's mean load.
- `GM_CV_RMSE_pct`: geometric mean, over one fixed set of units, of each unit's RMSE on that day in % of its mean
  load. The fixed set holds the units with a nonzero mean load and a nonzero error on every day for every forecaster.
- `n_units_gm`: size of that set (the same quantity as `units_in_U` in the next two files).
- Other columns: `set`, `tier`, `windows`, `units`, `model`, `model_label`, `model_class`, `day`.

**`lead_day_energy.csv`** — Energy error by forecast day for the same forecasts. Figure 9b.

- `GM_CV_daily_energy_pct`: error of the energy of day d. `GM_CV_cumulative_energy_pct`: error of the energy delivered
  from day 1 through day d; on day 31 it is the monthly energy error. Both are RMS errors over a unit's windows in %
  of its mean load, as geometric means over a fixed unit set.
- `units_in_U`: size of that set. It also requires nonzero daily and cumulative energy errors, so it is smaller than
  `n_units_gm` on the two GoiEner populations (435 and 577 units against 453 and 598).
- Other columns: `set`, `tier`, `windows`, `model`, `model_label`, `model_class`, `day`.

**`ankyra_2_vs_1x_by_day.csv`** — The `GM_CV_RMSE_pct` curve of `lead_day_metrics.csv` (same definition, same fixed
unit set, three decimals) for ANKYRA 2.2, 2.1, 2.0.1, 2.0.0, 1.x and the four foundation-model variants on the six test
sets. Columns: `set`, `day`, `units_in_U`, then one column per forecaster: `ankyra_2_2`, `ankyra_2_1`, `ankyra_2_0_1`, `ankyra_2_0_0`,
`ankyra_1x`,
`TimesFM`, `Chronos-2`, `Chronos-2-X`, `TimesFM-X`.

**`energy_error.csv`** — Monthly energy error of ANKYRA against each of the 20 baselines on the six test sets and the
Suzhou park. The energy error of a window is 744 × the error of its mean load (property P3 in
[theory](../theory/PROOFS.md)). `log_ratio`, `um_low`, `um_high` and `improvement_pct` are the unit-equal contrast on
that error. `median_energy_ape_pct` is each forecaster's median-unit absolute percentage energy error. `unit_set`:
BDG2 is given on all units (474 windows, 142 units) and without the three near-zero meters (464 windows, 139 units);
the other populations on all units. Other columns: `set`, `tier`, `windows`, `units`, `model`, `model_label`,
`model_class` (blank on the ANKYRA row, which is the reference and reads zero). Figure 11.

**`block_shares.csv`** — Where the hourly squared error sits, on the six test sets and the Suzhou park. Figure 14.
One row per `set`, `model`, `quantity` and `block`, with the number in `value`.

- `block`: `level`, `daily path`, `within-day`, or `hourly` (the total).
- For `model` = `ANKYRA`, `ANKYRA 1.x`, `TimesFM`, `Chronos-2-X`: `quantity` is `pooled_share` (the block's share of
  the forecaster's squared error pooled over windows) or `median_unit_share` (the median over units of that share).
- For `model` = `ANKYRA vs TimesFM` and `ANKYRA vs Chronos-2-X`: `quantity` is `improvement_pct` or `log_ratio` of
  ANKYRA against that model within the block, or `units_in_ratio`, the number of units in the contrast.

## Design choices

**`ablation.csv`** — ANKYRA 2.2 against its reduced versions, on all windows of the ten populations. Columns: `set`,
`tier`, `ablation`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`. Figure 4a. The six values of `ablation`:

- ANKYRA 2.1 (without gap tolerance): −0.03% to 0.32%, resolved on no population; bit-identical to 2.2 on Oslo,
  CINELDI and the Suzhou park;
- ANKYRA 2.0.1 (within-day trust per lead block): 0.00–0.45%, resolved in favour of 2.2 on Oslo and Drammen only;
- ANKYRA 2.0.0 (without the micro-load rule, trust per lead block): equal to the 2.0.1 row on every population except
  BDG2;
- ANKYRA 1.x (foundation within-day block, no anchoring);
- F1 (the 1.x forecaster without the off-state rule);
- F0 (the fixed division of labour).

F1 and F0 are forecasters of the 1.x period, so like 1.x they lack the within-day anchoring. Where the off-state rule
never fires, the F1 row equals the 1.x row. None of the last three reduced versions carries the micro-load rule, so on BDG2 the
last three contrasts include it; their 2.0.0 values are in `ankyra_2_0_0/ablation.csv` and their 2.0.1 values in
`ankyra_2_0_1/ablation.csv`.

**`component_contributions.csv`** — What each part of the forecaster adds, on all windows of the ten populations,
hourly error. Re-evaluations of populations already read; computed on 2.1 (gap tolerance off) and not recomputed for
2.2 (no gap-tolerance step is included)
([details](../docs/EVALUATION.md#what-the-parts-buy)). Columns: `set`, `component`, `improvement_pct`, `log_ratio`,
`um_low`, `um_high`, `kind`. Positive = the later version (or the first-named arm) is better. The values of
`component`:

- the five steps of the chain of `ablation.csv`: `handover of the daily means (F0 -> F1)`, `off-state rule (F1 -> 1.x)`,
  `within-day anchoring (1.x -> 2.0.0)`, `micro-load rule (2.0.0 -> 2.0.1)`, `one within-day trust value (2.0.1 -> 2.1)`;
  the first four are `difference of two contrasts (point estimate)`, the log ratio of 2.1 against the earlier version
  minus that against the later one, with blank interval; the fifth is a direct contrast;
- `all steps (F0 -> 2.1)`: 2.1 against the fixed division, a direct contrast;
- `block-wise weights vs one whole-window combination weight of the same two forecasts (B2)`: ANKYRA 2.1 against a
  combination of its history-side forecast and TimesFM with one least-squares weight per unit, shrunk towards ½;
- `weekly vs monthly handover weights`: the weekly handover against one weight per unit and month, from the
  simplification study, measured against 2.0.1 (`kind` says so).

**`constants.csv`** — Every constant of the forecaster, 20 rows: `group` (problem definition, evidence window, shrinkage,
analog shape and readout, numerical safeguard, data-state rule, frozen historical estimator), `constant`, `value`, `where_fixed` (the data or design step on
which it was fixed) and `sensitivity` (where measured, the largest change of the nine-set mean log ratio over the
values tried, from `constants_sensitivity.csv`; blank where no sensitivity run exists). The `group` column and the rows for the short-gap rule and the climatology were added on 7 October 2026; the values are
those of package 2.2.0 (unchanged).

**`handover_granularity.csv`** — An ablation of the handover on the ten populations, specified before it was run. It
is a record of 1.x; the handover is unchanged since. Four arms: ANKYRA's weekly per-unit weights (`AW`), a fixed half
mixture (`Ah`; A½ in the documents), one weight per unit and month (`AM`) and no handover (`A0`). Columns: `set`, `tier`, `contrast`, `log_ratio`, `um_low`,
`um_high`, `improvement_pct`, `pooled_mse_ratio`; the first arm named in `contrast` is the numerator. `C1`–`C4` number
the four contrasts fixed before the run, of which `C1` and `C2` are also given by forecast week. The rows without a
number (each arm against TimesFM, `AW` and `AM` against `A0`) are descriptive. Figure 4b.

**`lead_weeks_first_read.csv`** — Contrasts against TimesFM by forecast week (1–4) on the three populations scored
first after the handover was fixed (Cambridge, CINELDI, HEEW). Figure 4c and 4d.

- `ankyra_vs_timesfm_log_ratio`: ANKYRA 2.2 (the 2.1 values are in `ankyra_2_1/`; 2.0.0 and 2.0.1 were identical to
  each other, their values are in `ankyra_2_0_1/`).
- `ankyra_1x_vs_timesfm_log_ratio`: ANKYRA 1.x. `fixed_division_vs_timesfm_log_ratio`: F0.
- `mean_weight_on_model`: the mean estimated weight on TimesFM's daily means in that week.

**`history_length.csv`** — ANKYRA against TimesFM, ANKYRA 1.x and F0 (`comparator`) by the length of the unit's
history at the origin, per population and pooled (`all ten populations`); all windows. Descriptive. Columns: `set`,
`stratum`, `windows`, `units`, `comparator`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`.

- Strata by hours since the unit's first observation: `< 10,248 h (no annual candidate)`, `10,248 h - 2 years`,
  `2-3 years`, `>= 3 years`.
- Strata by `K_eff`, the number of complete 744-hour pseudo-origin windows the history allows, capped at 12:
  `K_eff 6-8`, `K_eff 9-11`, `K_eff 12`.

**`constants_sensitivity.csv`** — One shrinkage constant changed at a time and the forecaster re-scored on the nine
design sets only: the three development populations (Oslo, Drammen, the GoiEner development store) and the pre-cutoff
windows of the six test populations. No test window is used.

- `constant`: `handover K0` and `within-day K0` (shrinkage constants), `handover pairs` and `within-day pairs` (number
  of pseudo-origins), `within-day cap` (largest within-day trust weight). `value`: the value tried.
- `is_ankyra_value`: `True` on the row of the value ANKYRA uses. That row is the reference and reads zero.
- `nine_face_mean_log_ratio`: mean over the nine design sets of the hourly unit-equal log ratio of the variant against
  ANKYRA; negative is better than ANKYRA. `face` in the column names means design set.
- `worst_face`, `worst_face_log_ratio`: the design set with the largest ratio, and that ratio. In the 2.1 file the
  set is named by its internal key: `bdg2_early`, `eweld_early`, `households_early` (pre-cutoff windows of those test
  populations), `oslo_all`, `goiener_dev_all` (the GoiEner development store). The reference is ANKYRA 2.1. `best_face_log_ratio`:
  the smallest ratio. On the reference rows the named set has no meaning.
- Micro-load windows return the TimesFM forecast in the reference and in every variant.

## Readouts and intervals

**`peak_readout.csv`** — ANKYRA's peak readout (the peak operator on its daily means) against four alternatives
(`comparator`), on all windows of the ten populations: `trajectory maximum` (the maximum of ANKYRA's own trajectory),
`same readout on TimesFM`, `same readout on fixed division (F0)`, and `previous-window peak` (last month's observed
peak). `log_ratio`, `um_low`, `um_high`, `improvement_pct` are the unit-equal contrast on the absolute peak error.
`median_peak_ape_ankyra_pct` and `median_peak_ape_previous_peak_pct` are the median-unit absolute percentage peak
errors of the readout and of last month's peak; they repeat on the rows of a population. Figure 5.

**`intervals_households.json`** — The interval on GoiEner households (1,258 windows, 1,109 units). Figure 13.

- `arms`: `ours_around_ANKYRA` and `ours_around_F0` are the interval built from pseudo-origin residuals, centred on
  ANKYRA and on the fixed division; `timesfm_native` and `chronos_native` are the models' own quantiles.
- Per arm: `cov80`, `cov90` (coverage, a fraction), `width80`, `width90`, `winkler80` (Winkler score at 80%) and
  `pinball_*` (pinball losses), all means in kW. `pinball_mean_common` is the mean over the quantiles all arms
  provide (0.1, 0.5, 0.9). TimesFM has no 0.05 and 0.95 quantiles.
- `contrasts`: `log_ratio`, `UM` (the 95% unit-and-month bootstrap interval of the log ratio) and `pct` (improvement
  in %) of the ANKYRA interval against each other arm.

**`intervals_by_population.csv`** — The same interval and the native quantiles of TimesFM 2.5 and Chronos-2 on all
windows of the ten populations. Descriptive. Figure 16.

- `arm`: `ankyra_2_0` (the interval around the 2.2 trajectory; the name is from 2.0), `chronos_native`,
  `timesfm_native`.
- `cov80`, `cov90`: coverage, a fraction; `cov80_week1`–`cov80_week4` and `cov90_week1`–`cov90_week4` by forecast week.
- `width80`, `width90`, `winkler80`, `winkler80_week1`–`winkler80_week4`, `pinball_0.05`–`pinball_0.95`,
  `pinball_mean_common`: means in kW. The 90% columns and the 0.05 and 0.95 pinball losses are blank for TimesFM.
- On EWELD the width and the Winkler score of the ANKYRA interval are of the order of 10⁶ kW and carry no information:
  units that switch off produce enormous quantiles. The interval should not be used for such units.
- Other columns: `set`, `tier`, `units`, `windows`.

**`intervals_winkler_contrasts.csv`** — Unit-equal Winkler contrasts of the ANKYRA interval against `timesfm_native`
and `chronos_native` (`comparator`) on the ten populations, for `version` 2.1, 2.0.1 and 2.0.0 (no 2.2 row; the file
is unchanged). Columns: `version`, `set`,
`comparator`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`.

## BDG2 and the micro-load rule

**`bdg2_near_zero_sensitivity.csv`** — The BDG2 contrasts with and without the three meters that are near zero in
every window. Columns: `unit_set`, `subset`, `model`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`,
`ankyra_mean_unit_rank`. The rows include ANKYRA 2.1 (`ANKYRA-21`), 2.0.1 (`ANKYRA-201`), 2.0.0 and 1.x as `model`. `ankyra_mean_unit_rank` is ANKYRA's mean
per-unit rank on that unit set and subset, repeated on each row.

- Under 2.0.1, 2.1 and 2.2 the three meters are handed to TimesFM and still dominate the BDG2 unit means.
- In the rows without them the point estimates of 2.0.1 and 2.0.0 agree (late windows to 0.01 points, all windows to
  0.03). Between 2.2 and 2.0.0 they differ by 0.28 points on the late windows and 0.45 on all windows, of which 0.27
  and 0.32 points are the gap tolerance (the 2.1 row) and the rest the within-day change. The intervals differ,
  because six further meters are handed over in some windows; three late contrasts are
  resolved only with the rule (2.0.1, 2.1 and 2.2).

**`bdg2_micro_load_windows.csv`** — The 46 BDG2 windows the micro-load rule changes, one row each. Descriptive.
Columns: `meter`, `target_month`, `subset` (`early` or `late`), `context_max_kw` (largest load in the context),
`realised_mean_kw`, `realised_max_kw`, `meter_resumes_in_window`, and the mean forecast and RMSE of both versions
(`forecast_mean_2_0_0_kw`, `forecast_mean_2_0_1_kw`, `rmse_2_0_0_kw`, `rmse_2_0_1_kw`). In 41 windows the meter stays
near zero. In 5 it resumes, and there 2.0.0 is marginally better. 2.1 and 2.2 return the same TimesFM forecast on these
windows, so the 2.0.1 columns also describe 2.1 and 2.2.

## Robustness, cost, example, reproduction

**`robustness.csv`** — Stress test on 64 Drammen windows (a development population): the context is corrupted, the
targets are not. Measured on 2.1 (gap tolerance off) and not re-run for 2.2; EVALUATION.md notes that these Drammen
records have no qualifying gaps (the earlier measurement, on 2.0.0, is in `ankyra_2_0_0/` and `ankyra_2_0_1/`). One
row per `corruption`:

- `miss05`, `miss20`: 5% or 20% of the context hours removed and filled by linear interpolation;
- `zero24`: a 24-hour block of zeros in the last week;
- `spike`: one hour at 10 times the context maximum, 36 hours before the origin;
- `shift_plus1`, `shift_minus1`: the context shifted by one hour;
- `scale0.5`, `scale2`: the whole history multiplied by 0.5 or 2 (the forecast is scaled back before comparing).

Columns:

- `ankyra_error_vs_clean_log_ratio`, `timesfm_error_vs_clean_log_ratio`: unit-equal log ratio of the hourly error
  with the corrupted context to the error with the clean context; positive is worse.
- `ankyra_windows_worse_share`, `timesfm_windows_worse_share`: share of the 64 windows whose error grew.
- `ankyra_displacement_over_s0_median`, `timesfm_displacement_over_s0_median`: median over windows of the RMS change
  of the forecast, in units of the unit's normalisation scale `s0`.
- `level_change_pct_median`, `level_change_pct_max`: median and largest absolute change of ANKYRA's level, in %.
- `peak_readout_change_pct_median`: median change of the peak readout, in %. `peak_error_vs_clean_log_ratio`: log
  ratio of its error to the clean case.
- `off_state_fired`: number of windows in which the off-state rule fired (0 in every row).
- `ankyra_vs_timesfm_corrupted_log_ratio`: ANKYRA against TimesFM, both on the corrupted context.
- `equivariance_max_rel_dev`: scale rows only; the largest relative deviation from exact scale equivariance.

**`cost_per_window.csv`** — Timings on one laptop GPU, measured on 2.0.0 (the micro-load rule adds one maximum over
the context; the single trust of 2.1 adds no computation and was not timed separately). Columns: `item`, `value`, `unit`. The unit is `s/window` (seconds per 744-hour window) for the
forecasters and their components, `s` for the two model loads (once per session) and `GiB` for peak GPU memory.
"Evaluated configuration" is the TimesFM setting used in the study (per-core batch 1). The `component:` rows are the
parts of the totals above them; four of them repeat a total that has a single part.

**`example_window_cambridge.csv`**, **`example_window_cambridge.json`** — One Cambridge test window (University of
Cambridge estate archive, CC BY 4.0), used in Figures 6 and 7. The CSV has `hour` (0 is the origin; negative hours are
the 1,344-hour context), `load_kw`, and from hour 0 on `timesfm_kw` and `ankyra_kw`. The JSON has the building, the
forecast period, the day types of the context and target days (Monday 0 … Sunday 6, holiday 7) and the source.
`ankyra_kw` is the 2.2 forecast (the 2.1 forecast is in `ankyra_2_1/`, the 2.0.1 forecast in `ankyra_2_0_1/`).

**`REPRODUCTION_CHECK.json`** — The check of the current package (2.2.0; PASS) against the evaluated
forecasts on 484 windows of seven populations,
including every micro-load window of BDG2 and of the EWELD late windows (263 in all).

- `faces`: the window sets checked. `households` = GoiEner households, `goiener_confirm` = GoiEner non-household,
  `park` = Suzhou park; the suffixes `_late`, `_early`, `_all` name the subset.
- `max_rel_diff_2_1_vs_panel`: the package with `gap_tolerance=False` against the scored 2.1 forecasts (largest 7.4×10⁻⁸).
  All legacy modes below also run with `gap_tolerance=False` (field `criterion`).
  `daily_means_2_1_equal_2_0_1_and_one_trust`: the level and daily means of 2.1 are bit-identical to 2.0.1 and the four
  trust entries are equal. `micro_windows_2_1_equal_timesfm`: 2.1 returns the TimesFM forecast on every micro-load
  window. `median_seconds_cpu_side_2_1`: CPU time of the 2.1 call in this check, not a benchmark.
- `windows_with_complete_history`, `2_2_identical_to_2_1_on_windows_with_complete_history`,
  `windows_2_2_differs_from_2_1`: on every checked window whose history has no gap the 2.2 forecast is bit-identical
  to the 2.1 forecast (true on all eight sets); the last key counts the windows on which the two differ (53 of the
  484).
- `max_rel_diff_2_0_1_vs_panel`: the package with `gap_tolerance=False, single_trust=False` against the scored 2.0.1 forecasts ("panel" is the set of scored
  forecasts behind the tables). `max_rel_diff_2_0_0_mode`: the package with `gap_tolerance=False, single_trust=False, micro_load_rule=False` against the stored
  2.0.0 forecasts named in `v6_reference` ("v6" was the working name of the 2.0 forecaster).
  `max_rel_diff_2_0_0_mode_vs_panel_arm`: the same mode against the 2.0.0 rows of the 2.0.1 scoring. All agree to
  float32 precision, the precision of the stored forecasts.
- `max_abs_diff_1x_mode_kw`: the 1.x mode (`gap_tolerance=False, within_anchor=False, micro_load_rule=False`) against the
  evaluated 1.x forecasts, in kW.
- On micro-load windows 2.1 and 2.0.1 are bit-identical to the TimesFM forecast; elsewhere the 2.0.1 mode is
  bit-identical to the 2.0.0 mode.
- `package_files`: SHA-256 of the eight top-level modules of `ankyra/` as stored in the repository (LF line endings).
  The files under `ankyra/history/` are not listed; for eight of them see the note below.

**`REPRODUCTION_CHECK_2_0_1.json`** — the same check on the 2.0.1 package (4 October 2026); its `package_files` are the
hashes of the modules at that time, three of which (`__init__.py`, `analog.py`, `core.py`) have changed since.

The record of package 2.1.0 is `ankyra_2_1/REPRODUCTION_CHECK.json`. The record of package 2.0.3 (model 2.0.1) is `ankyra_2_0_1/REPRODUCTION_CHECK.json`; `ankyra_2_0_1/` also holds a copy
of `REPRODUCTION_CHECK_2_0_1.json`. The 2.0.0 and 1.x records are `ankyra_2_0_0/REPRODUCTION_CHECK.json` and
`ankyra_1x/REPRODUCTION_CHECK.json`.

**`reevaluation_2_1.json`** — The ANKYRA 2.1 re-evaluations of the three frozen-model checks of 2.0.1: LCL (against
matched-input 1.x and TimesFM on all and late windows, mean per-unit rank on the late windows, the same-information
check, the readouts, and 2.1 against 2.0.1), HKUST (hourly and energy contrasts, the added comparators, the mean unit
rank among 14 and the days on which ANKYRA is lowest) and Helsinki (both criteria, all contrasts, the mean unit rank
among 14). The same targets are read again with the 2.1 forecasts; these are re-evaluations, not tests. The 2.1
versions of the `lcl_*`, `hkust_*` and `helsinki_*` files are in `ankyra_2_1/`; this file is kept as their summary, and the
2.0.1 files of the first scoring are in `ankyra_2_0_1/`. `UM` and `um_low`, `um_high` are 95% unit-and-month
intervals in log units.

**`reevaluation_2_2.json`** — The same summary for ANKYRA 2.2 (same layout; the LCL block adds `2.2_vs_2.1`). Its
numbers are those of the `lcl_*`, `hkust_*` and `helsinki_*` files in this directory.

**Paths in the records.** `ankyra/history/provenance.json`, `ankyra/history/frozen_config.json` and the reproduction
records name files of the study's private working repository (for example `tools_*.py`, `recovery/…`,
`analysis_outputs/…`) and its internal labels ("v6", "round-2"). These files are not distributed; the paths
record where each value came from, and the hash-locked files are kept as they were.

**Line endings and the older hashes.** The hashes in `ankyra/history/provenance.json` and those of eight files under
`ankyra/history/` in `ankyra_1x/REPRODUCTION_CHECK.json` were taken on a Windows working copy with CRLF line endings.
The repository stores these files with LF. A hash computed on a checkout with LF endings therefore differs from the
recorded one, although the content is the same; with the line endings converted to CRLF the recorded values are
reproduced. The eight files are `_climate.py`, `_day.py`, `_eo.py`, `_level.py`, `_signature.py`, `_span.py`,
`frozen_config.json` and `provenance.json`.

## LCL households

The Low Carbon London (LCL) households were held out of the ten-population comparison. They were scored once with the
frozen 2.0.1 forecaster, and nothing was retuned. The `lcl_*` files hold ANKYRA 2.2, run afterwards on the same windows
(a re-evaluation; every check reads the same as under 2.0.1 and 2.1). The 2.1 files are in [`ankyra_2_1/`](ankyra_2_1/);
the 2.0.1 files, with the arithmetic re-check
`lcl_audit.json`, are in [`ankyra_2_0_1/`](ankyra_2_0_1/). The 1.x result on LCL had been seen earlier, so LCL is not
an unexposed population. The `lcl_*` files are a separate family: they are not merged into the ten-population tables
or ranks; `lcl_by_day.csv` is the LCL panel of Figures 9 and 9b ([details](../docs/LCL_AND_CLOSEOUT.md)).

- **Two window sets, not to be mixed.** `subset` = `full`: all 1,215 windows of 965 units. `subset` = `late`: the 710
  windows of 710 units after the training cutoff for which all seven trained baselines have a forecast. The set was
  chosen by window identity, not by any target or forecast value. On `full` the seven trained baselines (DLinear,
  GBT-T, iTransformer, iTransformer-X, LSTM, PatchTST, TiDE) have `status` = `not available` and blank numbers. A
  blank is not a zero and not a tie.
- **Two versions of 1.x.** `ANKYRA-1x-matched` is 1.x recomputed on the same input as 2.0.1. `ANKYRA-1x-archived` is
  the 1.x forecast made earlier. The inputs differ in the temperature before the start of the temperature record: it
  is now a constant 15 °C, where the earlier input had copied a later year. The difference between the two rows is
  therefore not all due to the forecaster.
- **Two checks set before scoring** (for the 2.0.1 scoring; they read the same for 2.1 and 2.2). The no-harm check: the upper
  end of the 95% interval of the log ratio of ANKYRA against `ANKYRA-1x-matched` must not exceed 0.01. It passes. The
  same-information check: six one-sided tests, Holm-corrected, of whether a baseline given ANKYRA's information (TiDE,
  iTransformer-X, GBT-T, Chronos-2-X, TimesFM-X and the per-unit ridge) is better than ANKYRA on the late windows.
  None is significantly better. This does not show equivalence, and it does not show that ANKYRA is better than all
  six.
- **What LCL does not test.** No LCL window triggers the micro-load rule (two windows trigger the off-state rule), so
  LCL says nothing about that rule. The interval was not assessed on LCL.
- The numbers are printed with full floating-point precision. The 2,000-draw bootstrap does not support that many
  digits.

| File | Content |
|---|---|
| `lcl_results.json` | The record: both window sets, mean ranks, the two checks, the readouts, the counts of off-state and micro-load windows, `2.1_vs_2.0.1` (2.1 against 2.0.1 on all windows) and `2.2_vs_2.1` (2.2 against 2.1 on all windows). All other blocks are 2.2; the CSV files below are extracts of it. The 2.1 record is `ankyra_2_1/lcl_results.json`, the 2.0.1 record `ankyra_2_0_1/lcl_results.json`. |
| `lcl_pairwise.csv` | ANKYRA against each baseline and both 1.x versions on `full`. |
| `lcl_pairwise_late.csv` | The same on `late`. |
| `lcl_mean_unit_rank_late.csv` | Mean per-unit rank of the 21 forecasters on `late`. The unrounded RMSE values are ranked and tied ranks averaged. The two 1.x versions are not ranked. |
| `lcl_shared_information_holm.csv` | The six tests of the same-information check. Here the ratio is the baseline over ANKYRA, the reverse of the pairwise files: a positive `log_ratio` means the baseline is worse. |
| `lcl_readouts.csv` | Energy and peak readouts of ANKYRA against the TimesFM trajectory on `full`. Descriptive; not used to select anything. |
| `lcl_conventional_metrics.csv`, `lcl_conventional_metrics_late.csv` | Conventional errors on `full` and on `late`. Descriptive. |
| `lcl_lead_day_metrics.csv`, `lcl_lead_day_metrics_late.csv` | Hourly, daily-energy and cumulative-energy error by forecast day on `full` and on `late`. Descriptive. |
| `lcl_metric_definitions.json` | Definitions for the four descriptive files above (version-free; unchanged). |
| `lcl_by_day.csv` | The LCL panel of Figures 9 and 9b: the 21 forecasters on the 710 late windows, with the definitions of those figures. Columns `model`, `model_label`, `day`, `hourly_gm_cv_pct`, `energy_to_date_gm_cv_pct`, `windows`, `units_in_fixed_set` (704 households whose errors are nonzero for every forecaster), as in `hkust_by_day.csv`. Descriptive. |

`lcl_audit.json`, the arithmetic re-check of the 2.0.1 scoring with a second implementation (96,032 comparisons, no
difference; not an independent review; the saved targets were opened once for scoring and once for the check), has
moved to [`ankyra_2_0_1/lcl_audit.json`](ankyra_2_0_1/lcl_audit.json). No such re-check of the 2.1 or 2.2 files is
recorded.

Columns of the pairwise, same-information and readout files:

- `set` (`LCL households`), `subset`, `windows`, `units`: the window set and its size.
- `model`, `model_label`: as in the main files, plus the two 1.x keys. `lcl_readouts.csv` has `readout` and
  `timesfm_reference` instead.
- `status`: `ok` or `not available`. `available_windows`: windows for which the model has a forecast. `units_scored`:
  units in the contrast.
- `direction`: which forecaster is the numerator of the ratio (`ANKYRA over model`, `model over ANKYRA`, or
  `ANKYRA readout over TimesFM trajectory readout`).
- `log_ratio`, `um_low`, `um_high`, `improvement_pct`, `pooled_mse_ratio`: as in the main files, for that direction.
- `bootstrap_one_sided_p_unadjusted`: one-sided bootstrap p-value for the hypothesis that the numerator is not better;
  not adjusted for the number of comparisons. `bootstrap_valid_draws`: draws used. `bootstrap_zero_draws`: draws in
  which a unit had exactly zero error (0 everywhere).
- `holm_p` (same-information file): the Holm-corrected p-value over the six tests.
- `readout` (readout file): `independent_energy` (744 × ANKYRA's level), `delivered_energy` (the sum of ANKYRA's
  hourly trajectory), `raw_peak` (the maximum of ANKYRA's trajectory), `envelope_peak` (ANKYRA's peak readout).
  `timesfm_reference`: `trajectory sum` or `trajectory maximum`. The `envelope_peak` row compares two different
  operators. `role` marks the rows as descriptive.

Columns of the other files:

- `lcl_mean_unit_rank_late.csv`: `set`, `subset`, `windows`, `units`, `model`, `model_label`, `mean_unit_rank`,
  `n_models`.
- `lcl_conventional_metrics*.csv`: `set`, `subset`, `windows`, `units`, `model`, `model_label`, `status`, then
  `RMSE_kW`, `MAE_kW`, `CV_RMSE_pct`, `NMBE_pct`, `WAPE_pct`, `WAPE_pooled_pct`, `units_excluded` as in
  `conventional_metrics_late.csv`.
- `lcl_lead_day_metrics*.csv`: `set`, `subset`, `windows`, `units`, `model`, `model_label`, `metric`, `day`,
  `units_total`, `units_eligible`, `zero_error_units`, `status`, `geometric_mean`, `arithmetic_unit_mean`,
  `unit_median`.
  - `metric`: `hourly_CV_RMSE_pct`, `daily_energy_CV_RMS_pct` or `cumulative_energy_CV_RMS_pct`, each in % of the
    unit's mean load over its scored windows.
  - `units_eligible`: units with a positive mean load. `zero_error_units`: units whose error on that day is exactly
    zero. They stay in; the geometric mean is then undefined, `status` reads `geometric mean undefined` and the cell
    is blank (611 cells in the two files). The arithmetic mean and the median are still given.
  - These curves keep all eligible units. `lead_day_metrics.csv` and `lcl_by_day.csv` use a fixed set of units with
    nonzero errors. The two kinds are not comparable; Figures 9 and 9b use `lcl_by_day.csv`.

## The anchoring record

**`anchoring_gain_deciles.csv`** - the two statistics of `anchoring_record` (package 2.2) against the realised gain of ANKYRA
2.2 over TimesFM on fourteen populations (14,177 windows, 14,006 with a defined log ratio: the ten of the main comparison, the GoiEner development store, HKUST,
Helsinki and UNICON). Columns: `statistic`, `decile` (global over all windows), `lower_edge`, `upper_edge`, `windows`, `populations`,
then the unit-equal log RMS improvement in per cent and the 95% unit-and-month interval of the log ratio for the monthly level
(= monthly energy) and for the hourly error ([README section](../README.md#when-anchoring-is-expected-to-help)).

## Checks with the forecaster frozen

**`carrier_swap.csv`** — ANKYRA 2.1 (gap tolerance off; not recomputed for 2.2) with Chronos-2 in place of TimesFM (`ANKYRA-C`), ten populations, all windows (`full`) and
windows after the training cutoff (`late`), hourly and monthly-energy error. Columns: `contrast` (first model vs
second), `log_ratio` with its 95% unit-and-month interval (`um_low`, `um_high`), `improvement_pct` (positive = first
model better), `resolved`. A re-evaluation of populations scored before.

**`hkust_first_read.csv`** — ANKYRA 2.2 on the HKUST campus incomer meters (134 windows, 33 units): one original first
read with the frozen 2.0.1 (its file is `ankyra_2_0_1/hkust_first_read.csv`), comparators added afterwards against the
frozen ANKYRA forecasts, every ANKYRA forecast recomputed after the causal correction of the temperature scale, and
the same targets read again with 2.1 (`ankyra_2_1/`) and with 2.2 (re-evaluations); ANKYRA against each
comparator. `resolved_at_seed_20261004` is the reading under one bootstrap seed; the two hourly contrasts against the
foundation models are borderline: under 2.2 both read `first better` (upper ends −0.007 and −0.001), where under
2.0.1 and 2.1 the Chronos-2 contrast read `not resolved`; the energy contrast against GBT (zero-shot) also reads
`first better` under 2.2 and `not resolved` under 2.0.1 and 2.1. These readings changed under 2.2 and can change with
the seed; the other 23 verdicts are those of 2.0.1. Not merged into any other table
([details and limits](../docs/FROZEN_MODEL_CHECKS.md#a-population-never-used-before)). The rows for Holt-Winters, MSTL
and GBT (zero-shot) were added in the same way. Figure 17 b, c.

**`hkust_by_day.csv`** — per-day curves on HKUST for the 14 forecasters (ANKYRA 2.2), on the 123 windows where the
per-unit ridge is defined: `hourly_gm_cv_pct` (Figure 9 definition) and `energy_to_date_gm_cv_pct` (Figure 9b
definition), geometric means over the fixed set of `units_in_fixed_set` units (29). The HKUST panels of Figures 9 and
9b; computed after scoring.

**`helsinki_confirmation.csv`** — the pre-registered confirmation test on Helsinki city service buildings (201 units,
1,168 windows; 200 units with non-zero load are scored), registered and first scored with the frozen 2.0.1 (its files
are in `ankyra_2_0_1/`, the 2.1 re-reading in `ankyra_2_1/`); the numbers here re-read the same targets with ANKYRA 2.2, with the same verdicts. ANKYRA
against each of the other 13 forecasters, hourly and monthly energy error, with the 95% unit-and-month interval at
seed 20261005. `helsinki_criteria.json` holds the two criteria and their outcome (primary failed, secondary passed;
not confirmed) and the mean unit ranks of the 14. `helsinki_by_day.csv` holds the per-day curves (the Helsinki panels
of Figures 9 and 9b; columns as in `hkust_by_day.csv`).
[Details](../docs/FROZEN_MODEL_CHECKS.md#a-pre-registered-confirmation-test-helsinki).

**`unicon_external.csv`** — the external test of the frozen ANKYRA 2.1 on UNICON (La Trobe University, five campuses,
Victoria, Australia; licence CC BY-NC-SA 4.0, data not redistributed): 843 windows, 60 units, a first read with 2.1
(its file is `ankyra_2_1/unicon_external.csv`); the file here re-reads the same targets with 2.2 (a re-evaluation,
with the same verdicts). Columns:
`error` (`hourly` or `energy`), `comparator`, `role` (`comparator`: the 13 other forecasters of the Helsinki test;
`descriptive arm`: ANKYRA 2.0.1, ANKYRA anchored to Chronos-2-X, the half-and-half combination B1 and the per-unit
combination weight B2, fixed in the protocol as descriptions), `windows`, `units`, `log_ratio`, `um_low`, `um_high`,
`improvement_pct` (ANKYRA 2.2 against the comparator; positive favours ANKYRA), `resolved_at_seed_20261006`
(`first better`, `second better` or `not resolved` under the test's seed) and `units_better_strict` (units on which
ANKYRA's summed error is strictly lower). The per-unit ridge is defined on 674 windows.

**`unicon_criteria.json`** — the protocol's two criteria and their outcome (primary, monthly energy against TimesFM:
failed, upper end +0.116 under 2.2, +0.080 in the 2.1 test; secondary, hourly: passed; `confirmed`: false), the window, unit and month counts, the mean
unit ranks of the 14 forecasters on the 674 ridge-defined windows, the improvements against TimesFM by origin year
(descriptive), the licence note and the diagnostic (0.51 of 6 pseudo-origin pairs used on average by the frozen 2.1; 3.49 under 2.2).

**`unicon_by_day.csv`** — per-day curves on UNICON for the 14 forecasters on the 674 ridge-defined windows (fixed set
of 60 units), columns as in `hkust_by_day.csv`. The UNICON panels of Figures 9 and 9b.
[Details](../docs/FROZEN_MODEL_CHECKS.md#an-external-test-of-ankyra-21-unicon).

**`carrier_swap_x.csv`** — post-hoc exploration (not a test): ANKYRA 2.1 anchored to Chronos-2-X on the twelve populations, against Chronos-2-X and against the TimesFM-anchored ANKYRA, hourly and monthly energy, with the 95% unit-and-month interval ([details](../docs/FROZEN_MODEL_CHECKS.md#a-post-hoc-exploration-ankyra-anchored-to-chronos-2-x)).

**`carrier_swap_combined.csv`** — the anchoring of ANKYRA 2.1 on two foundation-model families in three configurations (TimesFM; Chronos-2 without and with covariates) on the same windows with one seed: gain of each anchored version over its own foundation model, and the finished forecasters against each other ([details](../docs/FROZEN_MODEL_CHECKS.md#two-families-three-configurations-on-the-same-windows)).

The three carrier-swap files were recomputed with 2.1 (gap tolerance off) and not recomputed for 2.2; the 2.0.1 runs are in `ankyra_2_0_1/`, with the same resolved
counts.

## Long-context foundation models and generic combinations

Two descriptive experiments on **ANKYRA 2.2**, run after 2.2 under a protocol that was fixed before anything was
scored (one implementation each, no pass line, nothing tuned). Every population had been read before, so all numbers
are re-evaluations of read data, not tests. Interval: 95% unit-and-month bootstrap, 2,000 draws, seed **20261007**
(a new generator per contrast). Both files are printed with full floating-point precision, copied exactly from the
scoring records; the bootstrap does not support that many digits. `resolved` is `first better`, `second better` or
`not resolved`; `improvement_pct` is positive when the first-named forecaster is better. README section:
[Long-context foundation models and generic combinations](../README.md#long-context-foundation-models-and-generic-combinations).

**`long_context_carriers.csv`** — Does the anchoring gain survive when the foundation model sees a year of history
instead of 1,344 hours? Ten populations, the late windows of `datasets.csv` (`subset` = `late`; `windows`, `units` =
`windows_late`, `units_late`), hourly and monthly-energy error (`error`). Forecasters:

- `TimesFM-8736`: TimesFM 2.5 with an 8,736-hour (52-week) context; `Chronos-2-8192`: Chronos-2 with 8,192 hours, the
  limit of its configuration. When the record is shorter or a gap falls inside that span, the context is the longest
  completely observed run of hours ending at the origin (never shorter than 1,344 hours on these windows).
- `ANKYRA-T8736`: the unchanged 2.2 package with TimesFM-8736 as its foundation model, at the origin and at the same
  pseudo-origins as in the scored forecasts.
- `ANKYRA` (2.2) and `TimesFM-1344` are the scored forecasts behind the main tables; the row `ANKYRA vs TimesFM-1344`
  reproduces their point estimates (its intervals differ only by the seed).

Columns: `set`, `tier`, `subset`, `windows`, `units`, `contrast` (first model vs second; `ANKYRA vs TimesFM-8736`,
`ANKYRA vs Chronos-2-8192`, `ANKYRA-T8736 vs TimesFM-8736`, `TimesFM-8736 vs TimesFM-1344`, `ANKYRA vs
TimesFM-1344`), `error`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`, `resolved`.

**`generic_combinations.csv`** — Is ANKYRA's history-side forecast (H) a better combination partner for TimesFM than a
generic local forecast X? Twelve populations (the ten, HKUST and Helsinki; `tier` = `frozen-model check` for the last
two), all windows of the B2 comparison (`subset` = `full`), hourly and monthly-energy error.

- `B2(X)`: the B2 procedure of `component_contributions.csv` (one whole-window least-squares weight per unit from its
  pseudo-origin errors, clipped to [0, 1] and shrunk towards ½) with H replaced by X; X is `SN-week`, `WeekProf4` or
  `LYR-profile`, which can be computed from the history at every pseudo-origin. `B2(H)` is B2 itself. Windows on which
  B2(H) returns TimesFM (off-state, micro-load, no pseudo-origin) return TimesFM in every B2(X) as well.
- `EW(X)`: the equal-weight combination max(½ TimesFM + ½ X, 0), for every X whose scored forecast exists:
  `SN-week`, `WeekProf4`, `LYR-profile`, `RIDGE-L`, `MSTL`.
- `contrast`: `B2(H) vs B2(SN-week)`, `B2(H) vs B2(WeekProf4)`, `B2(H) vs B2(LYR-profile)`, `B2(H) vs best B2(X)`,
  `B2(H) vs best equal-weight` and `ANKYRA vs best generic`.
- **How "best" was chosen.** After scoring, separately for each population and each `error`: the candidate with the
  lowest error, i.e. the largest log ratio of the first-named forecaster against it. `best` names it and `candidates`
  lists the candidates; for `ANKYRA vs best generic` they are all B2(X) and all EW(X) available on every window. This
  choice favours the generic side.
- `availability_note`: an X whose forecast exists on part of the windows only (`RIDGE-L` on 917 of 1,234 GoiEner
  non-household windows and on 113 of 120 HKUST windows; no saved `MSTL` on HKUST) is not a candidate for best; the note
  is given on the two rows whose candidates it affects.
- `units` is blank: the scoring record holds the window counts only.
- Other columns: `set`, `tier`, `windows`, `error`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`, `resolved`.

## Two candidates examined after 2.0.1 and not adopted

**`closeout_status.json`** — The status of two candidate changes examined after the 2.0.1 release. Neither was
scored and neither was adopted; the forecaster is unchanged ([details](../docs/LCL_AND_CLOSEOUT.md)).

- `daily_path_candidate`: mixing ANKYRA's daily path with that of the per-unit ridge. It was to be scored only if the
  ridge's daily path alone was at least as good as ANKYRA's on 562 design windows of the GoiEner households. It was
  0.09% worse, so the candidate was not scored. This entry condition was cautious; its failure does not prove that no
  mixture could improve.
- `interval_candidate`: a new interval rule. Of 7,676 windows, at least 742 have no usable earlier residual, so the
  criteria on coverage and Winkler score could not be evaluated, and nothing was scored. This is not a measured
  failure of interval accuracy.
- `status_code` gives the label each stop carries in the study protocol; `status` says the same in words.
- `lcl`: the counts of the LCL evaluation and a pointer to its files.
