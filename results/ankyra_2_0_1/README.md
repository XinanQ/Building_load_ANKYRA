> **Archived record of ANKYRA 2.0.1 (packages 2.0.1 to 2.0.3; within-day trust estimated per lead block), kept
> unchanged beside the 2.1 results.** The current files are in [`results/`](../), with a full description of the
> columns in [`results/README.md`](../README.md).
>
> - These are the files of `results/` as released with package 2.0.3 (tag `v2.0.3`). Column names are those of the
>   current files.
> - ANKYRA 2.1 differs from 2.0.1 only in the within-day trust (one value per window instead of one per lead block).
>   Level, daily means, handover, energy readout and the off-state and micro-load rules are bit-identical, so files
>   that depend only on them, or that record the frozen-model checks made with 2.0.1, are identical to the current ones.
> - `REPRODUCTION_CHECK.json` is the check on package 2.0.3 (code of 2.0.2, model 2.0.1); `REPRODUCTION_CHECK_2_0_1.json`
>   is the check on package 2.0.1. In both, `faces` are the window sets checked (`goiener_confirm` = GoiEner
>   non-household, `households` = GoiEner households, `park` = Suzhou park), "panel" is the set of scored forecasts and
>   `v6` the working name of the 2.0 forecaster.
> - `robustness.csv` here was measured on 2.0.0, as stated in the 2.0.1 release.

# Results data (ANKYRA 2.0.1, archived)

All files describe **ANKYRA 2.0.1** (2.0.0 plus the micro-load rule) unless the file says otherwise; 2.0.0 is in
[`ankyra_2_0_0/`](../ankyra_2_0_0/) and 1.x in [`ankyra_1x/`](../ankyra_1x/). Scored statistics behind the figures and
tables of the 2.0.1 release, exported from the study's evaluation outputs; nothing was tuned. The BDG2 rows include the
micro-load rule, written after the BDG2 result of 2.0.0 had been seen.

**Files that differ from the current (2.1) files**: the within-day block and the quantities computed from the delivered
trajectory, plus the records that name the package.

| File | Content |
|---|---|
| `benchmark_pairwise.csv`, `benchmark_mean_unit_rank.csv` | ANKYRA 2.0.1 against the 20 baselines; mean per-unit ranks (Figures 2, 3, 12). |
| `rank_tests.csv`, `scaled_errors.csv` | Friedman, Nemenyi and Holm-corrected Wilcoxon rank tests; RMSSE and MASE (Figure 15). |
| `conventional_metrics.csv`, `conventional_metrics_late.csv` | Conventional errors, with 2.0.0 and 1.x as extra rows (Figure 8). |
| `ablation.csv` | ANKYRA 2.0.1 against 2.0.0, 1.x, F1 and F0 (Figure 4a). |
| `lead_day_metrics.csv`, `lead_day_energy.csv`, `ankyra_2_vs_1x_by_day.csv` | Hourly loss and energy error by forecast day (Figures 9, 9b, 10); the last with columns `ankyra_2_0_1`, `ankyra_2_0_0`, `ankyra_1x` and the four foundation-model variants. |
| `lead_weeks_first_read.csv` | Week-by-week contrasts against TimesFM (identical in 2.0.0 and 2.0.1). |
| `energy_error.csv` | Monthly energy error against the 20 baselines; BDG2 also without the three near-zero meters (Figure 11). |
| `block_shares.csv` | Block attribution (Figure 14). |
| `history_length.csv` | Contrasts by history length. |
| `peak_readout.csv` | Peak readout against four alternatives (Figure 5). |
| `intervals_households.json`, `intervals_by_population.csv`, `intervals_winkler_contrasts.csv` | Interval readout on households and on ten populations; Winkler contrasts for 2.0.1 and 2.0.0 (Figures 13, 16). |
| `bdg2_near_zero_sensitivity.csv` | BDG2 with and without the three near-zero meters, including 2.0.0 and 1.x rows. |
| `constants_sensitivity.csv` | One shrinkage constant changed at a time on the nine design sets, against 2.0.1. |
| `robustness.csv` | Stress test on 64 Drammen windows, measured on 2.0.0. |
| `example_window_cambridge.csv` | The Cambridge example window with the 2.0.1 forecast (Figures 6, 7). |
| `carrier_swap.csv`, `carrier_swap_x.csv`, `carrier_swap_combined.csv` | The anchoring of 2.0.1 with Chronos-2 and Chronos-2-X as foundation models, and the three configurations on the same windows. The current files repeat these runs with 2.1; the resolved counts are the same. |
| `REPRODUCTION_CHECK.json` | The reproduction check of package 2.0.3 (code of 2.0.2) on 484 windows of seven populations. |

**Files identical to the current ones**, kept so that the folder is a complete 2.0.1 set: `REPRODUCTION_CHECK_2_0_1.json`,
`bdg2_micro_load_windows.csv`, `cost_per_window.csv`, `datasets.csv`, `example_window_cambridge.json`,
`handover_granularity.csv`, `closeout_status.json`, the frozen-model checks made with 2.0.1 (`hkust_first_read.csv`,
`hkust_by_day.csv`, `helsinki_confirmation.csv`, `helsinki_criteria.json`, `helsinki_by_day.csv`) and the LCL
evaluation of 2.0.1 (`lcl_*`). The 2.1 re-evaluations of the frozen-model checks are in
[`../reevaluation_2_1.json`](../reevaluation_2_1.json).

Model classes:

- `same information`: the model is given ANKYRA's 11 past, 10 future and 6 static features, and uses the part its
  architecture accepts;
- `load only`: the model receives the 1,344-hour load context only.
