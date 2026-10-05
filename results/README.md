# Results data

All files describe **ANKYRA 2.0.1** (2.0.0 plus the micro-load rule). Where a file also carries 2.0.0 or 1.x, or was
measured on an earlier version, its entry says so. Earlier versions, scored on the same windows, are kept unchanged:
2.0.0 in [`ankyra_2_0_0/`](ankyra_2_0_0/) and 1.x in [`ankyra_1x/`](ankyra_1x/).

- **What differs from 2.0.0.** Only rows of BDG2 and aggregates that include BDG2. The micro-load rule returns the
  TimesFM forecast when the whole 1,344-hour context stays within 10⁻³ kW of zero. It changes 46 windows of nine
  meters at one BDG2 site and no forecast of the other nine populations.
- **Status of the BDG2 rows.** The rule was written after the BDG2 test result of 2.0.0 had been seen. The BDG2 rows
  describe what the rule changes; they are not a test of it
  ([details](../docs/EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)).

The files hold the scored statistics behind the figures and tables. They were exported from the study's evaluation
outputs. Raw data, saved forecasts, model weights and the code of the trained baselines are not in the repository.

- Two changes were made to the forecaster after the test populations were first scored (for 1.x): the within-day
  anchoring of 2.0, whose numbers are a re-evaluation under a frozen protocol, and the micro-load rule above
  ([details](../docs/EVALUATION.md#populations-and-tiers)).
- Nothing was tuned on the exported statistics.
- Files marked *descriptive* were computed after scoring, from the scored forecasts.
- GBT-T appears in its corrected implementation, re-scored after a defect in its scaling was found
  ([details](../docs/EVALUATION.md#correction-of-the-gbt-t-baseline)).
- The LCL households are a separate family of files (`lcl_*`, [below](#lcl-households)). They are not part of the
  ten-population tables, ranks or figures.

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
| `ANKYRA` | ANKYRA 2.0.1 | blank |
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

BDG2 is a test population for the 2.0.0 forecaster. Its 2.0.1 rows include the micro-load rule, written after its
result was seen. The 1.x result on LCL was known before 2.0.1 was scored there, so LCL is `seen` and is not an
unexposed population.

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
  in one file and not in the other. ANKYRA's rank is the same in both (4.535 and 4.5352).

**`conventional_metrics.csv`** — Conventional errors on all windows for ANKYRA, 2.0.0 (`ANKYRA-200`), 1.x
(`ANKYRA-1x`) and the forecasters that exist on all windows. Columns: `set`, `tier`, `model`, `RMSE_kW` and `MAE_kW`
(mean over units, kW), `CV_RMSE_pct`, `NMBE_pct` and `WAPE_pct` (median over units, %), `WAPE_pooled_pct` (pooled over
all windows, %).

**`conventional_metrics_late.csv`** — The same metrics on the late windows for all 21 forecasters, with 2.0.0 and 1.x
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
unit set, three decimals) for ANKYRA 2.0.1, 2.0.0, 1.x and the four foundation-model variants on the six test sets.
Columns: `set`, `day`, `units_in_U`, then one column per forecaster: `ankyra_2_0_1`, `ankyra_2_0_0`, `ankyra_1x`,
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

**`ablation.csv`** — ANKYRA 2.0.1 against its reduced versions, on all windows of the ten populations. Columns: `set`,
`tier`, `ablation`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`. Figure 4a. The four values of `ablation`:

- ANKYRA 2.0.0 (without the micro-load rule): zero on every population except BDG2;
- ANKYRA 1.x (foundation within-day block, no anchoring);
- F1 (the 1.x forecaster without the off-state rule);
- F0 (the fixed division of labour).

F1 and F0 are forecasters of the 1.x period, so like 1.x they lack the within-day anchoring. Where the off-state rule
never fires, the F1 row equals the 1.x row. None of the reduced versions carries the micro-load rule, so on BDG2 the
last three contrasts include it; their 2.0.0 values are in `ankyra_2_0_0/ablation.csv`.

**`handover_granularity.csv`** — An ablation of the handover on the ten populations, specified before it was run. It
is a record of 1.x; the handover is unchanged since. Four arms: ANKYRA's weekly per-unit weights (`AW`), a fixed half
mixture (`Ah`; A½ in the documents), one weight per unit and month (`AM`) and no handover (`A0`). Columns: `set`, `tier`, `contrast`, `log_ratio`, `um_low`,
`um_high`, `improvement_pct`, `pooled_mse_ratio`; the first arm named in `contrast` is the numerator. `C1`–`C4` number
the four contrasts fixed before the run, of which `C1` and `C2` are also given by forecast week. The rows without a
number (each arm against TimesFM, `AW` and `AM` against `A0`) are descriptive. Figure 4b.

**`lead_weeks_first_read.csv`** — Contrasts against TimesFM by forecast week (1–4) on the three populations scored
first after the handover was fixed (Cambridge, CINELDI, HEEW). Figure 4c and 4d.

- `ankyra_vs_timesfm_log_ratio`: ANKYRA (identical in 2.0.0 and 2.0.1).
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
- `worst_face`, `worst_face_log_ratio`: the design set with the largest ratio, and that ratio. `best_face_log_ratio`:
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

- `arm`: `ankyra_2_0` (the interval around the 2.0.1 trajectory; the name is from 2.0), `chronos_native`,
  `timesfm_native`.
- `cov80`, `cov90`: coverage, a fraction; `cov80_week1`–`cov80_week4` and `cov90_week1`–`cov90_week4` by forecast week.
- `width80`, `width90`, `winkler80`, `winkler80_week1`–`winkler80_week4`, `pinball_0.05`–`pinball_0.95`,
  `pinball_mean_common`: means in kW. The 90% columns and the 0.05 and 0.95 pinball losses are blank for TimesFM.
- On EWELD the width and the Winkler score of the ANKYRA interval are of the order of 10⁶ kW and carry no information:
  units that switch off produce enormous quantiles. The interval should not be used for such units.
- Other columns: `set`, `tier`, `units`, `windows`.

**`intervals_winkler_contrasts.csv`** — Unit-equal Winkler contrasts of the ANKYRA interval against `timesfm_native`
and `chronos_native` (`comparator`) on the ten populations, for `version` 2.0.1 and 2.0.0. Columns: `version`, `set`,
`comparator`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`.

## BDG2 and the micro-load rule

**`bdg2_near_zero_sensitivity.csv`** — The BDG2 contrasts with and without the three meters that are near zero in
every window. Columns: `unit_set`, `subset`, `model`, `log_ratio`, `um_low`, `um_high`, `improvement_pct`,
`ankyra_mean_unit_rank`. The rows include ANKYRA 2.0.0 and 1.x as `model`. `ankyra_mean_unit_rank` is ANKYRA's mean
per-unit rank on that unit set and subset, repeated on each row.

- Under 2.0.1 the three meters are handed to TimesFM and still dominate the BDG2 unit means.
- In the rows without them the point estimates of 2.0.1 and 2.0.0 agree (late windows to 0.01 points, all windows to
  0.03). The intervals differ, because six further meters are handed over in some windows; three late contrasts are
  resolved only under 2.0.1.

**`bdg2_micro_load_windows.csv`** — The 46 BDG2 windows the micro-load rule changes, one row each. Descriptive.
Columns: `meter`, `target_month`, `subset` (`early` or `late`), `context_max_kw` (largest load in the context),
`realised_mean_kw`, `realised_max_kw`, `meter_resumes_in_window`, and the mean forecast and RMSE of both versions
(`forecast_mean_2_0_0_kw`, `forecast_mean_2_0_1_kw`, `rmse_2_0_0_kw`, `rmse_2_0_1_kw`). In 41 windows the meter stays
near zero. In 5 it resumes, and there 2.0.0 is marginally better.

## Robustness, cost, example, reproduction

**`robustness.csv`** — Stress test on 64 Drammen windows (a development population): the context is corrupted, the
targets are not. Measured on 2.0.0. One row per `corruption`:

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
the context). Columns: `item`, `value`, `unit`. The unit is `s/window` (seconds per 744-hour window) for the
forecasters and their components, `s` for the two model loads (once per session) and `GiB` for peak GPU memory.
"Evaluated configuration" is the TimesFM setting used in the study (per-core batch 1). The `component:` rows are the
parts of the totals above them; four of them repeat a total that has a single part.

**`example_window_cambridge.csv`**, **`example_window_cambridge.json`** — One Cambridge test window (University of
Cambridge estate archive, CC BY 4.0), used in Figures 6 and 7. The CSV has `hour` (0 is the origin; negative hours are
the 1,344-hour context), `load_kw`, and from hour 0 on `timesfm_kw` and `ankyra_kw`. The JSON has the building, the
forecast period, the day types of the context and target days (Monday 0 … Sunday 6, holiday 7) and the source.

**`REPRODUCTION_CHECK.json`** — The 2.0.1 package against the evaluated forecasts on 484 windows of seven populations,
including every micro-load window of BDG2 and of the EWELD late windows (263 in all).

- `faces`: the window sets checked. `households` = GoiEner households, `goiener_confirm` = GoiEner non-household,
  `park` = Suzhou park; the suffixes `_late`, `_early`, `_all` name the subset.
- `max_rel_diff_2_0_1_vs_panel`: the package against the scored 2.0.1 forecasts ("panel" is the set of scored
  forecasts behind the tables). `max_rel_diff_2_0_0_mode`: the package with `micro_load_rule=False` against the stored
  2.0.0 forecasts named in `v6_reference` ("v6" was the working name of the 2.0 forecaster).
  `max_rel_diff_2_0_0_mode_vs_panel_arm`: the same mode against the 2.0.0 rows of the 2.0.1 scoring. All agree to
  float32 precision, the precision of the stored forecasts.
- `max_abs_diff_1x_mode_kw`: the 1.x mode against the evaluated 1.x forecasts, in kW.
- On micro-load windows the forecast is bit-identical to the TimesFM forecast, elsewhere to the 2.0.0 mode.
- `package_files`: SHA-256 of the eight top-level modules of `ankyra/` as stored in the repository (LF line endings).
  The files under `ankyra/history/` are not listed; for eight of them see the note below.

The 2.0.0 and 1.x records are `ankyra_2_0_0/REPRODUCTION_CHECK.json` and `ankyra_1x/REPRODUCTION_CHECK.json`.

**Line endings and the older hashes.** The hashes in `ankyra/history/provenance.json` and those of eight files under
`ankyra/history/` in `ankyra_1x/REPRODUCTION_CHECK.json` were taken on a Windows working copy with CRLF line endings.
The repository stores these files with LF. A hash computed on a checkout with LF endings therefore differs from the
recorded one, although the content is the same; with the line endings converted to CRLF the recorded values are
reproduced. The eight files are `_climate.py`, `_day.py`, `_eo.py`, `_level.py`, `_signature.py`, `_span.py`,
`frozen_config.json` and `provenance.json`.

## LCL households

The Low Carbon London (LCL) households were held out of the ten-population comparison. They were scored once with the
frozen 2.0.1 forecaster, and nothing was retuned. The 1.x result on LCL had been seen earlier, so LCL is not an
unexposed population. The `lcl_*` files are a separate family: they are not merged into the ten-population tables,
ranks or figures ([details](../docs/LCL_AND_CLOSEOUT.md)).

- **Two window sets, not to be mixed.** `subset` = `full`: all 1,215 windows of 965 units. `subset` = `late`: the 710
  windows of 710 units after the training cutoff for which all seven trained baselines have a forecast. The set was
  chosen by window identity, not by any target or forecast value. On `full` the seven trained baselines (DLinear,
  GBT-T, iTransformer, iTransformer-X, LSTM, PatchTST, TiDE) have `status` = `not available` and blank numbers. A
  blank is not a zero and not a tie.
- **Two versions of 1.x.** `ANKYRA-1x-matched` is 1.x recomputed on the same input as 2.0.1. `ANKYRA-1x-archived` is
  the 1.x forecast made earlier. The inputs differ in the temperature before the start of the temperature record: it
  is now a constant 15 °C, where the earlier input had copied a later year. The difference between the two rows is
  therefore not all due to the forecaster.
- **Two checks set before scoring.** The no-harm check: the upper end of the 95% interval of the log ratio of 2.0.1
  against `ANKYRA-1x-matched` must not exceed 0.01. It passed. The same-information check: six one-sided tests,
  Holm-corrected, of whether a baseline given ANKYRA's information (TiDE, iTransformer-X, GBT-T, Chronos-2-X,
  TimesFM-X and the per-unit ridge) is better than ANKYRA on the late windows. None is significantly better. This does
  not show equivalence, and it does not show that ANKYRA is better than all six.
- **What LCL does not test.** No LCL window triggers the micro-load rule (two windows trigger the off-state rule), so
  LCL says nothing about that rule. The interval was not assessed for 2.0.1 on LCL.
- The numbers are printed with full floating-point precision. The 2,000-draw bootstrap does not support that many
  digits.

| File | Content |
|---|---|
| `lcl_results.json` | The full record: both window sets, mean ranks, the two checks, the readouts, the counts of off-state and micro-load windows. The four CSV files below are extracts of it. |
| `lcl_pairwise.csv` | ANKYRA against each baseline and both 1.x versions on `full`. |
| `lcl_pairwise_late.csv` | The same on `late`. |
| `lcl_mean_unit_rank_late.csv` | Mean per-unit rank of the 21 forecasters on `late`. The unrounded RMSE values are ranked and tied ranks averaged. The two 1.x versions are not ranked. |
| `lcl_shared_information_holm.csv` | The six tests of the same-information check. Here the ratio is the baseline over ANKYRA, the reverse of the pairwise files: a positive `log_ratio` means the baseline is worse. |
| `lcl_readouts.csv` | Energy and peak readouts of ANKYRA against the TimesFM trajectory on `full`. Descriptive; not used to select anything. |
| `lcl_conventional_metrics.csv`, `lcl_conventional_metrics_late.csv` | Conventional errors on `full` and on `late`. Descriptive. |
| `lcl_lead_day_metrics.csv`, `lcl_lead_day_metrics_late.csv` | Hourly, daily-energy and cumulative-energy error by forecast day on `full` and on `late`. Descriptive. |
| `lcl_metric_definitions.json` | Definitions for the four descriptive files above. |
| `lcl_audit.json` | Arithmetic re-check of the saved LCL outputs with a second implementation: 96,032 comparisons, no difference. It is not an independent review. The saved targets were opened once for scoring and once for this check. |

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
    is blank (619 cells in the two files). The arithmetic mean and the median are still given.
  - These curves keep all eligible units. `lead_day_metrics.csv` uses a fixed set of units with nonzero errors. The
    two are not comparable, and the LCL curves are not part of Figures 9 and 9b.

## Two checks with the forecaster frozen

**`carrier_swap.csv`** — ANKYRA with Chronos-2 in place of TimesFM (`ANKYRA-C`), ten populations, all windows (`full`) and
windows after the training cutoff (`late`), hourly and monthly-energy error. Columns: `contrast` (first model vs
second), `log_ratio` with its 95% unit-and-month interval (`um_low`, `um_high`), `improvement_pct` (positive = first
model better), `resolved`. A re-evaluation of populations scored before.

**`hkust_first_read.csv`** — (the rows for Chronos-2-X and TimesFM-X were added afterwards, against the already frozen ANKYRA forecasts) the frozen 2.0.1 forecaster scored once on HKUST campus incomer meters (134 windows, 33
units), ANKYRA against each comparator. `resolved_at_seed_20261004` is the reading under one bootstrap seed; the two
hourly contrasts against the foundation models are borderline and change with the seed. Not merged into any other
table ([details and limits](../docs/FROZEN_MODEL_CHECKS.md)).

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
