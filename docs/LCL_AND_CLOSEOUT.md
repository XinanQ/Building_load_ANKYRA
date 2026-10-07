# Low Carbon London households: evaluation of ANKYRA 2.2

This page reports the Low Carbon London (LCL) households, the one population that is not in the ten-population
tables of [EVALUATION.md](EVALUATION.md). It also records two changes to the forecaster that were tried after 2.0.1
and not adopted. All LCL numbers on this page are those of **ANKYRA 2.2**. LCL was first scored once with the frozen
ANKYRA 2.0.1 (3 October 2026); 2.1 (one within-day trust per window), adopted later from a separate simplification
study, and then 2.2 (gap tolerance in the pseudo-origin bookkeeping) were run on the same windows, so its numbers are a
re-evaluation of targets already read. Every check and conclusion below is the same under 2.0.1 and 2.1, whose files
are in [`results/ankyra_2_0_1/`](../results/ankyra_2_0_1/) and [`results/ankyra_2_1/`](../results/ankyra_2_1/); the
one description that changed under 2.2 is noted where it appears (the by-day ranks).

Terms used here are those of [EVALUATION.md](EVALUATION.md#estimands). The *improvement* is $100[1-\exp(r)]$, where
$r$ is the mean over households of the log ratio of ANKYRA's hourly RMS error to the other forecaster's; positive
favours ANKYRA. Intervals are 95% intervals of $r$ from 2,000 bootstrap replicates that resample households and
target months. A contrast is *resolved* when its interval excludes zero.

## LCL final stage

LCL was the last population scored, after the forecaster had been frozen as 2.0.1.

### Summary

- **Scored without retuning.** The frozen 2.0.1 forecaster was run on all 1,215 windows of 965 households on
  3 October 2026, and 2.1 and 2.2 on the same windows after each was adopted. No constant or rule was changed for
  LCL or after its result was seen.
- **Against ANKYRA 1.x:** 1.0% better on the same inputs, resolved.
- **Against the foundation models:** 1.5–1.9% better in the point estimate than TimesFM, Chronos-2, Chronos-2-X and
  TimesFM-X. None of these contrasts is resolved.
- **Rank.** On the 710 late windows ANKYRA has the lowest mean per-unit rank of the 21 forecasters (5.87; per-unit
  ridge 6.51). The difference from the ridge is small and not significant.
- **Not an unexposed population.** The LCL result of ANKYRA 1.x was known before 2.0 was designed, and the 2.1 and
  2.2 numbers re-read targets already scored with 2.0.1. This is not a first read of LCL.

### What LCL is and why it was held out

LCL is the smart-meter record of London households published by UK Power Networks, 23 November 2011 to 28 February
2014 ([source and preparation](DATA.md#11-low-carbon-london-households-uk)).

ANKYRA 1.x was scored on LCL against the load-only forecasters: third of 14 by mean per-unit rank on the late
windows, behind the per-unit ridge and iTransformer ([`results/ankyra_1x/`](../results/ankyra_1x/)). When the
equal-information comparison was set up, LCL was held in reserve. The covariate-informed baselines were not scored
on it, and it was not read while the within-day rule of 2.0 and the micro-load rule of 2.0.1 were designed, selected
and evaluated. The aim was to keep one population on which no 2.x rule had been chosen. The single trust of 2.1 and
the gap tolerance of 2.2 were chosen after LCL had been scored with 2.0.1.

For that reason LCL is reported here and not merged into the ten-population tables and ranks. Those are unchanged.
Its per-day curves are one panel of Figures 9 and 9b ([below](#daily-curves-and-conventional-errors)).

### Windows and inputs

- **All windows:** 1,215 windows of 965 households. No window of the panel was dropped.
- **Late windows:** the 710 windows, one per household, on which all seven trained baselines have a saved forecast.
  Their origins lie after the baselines' training cutoff of 1 September 2013. The set was fixed from the index of the
  baselines' forecast files, not from load or forecast values.
- **Forecasters.** The 20 baselines of the ten-population comparison. On all windows only the 13 that are not
  trained per population are available; on the late windows all 20. The baselines' forecasts are the ones saved
  earlier; they were not rerun.
- **Temperature before the record starts.** The forecaster needs a record that starts on 1 January, so the LCL record
  is padded back to 1 January 2011. In the padding the load is unobserved and the temperature is a fixed 15 °C. The
  preparation used for 1.x had copied the temperature of the same hours one year later into the padding. The fixed
  value replaces it, so that no temperature stands at an hour before it was recorded.
- **Two versions of 1.x.** *Matched-input 1.x* is ANKYRA 1.x rerun on the repaired input, with the same
  foundation-model forecasts as ANKYRA. *Archived 1.x* is the set of 1.x forecasts scored earlier, made with the old
  padding. Both are reported. The difference between ANKYRA and archived 1.x is partly a change of input, so it must
  not be read as a change of model alone.
- **What was checked about the inputs.** The temperature values that the forecasts depend on were checked against
  the temperature record on its own clock, and the check passed. It does not certify the provider's load timestamps,
  later revisions of the data, or that the foundation models were not pretrained on LCL. The forecasts are a
  retrospective run; none was issued at the time.

### Results

Hourly error over the forecast month. "n/a" means that the forecaster has no forecast on that window set; it is not
a tie.

**All windows (1,215 windows, 965 households)**

| ANKYRA 2.2 against | Improvement | Log ratio | 95% interval (log scale) | Resolved |
|---|---:|---:|---|:---:|
| ANKYRA 1.x, matched input | +1.014% | −0.0102 | [−0.0142, −0.0064] | yes |
| ANKYRA 1.x, archived | +0.964% | −0.0097 | [−0.0139, −0.0059] | yes |
| TimesFM | +1.578% | −0.0159 | [−0.0303, +0.0080] | no |
| Chronos-2 | +1.501% | −0.0151 | [−0.0298, +0.0074] | no |
| Chronos-2-X | +1.874% | −0.0189 | [−0.0345, +0.0034] | no |
| TimesFM-X | +1.751% | −0.0177 | [−0.0339, +0.0046] | no |
| per-unit ridge | +2.267% | −0.0229 | [−0.0399, −0.0082] | yes |
| GBT-T, TiDE, iTransformer-X | n/a | n/a | n/a | n/a |

**Late windows (710 windows, 710 households)**

| ANKYRA 2.2 against | Improvement | Log ratio | 95% interval (log scale) | Resolved |
|---|---:|---:|---|:---:|
| ANKYRA 1.x, matched input | +1.308% | −0.0132 | [−0.0180, −0.0085] | yes |
| ANKYRA 1.x, archived | +1.277% | −0.0129 | [−0.0178, −0.0079] | yes |
| TimesFM | +1.696% | −0.0171 | [−0.0366, +0.0237] | no |
| Chronos-2 | +1.357% | −0.0137 | [−0.0324, +0.0256] | no |
| Chronos-2-X | +1.665% | −0.0168 | [−0.0366, +0.0216] | no |
| TimesFM-X | +1.764% | −0.0178 | [−0.0352, +0.0222] | no |
| per-unit ridge | +1.584% | −0.0160 | [−0.0371, +0.0069] | no |
| GBT-T | +8.613% | −0.0901 | [−0.1333, −0.0408] | yes |
| TiDE | +3.021% | −0.0307 | [−0.0540, −0.0135] | yes |
| iTransformer-X | +1.794% | −0.0181 | [−0.0388, +0.0158] | no |

- **All 20 baselines, late windows.** 11 contrasts are resolved in ANKYRA's favour, 9 are not resolved, and none is
  resolved against it. On all windows, 9 of the 13 available contrasts are resolved in ANKYRA's favour; the four
  foundation-model variants are not. The intervals are not adjusted for the number of comparisons, so these counts
  are not a set of significance findings. The other rows and the pooled MSE ratios are in the files listed below.
- **TimesFM.** The contrast is unresolved on both window sets: the intervals cross zero.
- **Mean per-unit rank, late windows.** ANKYRA 5.87, per-unit ridge 6.51, iTransformer 7.02, PatchTST 7.31, TiDE
  7.36, iTransformer-X 7.40, DLinear 7.59; TimesFM 10.03. ANKYRA's rank is the lowest of the 21. The ridge is not
  resolvably worse on these windows (table above), so the rank difference is a description, not a significant
  hourly advantage.
- **2.2 against 2.1:** +0.212%, log ratio −0.0021 [−0.0039, −0.0004], resolved (all windows). **2.1 against 2.0.1:**
  +0.130%, log ratio −0.0013 [−0.0025, −0.0007], resolved (all windows).

**What was fixed before scoring.** Two checks with a pass or fail, and one description. The study protocol calls
them L1, L3 and L2. They were fixed for the 2.0.1 scoring; under 2.1 and 2.2 they read the same.

1. *No harm against 1.x on the same inputs (L1).* The upper end of the interval of the log ratio against
   matched-input 1.x had to be at most +0.01. It is −0.0064 on all windows and −0.0085 on the late windows. The
   check is met.
2. *No same-information baseline significantly better (L3).* Six one-sided bootstrap tests asked whether a baseline
   is better than ANKYRA on the late windows: the five same-information baselines (TiDE, iTransformer-X, GBT-T,
   Chronos-2-X, TimesFM-X) and the per-unit ridge, with Holm's correction over the six. No test rejects; every
   adjusted p-value is 1.0 ([`lcl_shared_information_holm.csv`](../results/lcl_shared_information_holm.csv)). This
   result has one direction only. It does not show that ANKYRA is equivalent to these baselines, non-inferior to every
   baseline, or significantly better than all six.
3. *Position (L2), a description without pass or fail.* ANKYRA's mean per-unit rank among the 21 forecasters on the
   late windows and the number of resolved contrasts, both reported above.

**Energy and peak readouts** (all windows, against TimesFM; descriptive, not used to select anything).

| ANKYRA readout | TimesFM reference | Improvement | Log ratio | 95% interval (log scale) |
|---|---|---:|---:|---|
| energy read from the level, before the projection onto nonnegative load | sum of the trajectory | +38.726% | −0.4898 | [−0.5950, −0.3801] |
| energy of the delivered trajectory | sum of the trajectory | +38.726% | −0.4898 | [−0.5951, −0.3802] |
| peak as the maximum of ANKYRA's trajectory | maximum of the trajectory | +4.711% | −0.0483 | [−0.0735, −0.0219] |
| ANKYRA's peak readout (the envelope of [METHOD.md](METHOD.md#readouts)) | maximum of the trajectory | +77.570% | −1.4948 | [−1.6302, −1.4182] |

The last row compares two different operators: ANKYRA's envelope against the plain maximum of TimesFM's trajectory,
not against the same readout applied to TimesFM. It does not show that the envelope bounds the realised peak.

**Rules and intervals.**

- Two windows are off-state windows. No window meets the micro-load condition, so LCL gives no test of the
  micro-load rule, which was written after the BDG2 result had been seen.
- Prediction intervals were not assessed for 2.0.1, 2.1 or 2.2 on LCL. The interval result of 1.x is not relabelled
  as a 2.x result.

### Daily curves and conventional errors

Loss by forecast day and the conventional error metrics were computed afterwards from the saved forecasts, as a
description. They are not among the three items fixed before scoring.

- **Figures 9 and 9b.** The LCL panel of Figures 9 and 9b ([`lcl_by_day.csv`](../results/lcl_by_day.csv)) uses the
  definitions of those figures: the 21 forecasters on the 710 late windows, geometric means over one fixed set of 704
  households whose errors are nonzero for every forecaster. There ANKYRA is the lowest of the 21 for hourly error on
  three days (22, 24 and 28) and second to fifth on the others, and fifth to eleventh for the error of energy to date.
  Under 2.1 it was not the lowest on any day (second to fifth hourly, fifth to twelfth for energy to date); this
  description changed under 2.2.
- **All households.** The files `lcl_lead_day_metrics*.csv` keep every household instead, on both window sets. Their
  daily CV(RMSE) divides by each household's mean realised load over its scored windows of the window set. It is not
  a scale from the household's own history, and it is not an input of any forecaster.
- **Zero errors.** A household whose error is exactly zero on a day has no logarithm, so the geometric mean over
  households is undefined for that day. In those files such a cell is left blank and flagged in the `status` column
  (`geometric mean undefined`; 611 cells over the two window sets). It is not set to zero, interpolated, or computed
  after dropping the household. The arithmetic mean and the median are given beside it.
- **Two curve families.** `lcl_by_day.csv` (fixed unit set, the figure panel) and `lcl_lead_day_metrics*.csv` (every
  household) are different summaries; do not join them.
- The day-level curves, the monthly log ratio of the tables above, the pooled MSE ratio and the conventional
  metrics are four different summaries; they need not agree.

### Caveats

- **Earlier results were known.** The 1.x result on LCL had been seen, and the 2.1 and 2.2 numbers re-read targets
  already scored with 2.0.1. The LCL result is therefore not independent confirmation of every earlier choice.
- **Targets that are also history.** 250 target segments of earlier windows also serve, wholly or partly, as history
  for later origins of the same household. That use is legitimate, since each lies before the later origin, but it
  means that not every target value was unread when the forecasts were made. For the 2.0.1 scoring each target was
  read once, after the forecasts and the baselines had been frozen; the 2.1 and 2.2 scorings read them again.
- **Arithmetic re-check.** For the 2.0.1 scoring a second implementation, written within the same study, recomputed
  every reported statistic from the saved forecasts and targets: 96,032 comparisons, no difference. It read the saved
  targets once more. This is a reproducibility check on the same output. It is not an independent review and not new
  evidence ([`ankyra_2_0_1/lcl_audit.json`](../results/ankyra_2_0_1/lcl_audit.json)). The 2.1 and 2.2 files were
  written by the same code after it had reproduced the 2.0.1 files; no second-implementation re-check of the 2.1 or
  2.2 files is recorded.
- **Pretraining.** LCL is a public data set that predates TimesFM 2.5 and Chronos-2. Whether it is in their
  pretraining corpora was not established.
- **Run (the 2.0.1 scoring).** The foundation model was run on 8,505 distinct contexts (8,537 forecasts, including 32
  repeated for a fixed check of batched against single inference; the two differ by at most 6.52253×10⁻⁶ in relative
  terms, so they are not bit-identical). The run took 147.85 s including model load. An earlier attempt was
  interrupted after at least 576 forecasts; its exact count is unknown and none of its output was scored. ANKYRA
  2.0.1 and matched-input 1.x together took 691.37 s with PyTorch on one CPU thread (the thread count of NumPy's
  linear algebra was not measured). These times describe that evaluation run. They are not a deployment benchmark.
  2.1 and 2.2 were run from the same frozen inputs.

### Files

All in [`results/`](../results/); they hold ANKYRA 2.2, and the 2.1 and 2.0.1 versions are in
[`results/ankyra_2_1/`](../results/ankyra_2_1/) and [`results/ankyra_2_0_1/`](../results/ankyra_2_0_1/). The CSV files use the column names of the ten-population files
([`results/README.md`](../results/README.md)): `subset` is `full` (all windows) or `late`, `log_ratio` with `um_low`
and `um_high` is the log ratio with its interval, and `improvement_pct` is the improvement. Model keys are those of
the ten-population files (`RIDGE-L` is the per-unit ridge); the two versions of 1.x are `ANKYRA-1x-matched` and
`ANKYRA-1x-archived`.

| File | Content |
|---|---|
| [`lcl_pairwise.csv`](../results/lcl_pairwise.csv) | ANKYRA against every forecaster and against both versions of 1.x, all windows |
| [`lcl_pairwise_late.csv`](../results/lcl_pairwise_late.csv) | the same on the late windows |
| [`lcl_mean_unit_rank_late.csv`](../results/lcl_mean_unit_rank_late.csv) | mean per-unit rank of the 21 forecasters, late windows |
| [`lcl_shared_information_holm.csv`](../results/lcl_shared_information_holm.csv) | the six tests of the same-information check; the ratio is the baseline's error over ANKYRA's, the reverse of the pairwise files |
| [`lcl_readouts.csv`](../results/lcl_readouts.csv) | the energy and peak readouts against TimesFM |
| [`lcl_by_day.csv`](../results/lcl_by_day.csv) | the LCL panel of Figures 9 and 9b: hourly error and error of energy to date by forecast day, fixed unit set, late windows |
| [`lcl_lead_day_metrics.csv`](../results/lcl_lead_day_metrics.csv), [`lcl_lead_day_metrics_late.csv`](../results/lcl_lead_day_metrics_late.csv) | hourly error, daily energy error and cumulative energy error by forecast day, every household |
| [`lcl_conventional_metrics.csv`](../results/lcl_conventional_metrics.csv), [`lcl_conventional_metrics_late.csv`](../results/lcl_conventional_metrics_late.csv) | RMSE, MAE, CV(RMSE), NMBE, WAPE |
| [`lcl_metric_definitions.json`](../results/lcl_metric_definitions.json) | definitions of the metrics in the four files above |
| [`lcl_results.json`](../results/lcl_results.json) | the result record (2.2), with 2.2 against 2.1 and 2.1 against 2.0.1; the CSV files are extracts of it |

The record of the arithmetic re-check of the 2.0.1 scoring is
[`ankyra_2_0_1/lcl_audit.json`](../results/ankyra_2_0_1/lcl_audit.json).

## Two changes that were tried and not adopted

After 2.0.1, two further changes were examined. Each had a check, fixed in writing before it was run, that decided
whether the change would be scored at all. Both stopped at that check. Neither was scored on any test window or on
LCL, and neither is in the package. The machine-readable record is
[`closeout_status.json`](../results/closeout_status.json). Its `status_code` fields carry the labels of the study
protocol; in both cases they mean that the change stopped at its check and nothing was scored.

### 1. A daily path taken partly from the per-unit ridge

**The idea.** On households the per-unit ridge is the one baseline that beats ANKYRA for the typical unit
([EVALUATION.md](EVALUATION.md#rank-significance-tests)). The per-unit ridge is a regression on the calendar and
climatological temperature, refitted for each unit at every origin (`RIDGE-L` in the ten-population result files).
The change would have replaced ANKYRA's centred daily path by a fixed half-and-half blend of ANKYRA's path and the
ridge's. Off-state windows, micro-load windows and windows with too little history would have stayed as they are.

**The check.** The blend would be scored only if the ridge's daily path alone was at least as accurate as ANKYRA's
on the design windows: the 562 pre-cutoff windows of 562 GoiEner households, which had already been used to design
the 2.0 rule.

**The result.** The ridge was refitted at each origin from data before that origin on the 526 windows with enough
history; the other 36 keep ANKYRA's path. On the centred daily path over the month (unit-equal geometric RMS) the
ridge was 0.08755% worse than ANKYRA and 3.59095% worse than TimesFM. The check failed and the blend was not scored.
No other design set, no post-cutoff window and no LCL window was read, and no foundation-model forecast was made.

**What this does and does not show.**

- The check is conservative. A blend can improve on both of its parts, so the result does not prove that the blend
  would not have helped.
- The two percentages are diagnostics of the daily path. They are not the hourly error by forecast day and not a
  comparison of whole forecasters.
- An upper bound was also planned: the best choice between the two paths on each day, made with the realised load.
  It could not be evaluated. On the 544 units it applies to, 60 unit-days in nine units have an error of exactly
  zero, and the geometric mean is then undefined. The zeros were not dropped or replaced by a small number. So there
  is no finite estimate of the attainable gain, and no bound on it was established (the protocol's reference value
  was 2%). Such a choice could not be deployed, and it can break the energy identity of the blend.
- A ridge fitted at every origin is a supervised fit. A forecaster that used it could not be described as
  training-free.
- The numbers were recomputed by a second implementation within the same study. That is not an independent review,
  and design windows that were used before are not independent confirmation.

### 2. An interval built from ANKYRA's own earlier errors

**The idea.** The interval of [METHOD.md](METHOD.md#readouts) uses the residuals of the historical pseudo-forecasts.
The change would have used the residuals of complete ANKYRA forecasts made at earlier pseudo-origins of the same
unit. A residual counts only if that earlier forecast could have been made at the time: its pseudo-origin must lie
after the period on which the temperature scale `temp_sigma_std` was fitted (the first 244 days of the record), and
its whole 744-hour target must precede the current origin.

**The check.** Coverage and the Winkler score were to be judged on all 7,676 windows of the design sets, with no
window removed.

**The result.** At least 742 of the 7,676 windows have no usable earlier residual. Of the 562 household design
windows, 537 have none and 25 have one; none has four or more. The criteria on all windows could therefore not be
evaluated. The unsupported windows were not removed, and nothing was scored: the three candidate interval rules
were not run, and no foundation-model forecast was made.

**What this does and does not show.**

- The change stopped for lack of usable earlier forecasts. It is not a measured failure of interval accuracy.
- No new interval and no coverage guarantee is established. The interval of the package is unchanged, with the
  limits stated in [EVALUATION.md](EVALUATION.md#readouts).
- Every evaluation origin lies after the fitting period of its temperature scale. The shortage concerns the earlier
  pseudo-origins only; it does not show that any evaluated forecast used a parameter fitted on later data.

A cache for foundation-model forecasts was also tried, on artificial inputs only. It is not in the package, and no
speed gain was measured.
