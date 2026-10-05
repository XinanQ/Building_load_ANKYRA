# Method

This document describes ANKYRA 2.0.1, the model implemented by packages 2.0.1 to 2.0.3 (2.0.2 masks hours marked
unobserved once for every branch; 2.0.3 changes documentation only). The model versions differ in two places:

- 1.x used the foundation model's within-day shape unchanged. Section [Within-day shape](#within-day-shape) gives the
  rule introduced in 2.0.
- 2.0.1 adds the [micro-load rule](#off-state-and-micro-load-rules) to 2.0.0. It changes the forecast only when the
  whole 1,344-hour context stays within $10^{-3}$ kW of zero.

`forecast(..., micro_load_rule=False)` reproduces 2.0.0 exactly, and
`forecast(..., within_anchor=False, micro_load_rule=False)` reproduces 1.x exactly.

Two changes examined after 2.0.1, a daily path taken partly from a per-unit ridge regression and a new interval
rule, were not adopted and change nothing described here
([record](LCL_AND_CLOSEOUT.md#two-changes-that-were-tried-and-not-adopted)).

Contents: [Information at the origin](#information-at-the-origin) ·
[Inputs and features](#inputs-and-features-the-shared-information-set) ·
[Three orthogonal blocks](#three-orthogonal-blocks) · [Level](#level) · [Centred daily path](#centred-daily-path) ·
[Within-day shape](#within-day-shape) · [Week-by-week handover](#week-by-week-handover) ·
[Off-state and micro-load rules](#off-state-and-micro-load-rules) · [Readouts](#readouts) ·
[Output fields](#output-fields) · [Constants](#constants)

## Information at the origin

A forecast at origin $o$ is a function of the following, and nothing else:

- load and temperature at hours $t<o$;
- the calendar type (weekday or public holiday) of the 31 forecast days;
- the unit's category, which selects a fixed temperature-signature prior. The prior was fitted once on BDG2 windows
  ending before July 2016 and is never refitted. One category, Commercial, has no prior
  ([Level](#the-category-commercial-has-no-prior));
- a fixed temperature-anomaly scale, `temp_sigma_std`, set before the first origin
  ([definition](#the-temperature-anomaly-scale-temp_sigma_std));
- the daylight-saving rule of the unit's region (EU, US or none), used only to match analog days;
- the foundation model's forecasts from the 1,344 hours before $o$ and before each pseudo-origin $o-744k$.

Weights are estimated at pseudo-origins inside the record.

- Every pseudo-target ends by $o$.
- Each level pseudo-forecast at $o-744k$ uses only data before $o-744k$.
- The weekly handover uses the realised daily means of these pseudo-targets.

Two exceptions concern only the pre-origin record.

- One daily-path candidate, the path implied by the level construction, reuses the weather weight estimated at the
  origin. Its pseudo-errors are therefore not strictly out of sample with respect to that weight, although all of
  them precede the origin.
- The temperature-anomaly scale is fitted once, on the first 244 days of a population's record. A pseudo-origin that
  falls inside those days uses a scale that reflects temperature recorded after it. All of that temperature precedes
  the origin.

Two fixed components come from outside the unit's record: the pretrained foundation model and the signature prior.
Neither sees the unit's future. Both may, however, reflect data recorded later than the oldest evaluation windows, for
example the London households of 2011–2014.

[`tests/test_no_future_information.py`](../tests/test_no_future_information.py) changes every value after the origin,
or after each pseudo-origin, and checks that the forecast, the model's inputs, the pseudo-origin errors and the interval
are unchanged.

These tests establish input isolation in the implementation. They do not show that the inputs themselves carry no
later information. Three things lie upstream of the implementation: the providers' gap filling (imputed or zero-filled
hours are masked where documented), later quality control of weather archives, and the pretraining corpora. The
package's input checks are numerical: they cannot certify the providers' timestamps or later revisions of a record,
nor the period on which the supplied temperature-anomaly scale was fitted. The evaluation is a retrospective run; no
forecast in it was issued at the time.

## Inputs and features: the shared information set

Every forecaster in the evaluation — ANKYRA and the five same-information baselines — was given the same information,
fixed in writing before the baselines were run. ANKYRA receives it as the raw record (load, temperature, day types,
category) and forms its own quantities from it; the baselines receive it as the engineered features their
architectures accept. Nothing in the set is observed after the origin.

**Hourly features** (past = the 1,344-hour context, future = the 744-hour horizon):

| # | Feature | Past | Future | Construction | What ANKYRA makes of it |
|---|---|:---:|:---:|---|---|
| 1 | load | observed | — | per-unit z-score; statistics from the context or from before the training cutoff | level candidates, daily-path candidates, analog-day shapes, pseudo-origin errors, the foundation model's context |
| 2 | temperature | observed | climatology | horizon values are the frozen annual harmonic fitted on pre-origin temperature; **observed future temperature is never used** | weather-adjusted level and path candidates (signature response), analog-day selection |
| 3 | load one year earlier | ✓ | ✓ | $t-8{,}736$ h (52 weeks, weekday-aligned; always before $o$), same normalisation as 1, 0 where missing | the annual level and path candidates |
| 4 | availability of 3 | ✓ | ✓ | 1 where feature 3 is observed | annual candidates switched off without support |
| 5–6 | hour of day | sin, cos | sin, cos | period 24 | the hour grid of every block |
| 7–8 | weekday | sin, cos | sin, cos | period 7 | day types Monday … Sunday |
| 9–10 | day of year | sin, cos | sin, cos | period 365.25 | climatology phase, analog-day window (±14 days) |
| 11 | holiday / non-working day | ✓ | ✓ | day type 7 (public holiday) or Saturday/Sunday | day type 7 in every day-typed quantity |

Dimensions: 11 past, 10 future (features 2–11).

**Static features** (one set per unit): the category (Industrial, Office, Public, Residential, Commercial; one-hot,
the same label ANKYRA uses for its signature prior) and the log ratio of the long-history mean (at most 8,760 h) to the
context mean. Six dimensions.

**How each forecaster receives the set**

| Forecaster | Receives | Not accepted by the architecture |
|---|---|---|
| ANKYRA | the raw record behind all 11 + 10 + 6 features, plus the foundation model's forecasts at $o$ and $o-744k$ | — |
| TiDE | 11 past, 10 future, 6 static | — |
| iTransformer-X | 11 past as variable channels, 6 static as constant channels | future covariates |
| GBT-T | 21 features per forecast hour: three load aggregates, features 3–4, two temperature values, seven calendar values, the lead time, six static | — |
| Chronos-2-X | features 2–11 as past and known-future covariates | static features |
| TimesFM-X | features 2–11 through its linear covariate regression, the category as a categorical covariate | — |
| PatchTST | 11 past + 6 static as channels, but channel-independent: its load forecast equals the load-only one | information between channels |
| load-only models (TimesFM, Chronos-2, DLinear, iTransformer, LSTM, Holt–Winters, MSTL, naive and profile forecasters) | feature 1 only | — |
| per-unit ridge | calendar and climatological temperature, refitted at every origin | — |

**Deliberately excluded**: observed future weather; humidity and other meteorological variables (available for one
population only); hand-made signal transforms (smoothing, wavelet, Fourier or EMD decompositions), which add no
information and are a common source of look-ahead; load-derived statistics (used only inside GBT-T, which cannot read
a sequence). The feature set was fixed in writing before the baselines were run. The baselines' code, with its
assertions on every feature's time index, is not in this repository; the evaluation summary is in
[EVALUATION.md](EVALUATION.md#baselines).

## Three orthogonal blocks

At origin $o$ a forecast $F_{d,h}$ covers $D=31$ origin-aligned days of $H=24$ hours, $T=744$ hours in all. Define:

- the level $\ell(v)=T^{-1}\sum_{d,h}v_{d,h}$;
- the centred daily path $b_d(v)=H^{-1}\sum_h v_{d,h}-\ell(v)$;
- the within-day path $w_{d,h}(v)=v_{d,h}-H^{-1}\sum_r v_{d,r}$.

These are orthogonal projections of ranks 1, 30 and 713, so for an error $e=F-y$

$$\frac1T\sum_{d,h}e_{d,h}^2=\ell(e)^2+\frac1D\sum_d b_d(e)^2+\frac1T\sum_{d,h}w_{d,h}(e)^2 .$$

Replacing one block of a forecast changes its mean squared error by exactly the change in that block's loss. ANKYRA
uses this identity as a design rule: each block goes to the source that estimates it best.

- Because 7 and 31 are coprime, the 744-hour window has no separate weekly Fourier subspace.
- Weekly effects therefore enter the daily-path and within-day blocks and are represented by day types (Monday = 0 …
  Sunday = 6, holiday = 7).

The four-block refinement behind the Fourier statement, and the replacement calculus built on the identity, are P1–P6
in [theory/PROOFS.md](../theory/PROOFS.md).

Code: `ankyra/blocks.py`; the properties as operators: `theory/operators.py`.

## Level

Load is normalised by the mean $l_0$ and standard deviation $s_0$ of the 744 hours before the origin, with $s_0$
floored at $\max(0.01|l_0|,10^{-3})$ kW. A record whose whole context stays within the $10^{-3}$ kW floor of zero
is not normalised by its own scale; since 2.0.1 it is handled by the
[micro-load rule](#off-state-and-micro-load-rules).

**Six historical candidates.** Each of three means comes with and without weather adjustment:

- the recent 7-day mean;
- the long-history mean over at most 8,760 hours;
- the mean of the 744-hour window one year earlier.

Unadjusted candidates add a day-type offset estimated from the last eight weeks. Adjusted candidates replace the
temperature response of their own window by the expected response over the target days. No observed future weather
is used.

**Temperature signature.** The response is the unit's *temperature signature*: a convex piecewise-linear function of
the daily-mean temperature, with hinges every 5 °C from −10 °C to 40 °C. It is fitted on the unit's last 365 days
before the origin and shrunk towards the fixed prior curve of the unit's category. With fewer than 60 observed days
the prior curve is used as it is.

**Foundation-model candidate.** One further candidate, TimesFM's own window mean, is origin-normalised with the
calendar offset removed. The implementation is six historical candidates plus this one.

**Weights.** Each candidate's window-mean error is computed at up to $K=12$ earlier pseudo-origins $o-744k$ ($k\le6$ for
the model candidate, from forecasts issued at those origins). With $s_j$ the RMS of at least two such errors,

$$\widetilde w_j=\frac{I_j/\max(s_j,10^{-6})^2}{\sum_r I_r/\max(s_r,10^{-6})^2},\qquad
w_j=\frac{K_{\rm eff}\,\widetilde w_j+K_0\,w_{0j}}{K_{\rm eff}+K_0},\quad K_0=8,$$

where $I_j=1$ if candidate $j$ has at least two pseudo-origin errors and 0 otherwise, $w_0$ is uniform over the
supported candidates ($I_j=1$), and $K_{\rm eff}$ counts pseudo-origins with complete evidence.

- With complete records $K_{\rm eff}(m)=\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$ for a history of $m$ hours.
- Below two errors the weights are equal.
- The annual candidate needs 10,248 hours (about 14 months) before it can be weighted.
- In the historical estimator, with matched support and no candidate deleted at the origin, the shrinkage keeps the
  total weather weight within $[(1-\rho)/2,(1+\rho)/2]$, $\rho=K_{\rm eff}/(K_{\rm eff}+8)$. With the model candidate
  the prior weather mass is 3/7 once all seven candidates are supported, and the general bound of P8 applies.

These support and shrinkage properties are P7–P9 in [theory/PROOFS.md](../theory/PROOFS.md).

Code: `ankyra/history/` (frozen reference estimator), `ankyra/core.py` (`level_with_model_candidate`).

### The temperature-anomaly scale `temp_sigma_std`

The weather-adjusted candidates need the expected temperature response on days whose temperature is not known. The
expectation is taken over a normal temperature anomaly around the pre-origin climatology of each target day. Its
standard deviation is the argument `temp_sigma_std` of `ankyra.forecast`. It is one positive number per population,
in units of 10 °C: 0.25 means 2.5 °C.

The package does not estimate it; the caller supplies it. The study computed it as follows:

1. standardise the temperature as $(T-15\,^\circ\mathrm{C})/10\,^\circ\mathrm{C}$;
2. take daily means;
3. subtract a centred 31-day moving mean, which leaves the daily anomaly;
4. take the standard deviation of that anomaly, pooled over the units of the population, on the first 244 days of
   the record (15 days are dropped at each end, where the moving mean is incomplete).

It is fitted once, before the first origin, and then kept fixed. The package checks only that the value is a finite
positive number; it cannot check when or how it was fitted. The values used for the evaluation populations are not
listed in this repository.

### The category Commercial has no prior

The frozen configuration holds a prior signature curve for Industrial, Office, Public and Residential. It holds none
that the code reads for Commercial: the fifth curve of `ankyra/history/frozen_config.json` is stored under the key
`group_4`, and the estimator looks curves up by category name. A unit labelled Commercial therefore gets a temperature
signature of zero.

- Its three weather-adjusted level candidates equal the unadjusted ones, and its weather-response daily path is zero.
  The rest of the forecaster is unaffected.
- This is the behaviour that was evaluated. In the scored populations, 13 BDG2 units and one of the four Suzhou
  series are Commercial.
- It is kept as it is, because the forecaster's numbers are frozen. For a new Commercial unit, the choice is between
  this behaviour and one of the four categories that have a prior.

## Centred daily path

Seven candidate paths for the 31 daily means:

- the path implied by the level construction;
- day-type offsets from the last 8, 4 and 2 weeks;
- day-type offsets of the annual window;
- that window's daily means in date order;
- the weather-response path.

They are weighted as above with $K_0=2$, and the result sums to zero, so it redistributes energy between days
without changing the level.

## Within-day shape

**Foundation shape.** $w^T$ is the day-demeaned TimesFM 2.5 point forecast from the same 1,344 hours of load. No
covariates or fine-tuning are used. In 1.x this was the within-day block.

**Analog-day shape (2.0).** For each horizon day $d$, the unit's own *analog days* are the complete pre-origin days with
the same calendar type, within ±14 days of the same day of year, in the same daylight-saving state, and preceded by a
complete 744-hour window. Up to eight are kept: those closest in daily-mean temperature to the frozen climatology of
day $d$ (ties: the more recent). Candidates come from the whole pre-origin record, not only from the 1,344-hour context.
With $\mathcal A_d$ the kept analog days, $\bar x_j$ the mean of day $j$, $s_j$ the standard deviation of the 744 hours
before day $j$ and $s_o$ that of the 744 hours before the origin (each floored at $\max(0.01|\text{mean}|, 10^{-3})$ kW),

$$S_{d,h}=\frac{s_o}{|\mathcal A_d|}\sum_{j\in\mathcal A_d}\frac{x_{j,h}-\bar x_j}{s_j}.$$

Each analog day's shape is thus rescaled from the variability before it to the variability before the origin. A day with fewer than four analogs keeps $w^T_d$. If $\max|S|$ exceeds three times the largest
absolute context value the whole window keeps $w^T$ (a guard against scale floors on near-constant records).

**Anchoring.** For the lead blocks $k$ = days 1–7, 8–14, 15–21, 22–31,

$$w_{d,h}=w^T_{d,h}+\omega_k\,(S_{d,h}-w^T_{d,h}),\qquad
\omega_k=\min\Big(\mathrm{clip}(\hat\lambda_k,0,1)\,\frac{n}{n+2},\ \tfrac12\Big),$$

$$\hat\lambda_k=\frac{\sum_q\langle S_q-w^T_q,\ y_q-w^T_q\rangle_k}{\sum_q\Vert S_q-w^T_q\Vert_k^2},$$

estimated over the unit's $n\le3$ completed pseudo-origin windows $q=o-744k'$, $k'=1,2,3$, where $S_q$ is the analog
shape built from data before $q$, $w^T_q$ the foundation shape issued at $q$ and $y_q$ the realised within-day block.
The weight is a least-squares weight on the disagreement between the two shapes, shrunk towards the foundation model
(zero) and capped at one half. No pseudo-origin, or no disagreement, gives $\omega_k=0$ and the 1.x forecast.

- Both $w^T$ and $S$ have zero daily means, so the pre-projection daily means are unchanged by the anchoring, and with
  them the level, the daily path, the energy readout ($744\times$ level) and any readout computed from those daily means.
  The delivered trajectory $\max(F,0)$ can differ where the projection binds, and so can a readout computed from it: the
  study's peak readout and `examples/quickstart.py` use the delivered trajectory.
- The three pseudo-origin forecasts are among the six that ANKYRA already computes for the handover: no further
  foundation-model call is needed.
- The analog shape needs a previous year at the same dates. Records shorter than about 13 months give no analogs and
  the block stays the foundation model's.
- The rule was selected, from a family written down in advance, on three development populations and on the
  pre-cutoff windows of the six test cohorts; its evaluation is described in
  [EVALUATION.md](EVALUATION.md#within-day-anchoring-20).

**History-only configuration.** `forecast(..., foundation=None)` returns the history side alone: the six-candidate
level and the daily path, with the same-day-type within-day default (eight most recent days of each type), no model
candidate and no handover. It is a reduced configuration for ablation and for offline use without a foundation model.
It was not part of the benchmark. The off-state and micro-load rules return the foundation model's forecast, so they
do not apply in this configuration.

Code: `ankyra/analog.py` (`AnalogShapes`, `within_trust`, `anchored_within_day`), `ankyra/core.py` (`forecast`).

## Week-by-week handover

At the origin, let $m^H_d$ be the history-side daily means (the level including the model candidate, plus the daily
path) and $m^T_d$ those of TimesFM. For the weeks $w$ = days 1–7, 8–14, 15–21 and 22–31,

$$m_d=(1-\alpha_w)\,m^H_d+\alpha_w\,m^T_d,\qquad
\alpha_w=\frac{n\hat\lambda_w+K_0/2}{n+K_0},\quad K_0=2 .$$

$\hat\lambda_w$ is the least-squares combination weight, clipped to $[0,1]$:

$$\hat\lambda_w=\mathrm{clip}\Big(\frac{\sum_k\langle y_k-m^{H0}_k,\,m^T_k-m^{H0}_k\rangle_w}{\sum_k\Vert m^T_k-m^{H0}_k\Vert_w^2},\,0,\,1\Big).$$

It is estimated from the $n\le6$ completed pseudo-origin pairs of the unit, where:

- $y_k$ is the realised daily means;
- $m^T_k$ is TimesFM's daily means issued at pseudo-origin $k$;
- $m^{H0}_k$ is the **fixed division's** daily means: the six-candidate level plus the daily path, *without* the model
  candidate.

The weight is a least-squares weight rather than an inverse-MSE weight. Errors shared by the two sources pull
inverse-MSE weights towards 1/2, whereas least squares depends only on where the sources differ (P10 in
[theory/PROOFS.md](../theory/PROOFS.md)).

The weights are estimated on the fixed division and applied to $m^H$, which includes the model candidate. Using the
fixed division at the pseudo-origins avoids nested pseudo-origins. If no pair or no disagreement is available,
$\alpha_w=1/2$.

An ablation fixed before it was run shows that one weight per unit for the whole month is as accurate as the four
weekly weights ([EVALUATION.md](EVALUATION.md#what-the-handover-contributes)). The weekly form is kept as evaluated.

The forecast is $F_{d,h}=m_d+w_{d,h}$, projected onto $F\ge0$. It needs seven TimesFM calls per window (one at the
origin, six at pseudo-origins).

Code: `ankyra/core.py` (`lead_week_weights`, `lead_week_transition`, `forecast`).

## Off-state and micro-load rules

Two rules return the TimesFM forecast unchanged. Both look only at load before the origin.

**Off-state rule.** If the last 168 hours before the origin are all at most $10^{-6}$ kW, the TimesFM forecast is
returned.

- The rule adds no new constant.
- It follows from a measured property of the load: a departure from normal operation is more likely to continue the
  longer it has lasted ([evidence](EVALUATION.md#departures-from-normal-operation-persist)).
- Without it, the shrinkage of the weights keeps the historical level in play for a meter that is off.

**Micro-load rule (2.0.1).** If all 1,344 hours of the context are within $10^{-3}$ kW of zero
($\max|{\rm load}|\le10^{-3}$ kW), the TimesFM forecast is returned.

- The threshold reuses the value of the floor of the normalisation scale $s_0$ (see [Level](#level)); it is not a new
  constant. A record that stays inside that floor for eight weeks is treated as switched off, like a record that reads
  zero. The off-state rule does not catch it, because its readings are small but not zero.
- **What it corrects.** On the meters that prompted it the context read 0.0002–0.0005 kW, yet 2.0.0 forecast 0.35 kW on
  average: the historical candidates still carried the load of earlier months, and the shrinkage of the weights kept
  them in play, as for a meter that is off.
- **What it does not do.** It is a sufficient condition chosen after that failure was seen, not a derived boundary. A
  record slightly above the threshold is not covered, although its scale may also be at the floor. The rule cannot
  foresee a restart: in 5 of the 46 windows it changes, the meter resumed during the forecast month, and there 2.0.0
  was marginally better.
- The condition uses the whole context, so a unit with ordinary load anywhere in its last eight weeks is not affected.
  The context must be completely observed. A return under the micro-load rule alone runs the estimator's history,
  category and temperature-scale checks; a return under the off-state rule does not, as in 2.0.0.
- The threshold is an absolute value in kW, like the off-state threshold and the scale floor, and is compared in double
  precision. Loads must be supplied in kW; rescaling a record across the threshold changes which branch is taken.
- **Where it acts.** On the ten scored populations the rule changes 46 windows of nine meters at one BDG2 site (13
  before and 33 after the training cutoff of the trained baselines). On EWELD every micro-load window is already an
  off-state window, and no window of the other eight populations qualifies.
- **Status.** The rule was written after the BDG2 test result of 2.0.0 had been seen, in response to it. Its effect on
  BDG2 describes what the rule changes; it is not a test of the rule. The 2.0.0 results are kept beside the 2.0.1
  results ([EVALUATION.md](EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)).

On off-state and micro-load windows the returned trajectory is the foundation model's, without the projection onto
nonnegative load that the other windows receive.

Code: `ankyra/core.py` (`ZERO_KW`, `MICRO_KW`, `forecast`). The output fields `off_state` and `micro_load` report which
rule fired. They are not a certificate that the inputs were validated: the off-state return checks only the shape of
the foundation forecast. What the implementation's checks can and cannot establish about the inputs is stated in
[Information at the origin](#information-at-the-origin).

## Readouts

**Energy.** Window energy is $744\,\ell$ kWh for loads in kW, read before the projection.

- The projection $\max(F,0)$ cannot increase any hour's absolute error when the truth is nonnegative.
- It raises delivered energy by $\sum\max(-F,0)$, which is known at the origin.
- No map can simultaneously keep the energy readout, return nonnegative load and guarantee no increase in error.

**Peak.** Let $\hat L_d$ be the forecast mean of day $d$, $\tau_d$ its day type and $\bar F$ the forecast window
mean. Let $a_j=\max_h x_{j,h}-\bar x_j$ be the excursion of context day $j$ above its own mean ($x_{j,h}$ is the load
of hour $h$ of that day), and $A_t$ the largest excursion among the four most recent context days of type $t$. Then

$$U=\max_d\,(\hat L_d+A_{\tau_d}),\qquad \hat P_\kappa=\bar F+\kappa\,(U-\bar F)\quad(\kappa=1).$$

This operator has four properties:

1. **Motivation.** For exact conditional means, $\max_{d,h}\mathbb E[y_{d,h}]\le\mathbb E[\max_{d,h}y_{d,h}]$.
   Fitted forecasters are median-type summaries, so this motivates the operator rather than guaranteeing it.
2. **Scalar form.** Because maxima commute, $U$ equals the hour-wise envelope $\max_{d,h}(\hat L_d+\max_j a_{j,h})$.
   Also $U\ge\max_d\hat L_d\ge\bar F$.
3. **Median property.** Suppose daily levels are constant within type, excursions are drawn independently from each
   selected sample, and a type attaining the envelope has $m$ samples and $n$ future days with $((m-1)/m)^n<1/2$. Then
   the median of the future maximum equals $U$ exactly. Four samples and three repetitions suffice.
4. **Error decomposition.** With $M$ the realised peak of the window and $d^\ast$ the day on which it occurs,
   $U-M=\ell(e)+[b_{d^\ast}(F)-b_{d^\ast}(y)]+[A_{\tau_{d^\ast}}-a_{d^\ast}(y)]+\Delta_{\rm sel}$ with $\Delta_{\rm sel}\ge0$.
   Level and daily-path gains therefore carry into the peak.

**Interval.** Hourly residuals of historical pseudo-forecasts at up to 12 completed pseudo-origins are normalised by
each pseudo-window's origin scale and pooled by hour of day and workday status. Their empirical quantiles are added to
the forecast and scaled by the origin's scale.

Proofs, counterexamples and an optional day-level projection are P11–P18 in [theory/PROOFS.md](../theory/PROOFS.md).

Code: `ankyra/readouts.py`; the properties as operators: `theory/operators.py`.

## Output fields

`ankyra.forecast` returns an `AnkyraForecast`. All loads are in kW.

| Field | Meaning |
|---|---|
| `trajectory_kw` | the 744 delivered hourly values; nonnegative, except on off-state and micro-load windows, where the foundation model's trajectory is returned as it is |
| `level_kw` | the window mean before the projection onto nonnegative load |
| `energy_kwh` | the energy readout, $744\times$ `level_kw` |
| `daily_means_kw` | the 31 daily means after the week-by-week handover |
| `within_day_kw` | the final within-day block (zero mean on each day), with the analog-day anchoring where it acts |
| `foundation_within_day_kw` | the foundation model's own within-day block, unmodified. On off-state and micro-load windows `within_day_kw` equals it |
| `analog_shape_kw` | the unit's analog-day shape $S$ (a day with fewer than four analogs carries the foundation shape); `None` when it was not built |
| `within_trust` | the four weights $\omega_k$ on the analog-day shape, for days 1–7, 8–14, 15–21, 22–31 |
| `within_pseudo_pairs` | the number of completed pseudo-origin windows behind `within_trust` (at most 3) |
| `analog_kept` | `False` when the whole-window guard rejected the analog shape and the window keeps the foundation shape |
| `lead_week_weights` | the four handover weights $\alpha_w$ on the foundation model's daily means |
| `pseudo_pairs` | the number of completed pseudo-origin pairs behind `lead_week_weights` (at most 6) |
| `level_weights` | the weight of each level candidate (keys below) |
| `fixed_division_daily_means_kw` | the daily means of the fixed division: the six-candidate level plus the daily path, without the model candidate and without the handover |
| `off_state`, `micro_load` | which of the two rules returned the foundation model's forecast, if any |

On off-state and micro-load windows the weights, counts and `fixed_division_daily_means_kw` keep their empty
defaults, because the estimator is not run.

**Keys of `level_weights`.** The first letter is the window of the mean, the second says whether it is
weather-adjusted (`u` unadjusted, `w` weather-adjusted).

| Key | Level candidate |
|---|---|
| `s_u`, `s_w` | the recent 7-day mean (short window) |
| `l_u`, `l_w` | the long-history mean over at most 8,760 hours |
| `a_u`, `a_w` | the mean of the 744-hour window one year earlier (annual) |
| `fm` | the foundation model's own window mean |

The weights sum to one. A candidate with fewer than two pseudo-origin errors has weight zero, unless no candidate
has two; then the weights are equal.

**Keys of the daily-path weights.** The seven [daily-path candidates](#centred-daily-path) are weighted inside the
historical estimator. `AnkyraForecast` does not carry their weights;
`ankyra.history.estimate_from_history(...).diagnostics["day_weights"]` does, with `diagnostics["level_weights"]` for
the six historical level candidates before the model candidate is added.

| Key | Daily-path candidate |
|---|---|
| `cur` | the path implied by the level construction: the 8-week day-type offsets plus the weather-response path times the level's total weather weight |
| `c_w8`, `c_w4`, `c_w2` | day-type offsets from the last 8, 4 and 2 weeks |
| `c_ann_type` | day-type offsets of the annual window |
| `p_ann_cal` | the annual window's daily means in date order |
| `g_w` | the weather-response path |

**What `examples/quickstart.py` prints.**

| Printed key | Field or computation |
|---|---|
| `foundation_model` | which forecaster filled the foundation-model slot |
| `off_state`, `micro_load`, `energy_kwh`, `level_kw`, `level_weights` | the fields above |
| `peak_kw` | `ankyra.readouts.peak_readout` applied to the trajectory and the context |
| `interval_80pct_first_hour_kw` | the 10% and 90% bounds of the interval readout for the first forecast hour (`ankyra.readouts.residual_quantiles`, `interval_bands`) |
| `interval_pseudo_windows` | the number of completed pseudo-origin windows whose residuals the interval uses (at most 12) |
| `lead_week_weights_on_model` | `lead_week_weights` |
| `pseudo_origin_pairs` | `pseudo_pairs` |
| `within_day_trust_on_analog_shape` | `within_trust` |
| `within_day_pseudo_origin_triples` | `within_pseudo_pairs` |
| `analog_shape_kept` | `analog_kept` |
| `trajectory_first_day_kw` | the first 24 values of `trajectory_kw` |

Code: `ankyra/core.py` (`AnkyraForecast`), `ankyra/history/api.py` (`Estimate`).

## Constants

| Constant | Value | Where it was fixed |
|---|---|---|
| Context / horizon | 1,344 h / 744 h | before any evaluation |
| Pseudo-origins (history / model) | 12 / 6 | development data: household aggregates / the Spanish development store ([defined in EVALUATION.md](EVALUATION.md#populations-and-tiers)) |
| $K_0$ level, daily path, handover | 8, 2, 2 | development data; never changed afterwards |
| Within-day anchoring (2.0): pseudo-origins, shrinkage, cap | 3, $K_0=2$ towards 0, $\omega\le1/2$ | in the candidate family written down before the 2.0 rule was chosen; selected on the development populations and the pre-cutoff test windows |
| Analog days: window, kept, required, guard | ±14 days of year, 8, 4, $3\times\max\lvert\text{context}\rvert$ | with the first version of the analog-day shape; never changed |
| Off-state threshold | $10^{-6}$ kW | the pre-existing zero-load threshold |
| Micro-load threshold (2.0.1) | $10^{-3}$ kW on the magnitude of the load, over the 1,344-hour context | the pre-existing floor of the normalisation scale; the rule was added after the BDG2 test result of 2.0.0 had been seen |
| Peak envelope | 4 most recent same-type days, $\kappa=1$ | in the earlier version of this model ([theory/PROOFS.md](../theory/PROOFS.md#peak), evidence under P18) |
| Temperature standardisation; signature hinges | $(T-15\,^\circ\mathrm{C})/10\,^\circ\mathrm{C}$; every 5 °C from −10 °C to 40 °C | in the frozen configuration, with the signature prior (`ankyra/history/frozen_config.json`) |
