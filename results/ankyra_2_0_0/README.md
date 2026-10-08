> **Archived record of ANKYRA 2.0.0 (without the micro-load rule), kept unchanged beside the later results (2.0.1 in
> [`ankyra_2_0_1/`](../ankyra_2_0_1/), 2.1 in [`ankyra_2_1/`](../ankyra_2_1/), mostly 2.2 in `results/`).** The
> current files are in [`results/`](../), with a full description of the columns in
> [`results/README.md`](../README.md).
>
> - Figure numbers below are those of the 2.0.0 release: its Figure 9 (energy by forecast day) is now Figure 9b and
>   its Figure 9b (hourly loss by forecast day) is now Figure 9.
> - The data files of this folder keep the column names of their release. Three have since been renamed in the
>   current files: in `bdg2_near_zero_sensitivity.csv` the column `units` (values `all_units`, `without_near_zero`) is
>   now `unit_set`; in `energy_error.csv` the column `subset` (`all units`, `without the three near-zero meters`) is
>   now `unit_set`; in `cost_per_window.csv` the header `item,seconds_per_window` is now `item,value,unit`. In this
>   folder the last five rows of `cost_per_window.csv` are seconds per model load and GiB of GPU memory, not seconds
>   per window.
> - `REPRODUCTION_CHECK.json` here was written before the package's version string was raised, so its
>   `package_version` field reads 1.2.1; the check ran on the 2.0.0 code (the file hashes are in the file). In it,
>   `v6` is the working name of the 2.0 forecaster and `flagship` that of the 1.x research implementation; `faces`
>   are the window sets checked, with `goiener_confirm` the GoiEner non-household population, `households` the
>   GoiEner households and `park` the Suzhou park.

# Results data (ANKYRA 2.0.0, archived)

All files describe **ANKYRA 2.0** (within-day anchoring) unless the file name says `1x`; the complete 1.x set, scored
on the same windows, is kept unchanged in [`ankyra_1x/`](../ankyra_1x/). Scored statistics behind the figures and
tables. Everything was exported from the study's evaluation outputs, and nothing was tuned. Two files are descriptions
computed after scoring from the scored forecasts: `lead_day_metrics.csv` and `energy_error.csv`. The raw data are not
included. GBT-T appears in its corrected implementation, re-scored after a defect in its scaling was found
([details](../../docs/EVALUATION.md#correction-of-the-gbt-t-baseline)).

| File | Content |
|---|---|
| `benchmark_pairwise.csv` | ANKYRA against every external forecaster, per population. `subset`: `full` (all windows) or `late` (origins after the training cutoff, where trained models exist). Fields: unit-equal log RMS ratio (negative favours ANKYRA), 95% unit-and-month bootstrap interval (`um_low`, `um_high`), improvement `100[1 − exp(r)]`, pooled MSE ratio. |
| `benchmark_mean_unit_rank.csv` | Mean per-unit rank of ANKYRA and each external forecaster (models ranked within each unit by RMSE); positions per population in Figure 12. |
| `ablation.csv` | ANKYRA 2.0 against its reduced versions: ANKYRA 1.x (foundation within-day block, no anchoring), without the off-state rule (F1), and the fixed division of labour (F0). |
| `ankyra_2_vs_1x_by_day.csv` | Loss by forecast day (figure-9 definitions, same fixed unit set) of ANKYRA 2.0, ANKYRA 1.x and the four zero-shot foundation-model variants on the post-cutoff windows of the six test sets. |
| `lead_weeks_first_read.csv` | Week-by-week contrasts against TimesFM on the three populations scored first after the handover was fixed: ANKYRA 2.0 (`ankyra_vs_timesfm_log_ratio`), ANKYRA 1.x and the fixed division, with the estimated weekly weight on the model (the handover is unchanged in 2.0). |
| `peak_readout.csv` | Peak operator on ANKYRA's daily means against the trajectory maximum, the same readout on TimesFM and on the fixed division, and last month's observed peak. |
| `intervals_households.json` | Pseudo-origin interval around ANKYRA vs around the fixed division and the native quantiles of TimesFM and Chronos-2 (coverage, width, Winkler, pinball); Figure 13. |
| `block_shares.csv` | Block attribution on the late windows (six test populations and the Suzhou park): the pooled and median-unit share of each forecast's hourly squared error in the level, daily-path and within-day blocks, for ANKYRA 2.0, ANKYRA 1.x, TimesFM and Chronos-2-X; and ANKYRA 2.0's unit-equal improvement over TimesFM and Chronos-2-X in each block and in total (`improvement_pct`, `log_ratio`, `units_in_ratio`). Descriptive, computed after scoring; Figure 14. |
| `conventional_metrics.csv` | Full windows: RMSE, MAE (unit mean, kW); CV(RMSE), NMBE, WAPE (unit median, %); pooled WAPE. |
| `energy_error.csv` | Monthly energy error (744 × the level error, P3) of ANKYRA against each of the 20 baselines on the late windows of the six test sets and the Suzhou park: unit-equal log RMS ratio with its 95% unit-and-month bootstrap interval, improvement `100[1 − exp(r)]`, and each forecaster's median-unit absolute percentage energy error. BDG2 also without the three near-zero meters. Figure 11; computed after scoring, as a description. |
| `lead_day_metrics.csv` | Loss by forecast day (1–31) for all 21 forecasters on the late windows of the six test sets and the Suzhou park: RMSE and MAE (unit mean, kW); CV(RMSE) and normalised MAE (median unit, %); CV(RMSE) as a geometric mean over a fixed set of units (`GM_CV_RMSE_pct`, `n_units_gm`), used in Figures 9b and 10. A description made after scoring; pooled over the month it gives back the scored metrics. |
| `lead_day_energy.csv` | Energy error by forecast day for all 21 forecasters on the same late windows: the error of each day's energy (`GM_CV_daily_energy_pct`) and of the energy delivered through day d (`GM_CV_cumulative_energy_pct`), as geometric means over a fixed unit set (`units_in_U`); Figure 9. Computed after scoring. |
| `rank_tests.csv` | Rank tests on per-unit RMSE of the 21 forecasters, late windows: mean ranks, Friedman p-value, Nemenyi critical difference and Holm-corrected Wilcoxon p-values of ANKYRA against each forecaster, per population and pooled over the six test populations; Figure 15. |
| `scaled_errors.csv` | RMSSE and MASE of the 21 forecasters (scale: in-sample weekly seasonal-naive error over the 1,344-hour context), median and geometric mean over units, per population. |
| `intervals_by_population.csv` | The pseudo-origin residual interval around ANKYRA 2.0 and the native quantiles of TimesFM 2.5 and Chronos-2 on all windows of the ten scored populations: coverage at 80% and 90%, width, Winkler score, pinball losses, and coverage and Winkler score by forecast week; Figure 16. |
| `constants_sensitivity.csv` | One shrinkage constant changed at a time (handover K0 and pseudo-origins; within-day K0, cap and pseudo-origins): hourly unit-equal log ratio against ANKYRA 2.0 on the nine design sets, called faces in the column names: the three development populations (`oslo_all`, `drammen_all`, `goiener_dev_all`, the GoiEner development store) and the pre-cutoff windows of the six test populations (`bdg2_early`, `cambridge_early`, `eweld_early`, `households_early` and two more). The file gives the nine-set mean and the worst and best set. No test window is used. |
| `robustness.csv` | Stress test on 64 Drammen windows: change of ANKYRA's and TimesFM's hourly error, of the level and of the peak readout under corrupted contexts (gaps, zero-fill, spike, clock shift, scaling). |
| `history_length.csv` | ANKYRA 2.0 against TimesFM, ANKYRA 1.x and the fixed division by history length at the origin (hours since the unit's first observation; strata by hours and by the number of completed pseudo-origins), per population and pooled; all panel windows. Descriptive. |
| `conventional_metrics_late.csv` | The same metrics on the late windows for all 21 forecasters plus ANKYRA 1.x as a row, with windows, units and model class (Figure 8). `units_excluded`: units with a mean below 10⁻⁶ kW, left out of the ratio metrics. |
| `datasets.csv` | Populations, tier and design status. |
| `handover_granularity.csv` | Ablation fixed before it was run (1.x record; the handover is unchanged in 2.0): ANKYRA's weekly per-unit weights (AW) against a fixed half mixture (Ah), one weight per unit and month (AM) and no handover (A0), on the ten non-reserved populations, overall and by forecast week; also each arm against TimesFM. |
| `bdg2_near_zero_sensitivity.csv` | BDG2 comparisons with and without the three near-zero meters (full and late windows); the full result is the primary one. |
| `cost_per_window.csv` | Seconds per 744-hour window for ANKYRA, TimesFM alone, Chronos-2-X and the per-unit ridge on one laptop GPU; model loads and GPU memory. |
| `example_window_cambridge.csv` / `.json` | One Cambridge test window (University of Cambridge estate archive, CC BY 4.0), with its full 1,344-hour context and day types, used in Figures 6 and 7. |
| `REPRODUCTION_CHECK.json` | The 2.0 package against the evaluated forecasts on 150 sampled windows: 2.0 to float32 precision (largest relative difference 5.6×10⁻⁸), the 1.x mode exact (1.1×10⁻¹³ kW). The exact 1.x record of the adapter, readouts and intervals is `../ankyra_1x/REPRODUCTION_CHECK.json`. |

Model classes:

- `same information`: the model is given ANKYRA's 11 past, 10 future and 6 static features, and uses the part its
  architecture accepts;
- `load only`: the model receives the 1,344-hour load context only.
