> **Archived record of ANKYRA 1.x (release 1.2.1), kept unchanged beside the 2.1 results (2.0.1 in
> [`ankyra_2_0_1/`](../ankyra_2_0_1/)).** The current files are
> in [`results/`](../), with a full description of the columns in [`results/README.md`](../README.md).
>
> - Figure numbers and file descriptions below are those of the 1.2.1 release.
> - 1.x was scored on eleven populations, so the LCL households appear in these files. In the current files LCL is
>   kept apart (`lcl_*`).
> - The data files of this folder keep the column names of their release. Three have since been renamed in the
>   current files: in `bdg2_near_zero_sensitivity.csv` the column `units` (values `all_units`, `without_near_zero`) is
>   now `unit_set`; in `energy_error.csv` the column `subset` (`all units`, `without the three near-zero meters`) is
>   now `unit_set`; in `cost_per_window.csv` the header `item,seconds_per_window` is now `item,value,unit`. In this
>   folder the last five rows of `cost_per_window.csv` are seconds per model load and GiB of GPU memory, not seconds
>   per window.
> - `REPRODUCTION_CHECK.json` here refers to the 1.x package. In it, `goiener_confirm` is the GoiEner non-household
>   population, `lcl` the LCL households, "panel" the set of scored forecasts behind the tables, and `f1` the 1.x
>   forecaster without the off-state rule.
> - **Line endings and the recorded hashes.** In `REPRODUCTION_CHECK.json`, the hashes of eight files under
>   `ankyra/history/` (`_climate.py`, `_day.py`, `_eo.py`, `_level.py`, `_signature.py`, `_span.py`,
>   `frozen_config.json`, `provenance.json`) were taken on a Windows working copy with CRLF line endings. The
>   repository stores these files with LF. A hash computed on a checkout with LF endings therefore differs from the
>   recorded one, although the content is the same; with the line endings converted to CRLF the recorded values are
>   reproduced.

# Results data (ANKYRA 1.x, archived)

Scored statistics behind the figures and tables. Everything was exported from the study's evaluation outputs, and
nothing was tuned. Two files are descriptions computed after scoring from the scored forecasts: `lead_day_metrics.csv`
and `energy_error.csv`. The raw data are not included. GBT-T appears in its corrected implementation, re-scored after
a defect in its scaling was found ([details](../../docs/EVALUATION.md#correction-of-the-gbt-t-baseline)).

| File | Content |
|---|---|
| `benchmark_pairwise.csv` | ANKYRA against every external forecaster, per population. `subset`: `full` (all windows) or `late` (origins after the training cutoff, where trained models exist). Fields: unit-equal log RMS ratio (negative favours ANKYRA), 95% unit-and-month bootstrap interval (`um_low`, `um_high`), improvement `100[1 − exp(r)]`, pooled MSE ratio. |
| `benchmark_mean_unit_rank.csv` | Mean per-unit rank of ANKYRA and each external forecaster (models ranked within each unit by RMSE); positions per population in Figure 12. |
| `ablation.csv` | ANKYRA against its reduced versions: without the off-state rule (F1), and the fixed division of labour (F0). |
| `lead_weeks_first_read.csv` | Week-by-week contrasts against TimesFM and the estimated weekly weight on the model, on the three populations scored first after the handover was fixed. |
| `peak_readout.csv` | Peak operator on ANKYRA's daily means against the trajectory maximum, the same readout on TimesFM and on the fixed division, and last month's observed peak. |
| `intervals_households.json` | Pseudo-origin interval around ANKYRA vs around the fixed division and the native quantiles of TimesFM and Chronos-2 (coverage, width, Winkler, pinball); Figure 13. |
| `conventional_metrics.csv` | Full windows: RMSE, MAE (unit mean, kW); CV(RMSE), NMBE, WAPE (unit median, %); pooled WAPE. |
| `energy_error.csv` | Monthly energy error (744 × the level error, P3) of ANKYRA against each of the 20 baselines on the late windows of the six test sets and the Suzhou park: unit-equal log RMS ratio with its 95% unit-and-month bootstrap interval, improvement `100[1 − exp(r)]`, and each forecaster's median-unit absolute percentage energy error. BDG2 also without the three near-zero meters. Figure 11; computed after scoring, as a description. |
| `lead_day_metrics.csv` | Loss by forecast day (1–31) for all 21 forecasters on the late windows of the six test sets and the Suzhou park: RMSE and MAE (unit mean, kW); CV(RMSE) and normalised MAE (median unit, %); CV(RMSE) as a geometric mean over a fixed set of units (`GM_CV_RMSE_pct`, `n_units_gm`), used in Figures 9 and 10. A description made after scoring; pooled over the month it gives back the scored metrics. |
| `conventional_metrics_late.csv` | The same metrics on the late windows for all 21 forecasters, with windows, units and model class (Figure 8). `units_excluded`: units with a mean below 10⁻⁶ kW, left out of the ratio metrics. |
| `datasets.csv` | Populations, tier and design status. |
| `handover_granularity.csv` | Ablation fixed before it was run: ANKYRA's weekly per-unit weights (AW) against a fixed half mixture (Ah), one weight per unit and month (AM) and no handover (A0), on the ten non-reserved populations, overall and by forecast week; also each arm against TimesFM. |
| `bdg2_near_zero_sensitivity.csv` | BDG2 comparisons with and without the three near-zero meters (full and late windows); the full result is the primary one. |
| `cost_per_window.csv` | Seconds per 744-hour window for ANKYRA, TimesFM alone, Chronos-2-X and the per-unit ridge on one laptop GPU; model loads and GPU memory. |
| `example_window_cambridge.csv` / `.json` | One Cambridge test window (University of Cambridge estate archive, CC BY 4.0), with its full 1,344-hour context and day types, used in Figures 6 and 7. |
| `REPRODUCTION_CHECK.json` | The 1.x package against the evaluated forecasts: all differences 0.0 kW. |

Model classes:

- `same information`: the model is given ANKYRA's 11 past, 10 future and 6 static features, and uses the part its
  architecture accepts;
- `load only`: the model receives the 1,344-hour load context only.
