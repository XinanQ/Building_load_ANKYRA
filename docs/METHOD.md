# Method

## Information at the origin

A forecast at origin $o$ is a function of the following, and nothing else:

- load and temperature at hours $t<o$;
- the calendar type (weekday or public holiday) of the 31 forecast days;
- the unit's category, which selects a fixed temperature-signature prior. The prior was fitted once on BDG2 windows
  ending before July 2016 and is never refitted;
- a fixed temperature-anomaly scale set before the first origin;
- the foundation model's forecasts from the 1,344 hours before $o$ and before each pseudo-origin $o-744k$.

Weights are estimated at pseudo-origins inside the record.

- Every pseudo-target ends by $o$.
- Each level pseudo-forecast at $o-744k$ uses only data before $o-744k$.
- The weekly handover uses the realised daily means of these pseudo-targets.

One exception concerns only the pre-origin record. One daily-path candidate, the path implied by the level
construction, reuses the weather weight estimated at the origin. Its pseudo-errors are therefore not strictly out of
sample with respect to that weight, although all of them precede the origin.

Two fixed components come from outside the unit's record: the pretrained foundation model and the signature prior.
Neither sees the unit's future. Both may, however, reflect data recorded later than the oldest evaluation windows, for
example the London households of 2011–2014.

[`tests/test_no_future_information.py`](../tests/test_no_future_information.py) changes every value after the origin,
or after each pseudo-origin, and checks that the forecast, the model's inputs, the pseudo-origin errors and the interval
are unchanged.

These tests establish input isolation in the implementation. They do not show that the inputs themselves carry no
later information. Three things lie upstream of the implementation: the providers' gap filling (imputed or zero-filled
hours are masked where documented), later quality control of weather archives, and the pretraining corpora.

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
in [THEORY.md](THEORY.md).

Code: `ankyra/blocks.py`, `ankyra/operators.py`.

## Level

Load is normalised by the mean $l_0$ and standard deviation $s_0$ of the 744 hours before the origin, with $s_0$
floored at $\max(0.01|l_0|,10^{-3})$ kW.

**Six historical candidates.** Each of three means comes with and without weather adjustment:

- the recent 7-day mean;
- the long-history mean over at most 8,760 hours;
- the mean of the 744-hour window one year earlier.

Unadjusted candidates add a day-type offset estimated from the last eight weeks. Adjusted candidates replace the
temperature response of their own window by the expected response over the target days. The response is a convex
piecewise-linear signature, and the expectation uses a pre-origin climatology with a fixed anomaly scale. No observed
future weather is used.

**Foundation-model candidate.** One further candidate, TimesFM's own window mean, is origin-normalised with the
calendar offset removed. The implementation is six historical candidates plus this one. Earlier project documents
call it the "eighth candidate", because number seven had been given to a switched-off extension that is not part of
ANKYRA.

**Weights.** Each candidate's window-mean error is computed at up to $K=12$ earlier pseudo-origins $o-744k$ ($k\le6$ for
the model candidate, from forecasts issued at those origins). With $s_j$ the RMS of at least two such errors,

$$\widetilde w_j=\frac{I_j/\max(s_j,10^{-6})^2}{\sum_r I_r/\max(s_r,10^{-6})^2},\qquad
w_j=\frac{K_{\rm eff}\,\widetilde w_j+K_0\,w_{0j}}{K_{\rm eff}+K_0},\quad K_0=8,$$

where $w_0$ is uniform over the supported candidates and $K_{\rm eff}$ counts pseudo-origins with complete evidence.

- With complete records $K_{\rm eff}(m)=\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$ for a history of $m$ hours.
- Below two errors the weights are equal.
- The annual candidate needs 10,248 hours (about 14 months) before it can be weighted.
- In the historical estimator, with matched support and no candidate deleted at the origin, the shrinkage keeps the
  total weather weight within $[(1-\rho)/2,(1+\rho)/2]$, $\rho=K_{\rm eff}/(K_{\rm eff}+8)$. With the model candidate
  the prior weather mass is 3/7 once all seven candidates are supported, and the general bound of P8 applies.

These support and shrinkage properties are P7–P9 in [THEORY.md](THEORY.md).

Code: `ankyra/history/` (frozen reference estimator), `ankyra/core.py` (`level_with_model_candidate`).

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

The within-day block is the day-demeaned TimesFM 2.5 point forecast from the same 1,344 hours of load. No covariates
or fine-tuning are used.

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
[THEORY.md](THEORY.md)).

The weights are estimated on the fixed division and applied to $m^H$, which includes the model candidate. Using the
fixed division at the pseudo-origins avoids nested pseudo-origins. If no pair or no disagreement is available,
$\alpha_w=1/2$.

An ablation fixed before it was run shows that one weight per unit for the whole month is as accurate as the four weekly weights ([EVALUATION.md](EVALUATION.md#what-the-handover-contributes)). The weekly form is kept as evaluated.

The forecast is $F_{d,h}=m_d+w_{d,h}$, projected onto $F\ge0$. It needs seven TimesFM calls per window (one at the
origin, six at pseudo-origins).

Code: `ankyra/core.py` (`lead_week_weights`, `lead_week_transition`, `forecast`).

## Off-state rule

If the last 168 hours before the origin are all at most $10^{-6}$ kW, the TimesFM forecast is returned unchanged.

- The rule adds no new constant.
- It follows from a measured property of the load: a departure from normal operation is more likely to continue the
  longer it has lasted ([evidence](EVALUATION.md#departures-from-normal-operation-persist)).
- Without it, the shrinkage of the weights keeps the historical level in play for a meter that is off.

## Readouts

**Energy.** Window energy is $744\,\ell$ kWh for loads in kW, read before the projection.

- The projection $\max(F,0)$ cannot increase any hour's absolute error when the truth is nonnegative.
- It raises delivered energy by $\sum\max(-F,0)$, which is known at the origin.
- No map can simultaneously keep the energy readout, return nonnegative load and guarantee no increase in error.

**Peak.** Let $a_j=\max_h x_{j,h}-\bar x_j$ be the excursion of context day $j$ above its own mean, and $A_t$ the
largest excursion among the four most recent context days of type $t$. Then

$$U=\max_d\,(\hat L_d+A_{\tau_d}),\qquad \hat P_\kappa=\bar F+\kappa\,(U-\bar F)\quad(\kappa=1).$$

This operator has four properties:

1. **Motivation.** For exact conditional means, $\max_{d,h}\mathbb E[y_{d,h}]\le\mathbb E[\max_{d,h}y_{d,h}]$.
   Fitted forecasters are median-type summaries, so this motivates the operator rather than guaranteeing it.
2. **Scalar form.** Because maxima commute, $U$ equals the hour-wise envelope $\max_{d,h}(\hat L_d+\max_j a_{j,h})$.
   Also $U\ge\max_d\hat L_d\ge\bar F$.
3. **Median property.** Suppose daily levels are constant within type, excursions are drawn independently from each
   selected sample, and a type attaining the envelope has $m$ samples and $n$ future days with $((m-1)/m)^n<1/2$. Then
   the median of the future maximum equals $U$ exactly. Four samples and three repetitions suffice.
4. **Error decomposition.** With realised peak day $d^\ast$,
   $U-M=\ell(e)+[b_{d^\ast}(F)-b_{d^\ast}(y)]+[A_{\tau_{d^\ast}}-a_{d^\ast}(y)]+\Delta_{\rm sel}$ with $\Delta_{\rm sel}\ge0$.
   Level and daily-path gains therefore carry into the peak.

**Interval.** Hourly residuals of historical pseudo-forecasts at up to 12 completed pseudo-origins are normalised by
each pseudo-window's origin scale and pooled by hour of day and workday status. Their empirical quantiles are added to
the forecast and scaled by the origin's scale.

Proofs, counterexamples and an optional day-level projection are P11–P18 in [THEORY.md](THEORY.md).

Code: `ankyra/readouts.py`, `ankyra/operators.py`.

## Constants

| Constant | Value | Where it was fixed |
|---|---|---|
| Context / horizon | 1,344 h / 744 h | before any evaluation |
| Pseudo-origins (history / model) | 12 / 6 | household development aggregates / Spanish development store |
| $K_0$ level, daily path, handover | 8, 2, 2 | development data; never changed afterwards |
| Off-state threshold | $10^{-6}$ kW | the pre-existing zero-load threshold |
| Peak envelope | 4 most recent same-type days, $\kappa=1$ | earlier peak-operator study |
