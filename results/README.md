# Results data

All files describe **ANKYRA 2.0.1** (2.0.0 plus the micro-load rule) unless the file name says `1x`. Earlier versions,
scored on the same windows, are kept unchanged: 2.0.0 in [`ankyra_2_0_0/`](ankyra_2_0_0/) and 1.x in
[`ankyra_1x/`](ankyra_1x/).

- **What differs from 2.0.0.** Only rows of BDG2 and aggregates that include BDG2. The micro-load rule changes 46
  windows of nine meters at one BDG2 site and no forecast of the other nine populations.
- **Status of the BDG2 rows.** The rule was written after the BDG2 test result of 2.0.0 had been seen. The BDG2 rows
  describe what the rule changes; they are not a test of it
  ([details](../docs/EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)).

Scored statistics behind the figures and tables, exported from the study's evaluation outputs. Two changes were made
to the forecaster after the test populations were first scored (for 1.x): the within-day anchoring of 2.0, whose numbers
are a re-evaluation under a frozen protocol, and the micro-load rule above
([details](../docs/EVALUATION.md#populations-and-tiers)). Nothing was tuned on the exported statistics. Several files are
descriptions computed after scoring from the scored forecasts (marked below). The raw data are not included. GBT-T appears in its corrected implementation, re-scored after a defect in its scaling was
found ([details](../docs/EVALUATION.md#correction-of-the-gbt-t-baseline)).

| File | Content |
|---|---|
| `benchmark_pairwise.csv` | ANKYRA against every external forecaster, per population. `subset`: `full` (all windows) or `late` (origins after the training cutoff, where trained models exist). Fields: unit-equal log RMS ratio (negative favours ANKYRA), 95% unit-and-month bootstrap interval (`um_low`, `um_high`), improvement `100[1 − exp(r)]`, pooled MSE ratio. |
| `benchmark_mean_unit_rank.csv` | Mean per-unit rank of ANKYRA and each external forecaster (models ranked within each unit by RMSE); positions per population in Figure 12. |
| `ablation.csv` | ANKYRA 2.0.1 against its reduced versions: 2.0.0 (without the micro-load rule; zero on every population except BDG2), ANKYRA 1.x (foundation within-day block, no anchoring), F1 (the 1.x forecaster without the off-state rule) and F0 (the fixed division of labour). F1 and F0 are the 1.x-era forecasters, so like 1.x they also lack the within-day anchoring: where the off-state rule never fires, the F1 row equals the 1.x row. None of the reduced versions carries the micro-load rule, so on BDG2 the last three contrasts include it; their 2.0.0 values are in `ankyra_2_0_0/ablation.csv`. |
| `ankyra_2_vs_1x_by_day.csv` | Hourly loss by forecast day (figure-9 definitions, same fixed unit set) of ANKYRA 2.0.1, 2.0.0, 1.x and the four zero-shot foundation-model variants on the post-cutoff windows of the six test sets. |
| `lead_weeks_first_read.csv` | Week-by-week contrasts against TimesFM on the three populations scored first after the handover was fixed: ANKYRA (`ankyra_vs_timesfm_log_ratio`; identical in 2.0.0 and 2.0.1), ANKYRA 1.x and the fixed division, with the estimated weekly weight on the model (the handover is unchanged since 1.x). |
| `peak_readout.csv` | Peak operator on ANKYRA's daily means against the trajectory maximum, the same readout on TimesFM and on the fixed division, and last month's observed peak. |
| `intervals_households.json` | Pseudo-origin interval around ANKYRA vs around the fixed division and the native quantiles of TimesFM and Chronos-2 (coverage, width, Winkler, pinball); Figure 13. |
| `block_shares.csv` | Block attribution on the late windows (six test populations and the Suzhou park): the pooled and median-unit share of each forecast's hourly squared error in the level, daily-path and within-day blocks, for ANKYRA, ANKYRA 1.x, TimesFM and Chronos-2-X; and ANKYRA's unit-equal improvement over TimesFM and Chronos-2-X in each block and in total (`improvement_pct`, `log_ratio`, `units_in_ratio`). Descriptive, computed after scoring; Figure 14. |
| `conventional_metrics.csv` | Full windows: RMSE, MAE (unit mean, kW); CV(RMSE), NMBE, WAPE (unit median, %); pooled WAPE. ANKYRA 2.0.0 and 1.x appear as rows. |
| `energy_error.csv` | Monthly energy error (744 × the level error, P3) of ANKYRA against each of the 20 baselines on the late windows of the six test sets and the Suzhou park: unit-equal log RMS ratio with its 95% unit-and-month bootstrap interval, improvement `100[1 − exp(r)]`, and each forecaster's median-unit absolute percentage energy error. BDG2 also without the three near-zero meters. Figure 11; computed after scoring, as a description. |
| `lead_day_metrics.csv` | Loss by forecast day (1–31) for all 21 forecasters on the late windows of the six test sets and the Suzhou park: RMSE and MAE (unit mean, kW); CV(RMSE) and normalised MAE (median unit, %); CV(RMSE) as a geometric mean over a fixed set of units (`GM_CV_RMSE_pct`, `n_units_gm`), used in Figures 9 and 10. A description made after scoring; pooled over the month it gives back the scored metrics. |
| `lead_day_energy.csv` | Energy error by forecast day for all 21 forecasters on the same late windows: the error of each day's energy (`GM_CV_daily_energy_pct`) and of the energy delivered through day d (`GM_CV_cumulative_energy_pct`), as geometric means over a fixed unit set (`units_in_U`); Figure 9b. Computed after scoring. |
| `rank_tests.csv` | Rank tests on per-unit RMSE of the 21 forecasters, late windows: mean ranks, Friedman p-value, Nemenyi critical difference and Holm-corrected Wilcoxon p-values of ANKYRA against each forecaster, per population and pooled over the six test populations; Figure 15. |
| `scaled_errors.csv` | RMSSE and MASE of the 21 forecasters (scale: in-sample weekly seasonal-naive error over the 1,344-hour context), median and geometric mean over units, per population. |
| `intervals_winkler_contrasts.csv` | The unit-equal Winkler contrasts of the ANKYRA interval against TimesFM's and Chronos-2's native quantiles on the ten populations (log ratio, 95% interval, improvement), for 2.0.1 and 2.0.0. |
| `intervals_by_population.csv` | The pseudo-origin residual interval around ANKYRA (arm `ankyra_2_0`; the 2.0.1 trajectory) and the native quantiles of TimesFM 2.5 and Chronos-2 on all windows of the ten scored populations: coverage at 80% and 90%, width, Winkler score, pinball losses, and coverage and Winkler score by forecast week; Figure 16. |
| `constants_sensitivity.csv` | One shrinkage constant changed at a time (handover K0 and pseudo-origins; within-day K0, cap and pseudo-origins): hourly unit-equal log ratio against ANKYRA on the nine design faces (nine-face mean, worst and best face). Micro-load windows return the TimesFM forecast in the reference and in every variant. No test window is used. |
| `robustness.csv` | Stress test on 64 Drammen windows: change of ANKYRA's and TimesFM's hourly error, of the level and of the peak readout under corrupted contexts (gaps, zero-fill, spike, clock shift, scaling). |
| `history_length.csv` | ANKYRA against TimesFM, ANKYRA 1.x and the fixed division by history length at the origin (hours since the unit's first observation; strata by hours and by the number of completed pseudo-origins), per population and pooled; all panel windows. Descriptive. |
| `conventional_metrics_late.csv` | The same metrics on the late windows for all 21 forecasters plus ANKYRA 2.0.0 and 1.x as rows, with windows, units and model class (Figure 8). `units_excluded`: units with a mean below 10⁻⁶ kW, left out of the ratio metrics. |
| `datasets.csv` | Populations, tier and design status. BDG2 is a test population for the 2.0.0 forecaster; its 2.0.1 rows include the micro-load rule, written after its result was seen. |
| `handover_granularity.csv` | Ablation fixed before it was run (1.x record; the handover is unchanged in 2.0): ANKYRA's weekly per-unit weights (AW) against a fixed half mixture (Ah), one weight per unit and month (AM) and no handover (A0), on the ten non-reserved populations, overall and by forecast week; also each arm against TimesFM. |
| `bdg2_near_zero_sensitivity.csv` | BDG2 comparisons with and without the three meters that are near zero in every window (full and late windows), including ANKYRA 2.0.0 and 1.x as rows. Under 2.0.1 those meters are handed to TimesFM and still dominate the BDG2 unit means. In the rows without them the point estimates of 2.0.1 and 2.0.0 agree (late windows to 0.01 points, all windows to 0.03), but the intervals differ, because six further meters are handed over in some windows; three late contrasts are resolved only under 2.0.1. |
| `bdg2_micro_load_windows.csv` | The 46 BDG2 windows the micro-load rule changes, one row each: meter, target month, subset, the context maximum, the realised mean and maximum, whether the meter resumed during the forecast month, and the mean forecast and RMSE of 2.0.0 and 2.0.1. In 41 windows the meter stays near zero; in 5 it resumes, and there 2.0.0 is marginally better. Descriptive. |
| `cost_per_window.csv` | Seconds per 744-hour window for ANKYRA (measured on 2.0.0; the micro-load rule adds one maximum over the context), TimesFM alone, Chronos-2-X and the per-unit ridge on one laptop GPU; model loads and GPU memory. |
| `example_window_cambridge.csv` / `.json` | One Cambridge test window (University of Cambridge estate archive, CC BY 4.0), with its full 1,344-hour context and day types, used in Figures 6 and 7. |
| `REPRODUCTION_CHECK.json` | The 2.0.1 package against the evaluated forecasts on 484 windows of seven populations, including every micro-load window of BDG2 and of the EWELD post-cutoff windows (263 in all): the 2.0.1 forecasts against the scored panel and the 2.0.0 mode (`micro_load_rule=False`) against the evaluated 2.0.0 forecasts and the panel's 2.0.0 arm, all to float32 precision (largest relative differences 6.6×10⁻⁸, 5.7×10⁻⁸ and 6.6×10⁻⁸), the 1.x mode exact (3.4×10⁻¹³ kW); on micro-load windows the forecast is bit-identical to the TimesFM forecast, elsewhere to the 2.0.0 mode. The 2.0.0 and 1.x records are `ankyra_2_0_0/REPRODUCTION_CHECK.json` and `ankyra_1x/REPRODUCTION_CHECK.json`. |

Model classes:

- `same information`: the model is given ANKYRA's 11 past, 10 future and 6 static features, and uses the part its
  architecture accepts;
- `load only`: the model receives the 1,344-hour load context only.

## Final optimization records (2026-10-03)

`final_optimization_status.json` exports already saved result/audit JSON for the frozen 2.0.1 point model, the hourly conservative admission STOP, the interval source-support STOP and synthetic cache staging. The exporter reads no targets or prediction arrays. See [the closeout](../docs/FINAL_OPTIMIZATION_20261003.md). The original ten-population CSVs, ranks and BDG2 sensitivity results are unchanged. Final-stage LCL exports are a separate family: all registered windows and the metadata-key common post-cutoff face must remain separate, as must matched-input 1.x and the older archived 1.x forecast.


| New file | Scope |
|---|---|
| `lcl_final_results.json` | Final frozen 2.0.1 LCL result record, exported from saved JSON. |
| `lcl_final_all_pairwise.csv` | All 1,215 windows / 965 units; incomplete comparators explicitly unavailable. |
| `lcl_final_common_late_pairwise.csv` | The fixed metadata-key common late face: 710 windows / 710 units. |
| `lcl_final_common_late_ranks.csv` | Fixed 21-model mean unit ranks on that same common face only; no 1.x ablations in the rank set. |
| `lcl_final_shared_information_holm.csv` | Six directional tests of baseline superiority over ANKYRA; direction is the reverse of the pairwise CSVs. |
| `lcl_final_readouts.csv` | Full-face descriptive energy and peak errors; comparator operator is explicit. |

Pairwise CSVs report `improvement_percent = 100 * (1 - exp(log_RMS_ratio))`, positive in favor of ANKYRA. `UM95_log_RMS_lower/upper` remain on the log scale. `pooled_MSE_ratio` is a separate estimand. No significance stars are assigned by these exports. The two 1.x keys identify matched-input and archived-input comparisons separately. A zero or unavailable score is not replaced by an epsilon or interpreted as a tie.


The numerical audit passed 96,032 checks; `lcl_final_audit.json` and `lcl_final_exposure.json` record one audit target decode after the one formal scoring decode (two total). `lcl_final_all_lead_day_descriptive.csv` / `lcl_final_common_late_lead_day_descriptive.csv` and `lcl_final_all_conventional_descriptive.csv` / `lcl_final_common_late_conventional_descriptive.csv` partition the auditor's saved summaries by the two fixed faces without changing any value. `lcl_final_descriptive_definitions.json` gives the definitions. The 619 undefined geometric cells caused by exact zero error remain blank and explicitly unresolved. These descriptive curves use registered-face truth means for normalization and differ from the old figure's zero-error exclusion policy; do not splice them into Figure 9/9b or reinterpret them as the monthly primary statistic.
