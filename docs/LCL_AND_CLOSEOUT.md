# Low Carbon London households: evaluation of ANKYRA 2.0.1

This page reports the one population that is not in the ten-population tables of [EVALUATION.md](EVALUATION.md): the
Low Carbon London (LCL) households. It also records two changes to the forecaster that were tried after 2.0.1 and not
adopted. ANKYRA 2.0.1 is unchanged by anything on this page. ANKYRA 2.1 (one within-day trust per window), adopted
later from a separate simplification study, was re-scored on LCL afterwards. That re-evaluation is reported
[below](#re-evaluation-with-ankyra-21) and does not replace the 2.0.1 result.

Terms used here are those of [EVALUATION.md](EVALUATION.md#estimands). The *improvement* is $100[1-\exp(r)]$, where
$r$ is the mean over households of the log ratio of ANKYRA's hourly RMS error to the other forecaster's; positive
favours ANKYRA. Intervals are 95% intervals of $r$ from 2,000 bootstrap replicates that resample households and
target months. A contrast is *resolved* when its interval excludes zero.

## LCL final stage

LCL was the last population scored, after the forecaster had been frozen as 2.0.1.

### Summary

- **Scored once, without retuning.** The frozen 2.0.1 forecaster was run on all 1,215 windows of 965 households on
  3 October 2026. No constant or rule was changed for LCL or after its result was seen.
- **Against ANKYRA 1.x:** 0.7% better on the same inputs, resolved.
- **Against the foundation models:** 1.2–1.5% better in the point estimate than TimesFM, Chronos-2, Chronos-2-X and
  TimesFM-X. None of these contrasts is resolved.
- **Rank.** On the 710 late windows ANKYRA has the lowest mean per-unit rank of the 21 forecasters (6.25; per-unit
  ridge 6.48). The difference from the ridge is small and not significant.
- **Not an unexposed population.** The LCL result of ANKYRA 1.x was known before 2.0 was designed. This is the first
  score of a 2.x version on LCL, not a first read of LCL.

### What LCL is and why it was held out

LCL is the smart-meter record of London households published by UK Power Networks, 23 November 2011 to 28 February
2014 ([source and preparation](DATA.md#11-low-carbon-london-households-uk)).

ANKYRA 1.x was scored on LCL against the load-only forecasters: third of 14 by mean per-unit rank on the late
windows, behind the per-unit ridge and iTransformer ([`results/ankyra_1x/`](../results/ankyra_1x/)). When the
equal-information comparison was set up, LCL was held in reserve. The covariate-informed baselines were not scored
on it, and it was not read while the within-day rule of 2.0 and the micro-load rule of 2.0.1 were designed, selected
and evaluated. The aim was to keep one population on which no 2.x rule had been chosen.

For that reason LCL is reported here and not merged into the ten-population tables, ranks and figures. Those are
unchanged.

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
  foundation-model forecasts as 2.0.1. *Archived 1.x* is the set of 1.x forecasts scored earlier, made with the old
  padding. Both are reported. The difference between 2.0.1 and archived 1.x is partly a change of input, so it must
  not be read as a change of model alone.
- **What was checked about the inputs.** The temperature values that the forecasts depend on were checked against
  the temperature record on its own clock, and the check passed. It does not certify the provider's load timestamps,
  later revisions of the data, or that the foundation models were not pretrained on LCL. The forecasts are a
  retrospective run; none was issued at the time.

### Results

Hourly error over the forecast month. "n/a" means that the forecaster has no forecast on that window set; it is not
a tie.

**All windows (1,215 windows, 965 households)**

| ANKYRA 2.0.1 against | Improvement | Log ratio | 95% interval (log scale) | Resolved |
|---|---:|---:|---|:---:|
| ANKYRA 1.x, matched input | +0.675% | −0.0068 | [−0.0098, −0.0036] | yes |
| ANKYRA 1.x, archived | +0.625% | −0.0063 | [−0.0095, −0.0030] | yes |
| TimesFM | +1.240% | −0.0125 | [−0.0262, +0.0119] | no |
| Chronos-2 | +1.163% | −0.0117 | [−0.0260, +0.0108] | no |
| Chronos-2-X | +1.538% | −0.0155 | [−0.0309, +0.0069] | no |
| TimesFM-X | +1.415% | −0.0142 | [−0.0296, +0.0083] | no |
| per-unit ridge | +1.932% | −0.0195 | [−0.0362, −0.0052] | yes |
| GBT-T, TiDE, iTransformer-X | n/a | n/a | n/a | n/a |

**Late windows (710 windows, 710 households)**

| ANKYRA 2.0.1 against | Improvement | Log ratio | 95% interval (log scale) | Resolved |
|---|---:|---:|---|:---:|
| ANKYRA 1.x, matched input | +0.921% | −0.0093 | [−0.0125, −0.0060] | yes |
| ANKYRA 1.x, archived | +0.890% | −0.0089 | [−0.0124, −0.0053] | yes |
| TimesFM | +1.311% | −0.0132 | [−0.0331, +0.0270] | no |
| Chronos-2 | +0.970% | −0.0097 | [−0.0284, +0.0285] | no |
| Chronos-2-X | +1.279% | −0.0129 | [−0.0329, +0.0253] | no |
| TimesFM-X | +1.379% | −0.0139 | [−0.0308, +0.0254] | no |
| per-unit ridge | +1.198% | −0.0121 | [−0.0326, +0.0101] | no |
| GBT-T | +8.254% | −0.0861 | [−0.1297, −0.0376] | yes |
| TiDE | +2.640% | −0.0268 | [−0.0504, −0.0095] | yes |
| iTransformer-X | +1.409% | −0.0142 | [−0.0336, +0.0195] | no |

- **All 20 baselines, late windows.** 11 contrasts are resolved in ANKYRA's favour, 9 are not resolved, and none is
  resolved against it. On all windows, 9 of the 13 available contrasts are resolved in ANKYRA's favour; the four
  foundation-model variants are not. The intervals are not adjusted for the number of comparisons, so these counts
  are not a set of significance findings. The other rows and the pooled MSE ratios are in the files listed below.
- **TimesFM.** The contrast is unresolved on both window sets: the intervals cross zero.
- **Mean per-unit rank, late windows.** ANKYRA 6.25, per-unit ridge 6.48, iTransformer 6.99, PatchTST 7.29, TiDE
  7.32, iTransformer-X 7.37, DLinear 7.55; TimesFM 10.00. ANKYRA's rank is the lowest of the 21. The ridge is not
  resolvably worse on these windows (table above), so the rank difference is a description, not a significant
  hourly advantage.

**What was fixed before scoring.** Two checks with a pass or fail, and one description. The study protocol calls
them L1, L3 and L2.

1. *No harm against 1.x on the same inputs (L1).* The upper end of the interval of the log ratio against
   matched-input 1.x had to be at most +0.01. It is −0.0036 on all windows and −0.0060 on the late windows. The
   check is met (field `no_harm_check` of `lcl_results.json`).
2. *No same-information baseline significantly better (L3).* Six one-sided bootstrap tests asked whether a baseline
   is better than ANKYRA on the late windows: the five same-information baselines (TiDE, iTransformer-X, GBT-T,
   Chronos-2-X, TimesFM-X) and the per-unit ridge, with Holm's correction over the six. No test rejects; every
   adjusted p-value is 1.0 (field `same_information_check`). This result has one direction only. It does not show
   that ANKYRA is equivalent to these baselines, non-inferior to every baseline, or significantly better than all
   six.
3. *Position (L2), a description without pass or fail.* ANKYRA's mean per-unit rank among the 21 forecasters on the
   late windows and the number of resolved contrasts, both reported above.

**Energy and peak readouts** (all windows, against TimesFM; descriptive, not used to select anything).

| ANKYRA readout | TimesFM reference | Improvement | Log ratio | 95% interval (log scale) |
|---|---|---:|---:|---|
| energy read from the level, before the projection onto nonnegative load | sum of the trajectory | +39.205% | −0.4977 | [−0.6012, −0.3870] |
| energy of the delivered trajectory | sum of the trajectory | +39.178% | −0.4972 | [−0.6008, −0.3869] |
| peak as the maximum of ANKYRA's trajectory | maximum of the trajectory | +5.453% | −0.0561 | [−0.0762, −0.0305] |
| ANKYRA's peak readout (the envelope of [METHOD.md](METHOD.md#readouts)) | maximum of the trajectory | +77.708% | −1.5010 | [−1.6377, −1.4177] |

The last row compares two different operators: ANKYRA's envelope against the plain maximum of TimesFM's trajectory,
not against the same readout applied to TimesFM. It does not show that the envelope bounds the realised peak.

**Rules and intervals.**

- Two windows are off-state windows. No window meets the micro-load condition, so LCL gives no test of the
  micro-load rule, which was written after the BDG2 result had been seen.
- Prediction intervals were not assessed for 2.0.1 or 2.1 on LCL. The interval result of 1.x is not relabelled as a 2.0.1
  result.

### Re-evaluation with ANKYRA 2.1

After ANKYRA 2.1 was adopted (6 October 2026), the same 1,215 windows were scored again with 2.1 against the same saved
baseline forecasts. This is a second read of the LCL targets and a re-evaluation, not a test; the 2.0.1 result above
remains the frozen evaluation. Source: [`reevaluation_2_1.json`](../results/reevaluation_2_1.json).

- 2.1 against 2.0.1: +0.130%, log ratio −0.0013 [−0.0025, −0.0007], resolved (all windows).
- Against matched-input 1.x: +0.804% [−0.0115, −0.0047] on all windows, +1.105% [−0.0150, −0.0073] on the late
  windows; both resolved, so L1 is met.
- Against TimesFM: +1.368% [−0.0277, +0.0101] on all windows, +1.494% [−0.0346, +0.0253] late; unresolved. Against
  Chronos-2, Chronos-2-X and TimesFM-X: +1.15% to +1.67%, unresolved.
- Per-unit ridge: +2.060% [−0.0376, −0.0069] on all windows, resolved; +1.382% [−0.0343, +0.0085] late, unresolved.
- Late windows: 11 of 20 contrasts resolved in ANKYRA's favour, none against; all windows: 9 of 13. Mean per-unit rank
  6.08, first of 21 (per-unit ridge 6.49, iTransformer 7.01). Same-information check: no test rejects.
- Readouts against TimesFM: energy from the level unchanged (+39.205%); delivered energy +39.218%; trajectory maximum
  +4.360% [−0.0627, −0.0184] (2.0.1: +5.453%); envelope peak +77.709%.
- These numbers are not in the `lcl_*` files, which hold 2.0.1.

### Daily curves and conventional errors

Loss by forecast day and the conventional error metrics were computed afterwards from the saved forecasts, as a
description. They are not among the three items fixed before scoring, and they do not replace Figures 9 and 9b or
the ten-population tables.

- **Normaliser.** The daily CV(RMSE) divides by each household's mean realised load over its scored windows of the
  window set. It is not a scale from the household's own history, and it is not an input of any forecaster.
- **Zero errors.** A household whose error is exactly zero on a day has no logarithm, so the geometric mean over
  households is undefined for that day. In these files such a cell is left blank and flagged in the `status` column
  (`geometric mean undefined`; 619 cells over the two window sets). It is not set to zero, interpolated, or computed
  after dropping the household. The arithmetic mean and the median are given beside it.
- **Not comparable with Figure 9.** The ten-population curves use a fixed set of units whose error is nonzero for
  every forecaster. The LCL curves keep every household. Do not join the two.
- The day-level curves, the monthly log ratio of the tables above, the pooled MSE ratio and the conventional
  metrics are four different summaries; they need not agree.

### Caveats

- **Earlier results were known.** The 1.x result on LCL had been seen. The LCL result of 2.0.1 is therefore not
  independent confirmation of every earlier choice.
- **Targets that are also history.** 250 target segments of earlier windows also serve, wholly or partly, as history
  for later origins of the same household. That use is legitimate, since each lies before the later origin, but it
  means that not every target value was unread when the forecasts were made. For scoring, each target was read once,
  after the forecasts and the baselines had been frozen.
- **Arithmetic re-check.** A second implementation, written within the same study, recomputed every reported
  statistic from the saved forecasts and targets: 96,032 comparisons, no difference. It read the saved targets once
  more. This is a reproducibility check on the same output. It is not an independent review and not new evidence
  ([`lcl_audit.json`](../results/lcl_audit.json)).
- **Pretraining.** LCL is a public data set that predates TimesFM 2.5 and Chronos-2. Whether it is in their
  pretraining corpora was not established.
- **Run.** The foundation model was run on 8,505 distinct contexts (8,537 forecasts, including 32 repeated for a
  fixed check of batched against single inference; the two differ by at most 6.52253×10⁻⁶ in relative terms, so
  they are not bit-identical). The run took 147.85 s including model load. An earlier attempt was interrupted after
  at least 576 forecasts; its exact count is unknown and none of its output was scored. ANKYRA 2.0.1 and
  matched-input 1.x together took 691.37 s with PyTorch on one CPU thread (the thread count of NumPy's linear
  algebra was not measured). These times describe this evaluation run. They are not a deployment benchmark.

### Files

All in [`results/`](../results/). The CSV files use the column names of the ten-population files
([`results/README.md`](../results/README.md)): `subset` is `full` (all windows) or `late`, `log_ratio` with `um_low`
and `um_high` is the log ratio with its interval, and `improvement_pct` is the improvement. Model keys are those of
the ten-population files (`RIDGE-L` is the per-unit ridge); the two versions of 1.x are `ANKYRA-1x-matched` and
`ANKYRA-1x-archived`.

| File | Content |
|---|---|
| [`lcl_pairwise.csv`](../results/lcl_pairwise.csv) | ANKYRA 2.0.1 against every forecaster and against both versions of 1.x, all windows |
| [`lcl_pairwise_late.csv`](../results/lcl_pairwise_late.csv) | the same on the late windows |
| [`lcl_mean_unit_rank_late.csv`](../results/lcl_mean_unit_rank_late.csv) | mean per-unit rank of the 21 forecasters, late windows |
| [`lcl_shared_information_holm.csv`](../results/lcl_shared_information_holm.csv) | the six tests of the same-information check; the ratio is the baseline's error over ANKYRA's, the reverse of the pairwise files |
| [`lcl_readouts.csv`](../results/lcl_readouts.csv) | the energy and peak readouts against TimesFM |
| [`lcl_lead_day_metrics.csv`](../results/lcl_lead_day_metrics.csv), [`lcl_lead_day_metrics_late.csv`](../results/lcl_lead_day_metrics_late.csv) | hourly error, daily energy error and cumulative energy error by forecast day |
| [`lcl_conventional_metrics.csv`](../results/lcl_conventional_metrics.csv), [`lcl_conventional_metrics_late.csv`](../results/lcl_conventional_metrics_late.csv) | RMSE, MAE, CV(RMSE), NMBE, WAPE |
| [`lcl_metric_definitions.json`](../results/lcl_metric_definitions.json) | definitions of the metrics in the four files above |
| [`lcl_results.json`](../results/lcl_results.json) | the complete result record from which the CSV files were exported |
| [`lcl_audit.json`](../results/lcl_audit.json) | record of the arithmetic re-check |

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
