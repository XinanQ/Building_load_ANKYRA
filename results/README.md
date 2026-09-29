# Results data

Scored statistics behind the figures and tables. Everything was exported from the study's evaluation outputs;
nothing here is recomputed or tuned. The raw data are not included.

| File | Content |
|---|---|
| `benchmark_pairwise.csv` | ANKYRA against every external forecaster, per population. `subset`: `full` (all windows) or `late` (origins after the training cutoff, where trained models exist). Fields: unit-equal log RMS ratio (negative favours ANKYRA), 95% unit-and-month bootstrap interval (`um_low`, `um_high`), improvement `100[1 − exp(r)]`, pooled MSE ratio. |
| `benchmark_mean_unit_rank.csv` | Mean per-unit rank of ANKYRA and each external forecaster (models ranked within each unit by RMSE). |
| `ablation.csv` | ANKYRA against its reduced versions: without the off-state rule (F1), and the fixed division of labour (F0). |
| `lead_weeks_first_read.csv` | Week-by-week contrasts against TimesFM and the estimated weekly weight on the model, on the three populations scored first after the handover was fixed. |
| `peak_readout.csv` | Peak operator on ANKYRA's daily means against the trajectory maximum, the same readout on TimesFM and on the fixed division, and last month's observed peak. |
| `intervals_households.json` | Pseudo-origin interval around ANKYRA vs around the fixed division and the native quantiles of TimesFM and Chronos-2 (coverage, width, Winkler, pinball). |
| `conventional_metrics.csv` | RMSE, MAE (unit mean, kW); CV(RMSE), NMBE, WAPE (unit median, %); pooled WAPE. |
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
