# Results data

Scored statistics behind the figures and tables. Everything was exported from the study's evaluation outputs, and
nothing was tuned. Two files are descriptions computed after scoring from the scored forecasts: `lead_day_metrics.csv`
and `energy_error.csv`. The raw data are not included.

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
| `REPRODUCTION_CHECK.json` | This package against the evaluated forecasts: all differences 0.0 kW. |

Model classes:

- `same information`: the model is given ANKYRA's 11 past, 10 future and 6 static features, and uses the part its
  architecture accepts;
- `load only`: the model receives the 1,344-hour load context only.
