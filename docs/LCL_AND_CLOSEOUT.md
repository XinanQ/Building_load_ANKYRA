# LCL evaluation and closeout of the last round (3 October 2026)

ANKYRA 2.0.1 remains the frozen point model. No new point or interval rule was adopted in this round. The original ten-population tables and BDG2 qualifications are unchanged. The machine-readable record is [`closeout_status.json`](../results/closeout_status.json).

## Centered daily-path route

The sole registered point proposal was a fixed beta = 0.5 centered RIDGE-L daily-path replacement, with off, micro-load and insufficient-history windows unchanged. The reused household early design face contains 562 windows from 562 units. RIDGE-L was refitted using each origin's permitted prefix on 526 supported active windows; the other 36 retain ANKYRA. Such local Ridge fits are supervised fitting and cannot inherit a training-free description.

The eligible donor's unit-equal geometric centered daily-path RMS was 0.08755% worse than ANKYRA and 3.59095% worse than TimesFM. These are month-aggregated centered-path diagnostics, not the primary hourly-by-day statistic or an overall model comparison. The donor endpoint direction is a conservative admission condition; its failure does not prove a mixture could not improve. The protocol field and machine status remain `STOP_NECESSITY_UNRESOLVED` for traceability.

The truth-selected daily oracle remained **UNRESOLVED**: on fixed support of 544 units it had 60 exact-zero unit/day risks in nine units. Candidate zeros were not dropped or replaced by an epsilon. This supplies no finite geometric gain or claim that a 2% bound was established. The oracle is undeployable and can violate the fixed candidate's energy identity.

The fixed-beta candidate was not scored. The other eight design faces, protection and cost stages were not triggered; this branch read no late or LCL targets and made no new foundation-model calls. The numerical cross-check used a separate implementation by the same agent, not an independent reviewer or a new experiment. Main evaluation and cross-check each opened the saved target member once (two formal reads total); the interrupted initial historical-input access count is unknown. Reused design evidence is not independent confirmation.

## Interval route

`STOP_INTERVAL_SOURCE_SUPPORT_GATE`: all 7,676 registered windows were retained, and at least 742 have no qualified mature complete-ANKYRA residual under the fixed sigma fitting cutoffs. The household face has 537 windows with no such residual and 25 with one; all 562 have fewer than four. Required all-window coverage and Winkler gates are therefore unresolved, and unsupported windows were not removed.

I1–I3 numerical replay, scoring, the pilot and GPU inference were not triggered. No new interval rule or coverage guarantee is established. This is a source-support stop, not a measured interval-accuracy failure. Current origins all meet their fixed sigma cutoffs; the support shortage concerns historical pseudo-origins and does not establish future-parameter use at current origins. Existing archive qualifications about source clocks, arrival/revision history and historically issued forecasts remain applicable.

## Cache and public API

The content/version-keyed cache is synthetic engineering staging only. Equality on real archive inputs, end-to-end integration and any performance benefit have not been established; nominal key matches are not input-certified cache hits. No public code changed.

Documentation now describes the actual existing early-return branches: only a micro-load return without the legacy off-state condition runs the full estimator history/category/temperature-scale checks. The off-state branch retains its existing checks and compatibility behavior. The returned flags are not validation or source-clock certificates. `within_day_kw` is the final anchored block; `foundation_within_day_kw` is the unmodified foundation shape.

## LCL final stage

The frozen ANKYRA 2.0.1 model was evaluated once without retuning. All 1,215 registered windows from 965 units were retained. The common late face has 710 windows from 710 units, selected by the frozen metadata-key intersection of seven trained baseline files, not by target or prediction values. This is the first scoring of the frozen 2.x version on LCL; the population's 1.x results were already known, so it is not a wholly unexposed population or an independent confirmation of all prior choices. It is not merged into the original ten-population ranks.

The source adapter now uses a fixed 15°C before the actual temperature record; missing load stays missing. The older adapter copied temperature from a later year into that padding. The matched-input 1.x ablation uses the same repaired input and fresh foundation forecasts as 2.0.1; the archived 1.x comparison is retained separately. Their difference must not be assigned entirely to a model change. Existing baselines keep their frozen input contracts. The own-clock weather check certifies the checked temperature dependencies, not original load timestamps, arrival/revision history, physical-hour interpretation or foundation-model pretraining independence. Historical internal replay is not evidence of forecasts actually issued then.

Percentages below are unit-equal geometric RMS improvements in favor of ANKYRA; bracketed numbers are **95% UM intervals on the log-RMS ratio**, not percentage intervals. These are month-aggregated hourly losses. Unavailable full-face comparisons are not ties, and the raw pairwise intervals are not Holm-adjusted superiority findings.

| Comparator | All 1,215 windows / 965 units | Common late 710 windows / 710 units |
|---|---:|---:|
| 1.x, matched input | +0.675%; [-0.009810, -0.003625] | +0.921%; [-0.012486, -0.005962] |
| 1.x, archived input | +0.625%; [-0.009460, -0.003017] | +0.890%; [-0.012415, -0.005346] |
| TimesFM | +1.240%; [-0.026234, +0.011858] | +1.311%; [-0.033120, +0.027040] |
| RIDGE | +1.932%; [-0.036164, -0.005245] | +1.198%; [-0.032569, +0.010077] |
| Chronos-2 | +1.163%; [-0.026008, +0.010800] | +0.970%; [-0.028421, +0.028541] |
| Chronos-2-X | +1.538%; [-0.030881, +0.006932] | +1.279%; [-0.032880, +0.025334] |
| TimesFM-X | +1.415%; [-0.029575, +0.008294] | +1.379%; [-0.030794, +0.025373] |
| GBT-T | Unavailable on this registered face | +8.254%; [-0.129657, -0.037581] |
| TiDE | Unavailable on this registered face | +2.640%; [-0.050380, -0.009490] |
| iTransformer-X | Unavailable on this registered face | +1.409%; [-0.033624, +0.019506] |

The matched-input 1.x no-harm gate L1 passed (registered log-RMS upper bound at most 0.01). On the fixed common face ANKYRA has mean unit rank 6.247887, the smallest of the fixed 21 models (Ridge: 6.483099); this modest descriptive rank difference is not a significant hourly advantage over Ridge on that face. L3 found no registered same-information baseline significantly better under its six-test Holm family; this direction-specific result does not establish equivalence, noninferiority to every baseline, or Holm-adjusted ANKYRA superiority over all six. The hourly contrasts with TimesFM are unresolved in both faces because their intervals cross zero.

Full-face descriptive readouts relative to TimesFM are: independent energy +39.205%, delivered energy +39.178%, raw trajectory peak +5.453%, and ANKYRA's envelope peak +77.708%. Energy references are TimesFM's trajectory integral. Both peak references are TimesFM's raw trajectory maximum; the envelope contrast compares different readout operators and does not certify true capacity adequacy or an achieved physical peak bound. These readouts were not selection criteria.

There were two off-state windows and no micro-load trigger. LCL therefore supplies no new effectiveness test of the post hoc micro-load rule. New LCL intervals were not assessed; the old 1.x interval result is not relabeled as a new 2.0.1 confirmation.

During source preparation, 250 earlier registered target segments were wholly or partly read as matured history for later origins. That use follows the later origin's prefix and precludes an all-target-values-unseen claim. Formal scoring opened each current target once after prediction and comparator freezes. The separate saved-output arithmetic audit passed 96,032 checks with zero numerical differences and opened the saved target once more: two formal-plus-audit reads in total. It made no new model, GPU or raw-data call. This is a reproducibility check on the same saved output, not another external experiment. See the [audit](../results/lcl_audit.json) and [exposure receipt](../results/lcl_exposure.json).

The completed inference run used 8,505 unique contexts and produced 8,537 forecasts including 32 outputs for the fixed batch-equivalence pilot. An earlier interrupted attempt completed at least 576 forecasts; its exact count is unknown and no scored output was used. Completed-run time including load/pilot was 147.85 seconds. Batch and individual inference were not bit-identical (maximum pilot relative difference 6.52253e-6). Combined point-model and matched-1.x computation took 691.37 seconds with Torch set to one CPU thread; actual NumPy BLAS thread counts were not measured. These are source/reproduction workloads, not a deployment-speed benchmark or evidence of cache acceleration.

Exports: [all registered pairwise](../results/lcl_pairwise.csv), [common late pairwise](../results/lcl_pairwise_late.csv), [fixed common ranks](../results/lcl_mean_unit_rank_late.csv), [six baseline-better Holm tests](../results/lcl_shared_information_holm.csv), [descriptive readouts](../results/lcl_readouts.csv), and [source result JSON](../results/lcl_results.json). All were exported from saved result JSON without rereading targets or predictions.


## Supplementary LCL curves and conventional errors

The saved-output auditor also generated descriptive summaries from its one in-memory target decode; these exports required no additional target read. They are separate from L1/L3 and do not replace Figure 9, Figure 9b or the original ten-population tables.

Daily curves and conventional errors are split into [all-window curves](../results/lcl_lead_day_metrics.csv), [common-late curves](../results/lcl_lead_day_metrics_late.csv), [all-window conventional errors](../results/lcl_conventional_metrics.csv), and [common-late conventional errors](../results/lcl_conventional_metrics_late.csv). The [definitions](../results/lcl_metric_definitions.json) specify their normalizers and support. Daily CV uses each unit's mean truth over the registered windows of the relevant face, rather than an own-history scale or whole-record mean. It is a descriptive normalization, not an input feature.

The curves retain zero-error units. Across the two source faces 619 geometric summary cells are `UNRESOLVED_ZERO_LOG_RISK` and remain blank, never zero or interpolated. Arithmetic means and medians have their own reported definitions. This differs from the older plotted support that excluded units with zero error in any model. The day-level geometric curves, month-level log-RMS pairwise statistic, pooled MSE and conventional unit summaries are distinct estimands.
