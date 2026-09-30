# Evaluation

All numbers below are in [`results/`](../results). The figures are regenerated from those files by
`figures/make_figures.py`.

## Populations and tiers

| Population | Country | Units / windows (all / late) | Tier | ANKYRA design status | Source |
|---|---|---|---|---|---|
| BDG2 2017, building meters | USA / Europe | 178 / 934 · 142 / 474 | test | seen | Miller et al., *Sci. Data* 2020, [doi:10.1038/s41597-020-00712-x](https://doi.org/10.1038/s41597-020-00712-x) |
| University of Cambridge estate | UK | 119 / 1,456 · 108 / 730 | test | first read | Langtry & Choudhary 2024, [doi:10.5281/zenodo.10955332](https://doi.org/10.5281/zenodo.10955332) (CC BY 4.0) |
| HEEW, Arizona State University | USA | 142 / 1,282 · 138 / 658 | test | first read | Dong et al., *Sci. Data* 2025, [doi:10.1038/s41597-025-06010-8](https://doi.org/10.1038/s41597-025-06010-8) |
| EWELD industrial and commercial meters | China | 274 / 1,023 · 197 / 523 | test | seen | Liu et al., *Sci. Data* 2023, [doi:10.1038/s41597-023-02503-6](https://doi.org/10.1038/s41597-023-02503-6) |
| GoiEner non-household supply points | Spain | 486 / 1,237 · 481 / 890 | test | seen | Quesada et al., *Sci. Data* 2024, [doi:10.1038/s41597-023-02846-0](https://doi.org/10.1038/s41597-023-02846-0) |
| GoiEner households | Spain | 1,109 / 1,258 · 696 / 696 | test | seen | as above |
| COFACTOR-SBHUB Oslo schools | Norway | 45 / 1,147 · 41 / 581 | preview | seen | Lien et al., *Data in Brief* 2025, [doi:10.1016/j.dib.2025.112288](https://doi.org/10.1016/j.dib.2025.112288) |
| COFACTOR Drammen municipal buildings | Norway | 45 / 1,375 · 43 / 689 | preview | seen | Lien et al., *Sci. Data* 2025, [doi:10.1038/s41597-025-04708-3](https://doi.org/10.1038/s41597-025-04708-3) |
| CINELDI industrial customers | Norway | 45 / 929 · 45 / 475 | preview | first read | Sandell et al., *Data in Brief* 2023, [doi:10.1016/j.dib.2023.109121](https://doi.org/10.1016/j.dib.2023.109121) |
| Suzhou industrial park (4 category aggregates) | China | 4 / 127 · 4 / 64 | preview | seen | Zhou et al., *Sci. Data* 2023, [doi:10.1038/s41597-023-02786-9](https://doi.org/10.1038/s41597-023-02786-9) |
| Low Carbon London households | UK | 965 / 1,215 · 710 / 710 | reserved | seen | UK Power Networks, [London Datastore](https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d) |

**Design status.**

- **Seen:** results for the population were known when some ANKYRA component was specified.
  - The annual candidate followed a diagnosis on the Suzhou park.
  - The foundation-model candidate and the handover were developed on the Spanish development store (not listed).
  - The off-state rule followed the EWELD and household results.
- **First read:** the population was scored for the first time after the handover had been fixed.

**Tiers of the equal-information comparison.** ANKYRA was fixed first. The covariate-informed baselines were then
generated for every population and scored in two steps:

1. a preview on four populations, used for diagnosis;
2. after all model development had ended, one scoring of the six test populations.

LCL was held in reserve. Between the two steps, four versions of a within-day extension were developed on the
development store and the preview populations. None passed its no-harm criterion, so the test populations were never
used for development. ANKYRA's univariate comparisons on the test populations had been scored before the covariate
baselines.

A window needs a completely observed 1,344-hour context and 744-hour target, and enough history for six pseudo-origins.
Panels are capped at 1,500 windows per population by a fixed thinning rule. Data are used as released by the
providers, with documented masking of imputed or zero-filled hours. The raw data are not redistributed here; follow
each provider's access route and terms.

## Baselines

| Information | Forecasters |
|---|---|
| Given ANKYRA's information set: 11 past, 10 future, 6 static features, no future observed weather; each model uses the part its architecture accepts | TiDE (all inputs), iTransformer-X (no future covariates), GBT-T (21 derived features), trained per population; Chronos-2-X (no static features), TimesFM-X (covariates through linear XReg), zero-shot |
| Load only, foundation models | TimesFM 2.5, Chronos-2 (zero-shot) |
| Load only, trained per population | DLinear, PatchTST, iTransformer, LSTM |
| Load only, statistical | Holt–Winters (damped, additive, period 168 h), MSTL (24 h and 168 h) |
| Calendar and climatological temperature | per-unit ridge regression refitted at every origin |
| Simple | previous-month, 4-week and last-year profiles; seasonal naive (day, week); a zero-shot gradient-boosting model |

The shared feature set is:

- load;
- temperature (climatology in the horizon);
- the load one year earlier (lag 8,736 h, always before the origin) with its availability mask;
- sines and cosines of hour, weekday and day of year;
- a non-working-day flag;
- the category (one-hot);
- the log ratio of the long-history to the recent mean.

PatchTST is channel-independent, so its load forecast is the same function with or without these channels.

**Training protocol for the trained models.**

- The cutoff is the first day of each population's median origin month.
- All training targets end before the cutoff.
- The learning rate is chosen from {1e-4, 3e-4, 1e-3} on the last 20% of training origins; at most 15 epochs with
  patience 3.
- Predictions are averaged over three seeds.
- Trained models are scored on origins after the cutoff (the *late* windows), on the same windows as every other model.
- Leakage checks (feature time indices, lag indices, normalisation statistics, training-target end) are implemented as
  assertions.

**No information after the origin, on either side.**

- **ANKYRA** uses only pre-origin load and temperature, the forecast month's calendar and a pre-origin temperature
  expectation ([METHOD.md](METHOD.md#information-at-the-origin)). Tests change every value after the origin and check
  that nothing moves. This establishes input isolation in the implementation, not the absence of later information in
  the providers' data preparation, the weather archives or the pretraining corpora.
- **Covariate-informed baselines** receive the same set:
  - future temperature enters as the same climatological expectation, never as observed weather;
  - the one-year load lag always precedes the origin.
- **Trained baselines** are fitted on targets that end before a cutoff and are scored only after it.
- **Test populations** were scored once, after all development had ended.
- **Pretraining corpora** of the foundation models are the one exposure no forecaster controls (see
  [Limitations](#limitations)).

### Correction of the GBT-T baseline

GBT-T is our own implementation: scikit-learn's histogram gradient boosting on 21 features from the shared set, trained
across the units of each population. Its first version normalised every window by the window's own context mean and
standard deviation, with a floor of max(1% of the mean, 10⁻³ kW). On flat or all-zero contexts the floor produced
training targets 10⁵–10⁷ times too large, and the trees then forecast loads up to 18,500,000 kW on EWELD, whose largest
observed load is 13,427 kW. This affected 96% of EWELD's late windows, 12% on GoiEner non-household, 7% on BDG2 and 1%
on households.

The defect was found after the test populations had been scored. Two corrections were written before each was run:

- The first replaced the window scale by each unit's pre-cutoff scale everywhere. It removed the failure but also
  weakened GBT-T where it had worked, for example on Cambridge, HEEW and Oslo.
- The second, reported here, keeps the original scaling and uses the unit's pre-cutoff standard deviation only where
  the floor was active.

GBT-T was therefore scored three times on the test populations; ANKYRA and the other 19 forecasters once. On EWELD the
per-window scaling still overshoots in 41% of windows. There the contexts are almost entirely zero with isolated spikes,
so read GBT-T's EWELD result as a limit of that design, not as an advantage of ANKYRA. The Norwegian diagnostics below
were recomputed with the corrected GBT-T.

## Estimands

**Unit-equal log RMS ratio (primary).** For unit $i$, $R_i$ is the RMS of its hourly errors over its windows, and
$r=N^{-1}\sum_i\log(R_i^{A}/R_i^{B})$. It is reported as the improvement $100[1-\exp(r)]$; positive favours ANKYRA.

**Intervals.** 95% intervals come from 2,000 bootstrap replicates that resample units and target-midpoint months
independently (UM). A contrast is *resolved* when its interval excludes zero.

**Mean per-unit rank.** Models are ranked within each unit by RMSE, with ties averaged. This summary stays defined
where some units have exactly zero error.

**Conventional metrics.** RMSE and MAE (unit mean, kW); CV(RMSE), NMBE and WAPE (unit median, %); WAPE also pooled.
See [`results/conventional_metrics.csv`](../results/conventional_metrics.csv) for the full windows and
[`results/conventional_metrics_late.csv`](../results/conventional_metrics_late.csv) for the late windows, where all 21
forecasters are available.

**Why four summaries.** Pooled and unit-equal summaries can disagree in sign for an algebraic reason. The pooled MSE
ratio weights each unit's squared RMS ratio by its share of the reference error, and those weights are coupled to the
ratios (P19 in [theory/PROOFS.md](../theory/PROOFS.md)). No single summary is therefore reported alone.

## Results

### Test populations (late windows, 21 forecasters)

Primary estimand first: the unit-equal improvement $100[1-\exp(r)]$ in hourly RMS against each forecaster. The rank
rows at the bottom are a secondary summary.

| | BDG2 | Cambridge | HEEW | EWELD | GoiEner NH | GoiEner HH |
|---|---:|---:|---:|---:|---:|---:|
| vs TiDE | +13.6 * | +16.3 * | +18.9 * | +33.1 * | +13.8 * | +14.7 * |
| vs iTransformer-X | +3.5 | −1.5 | +5.3 * | +20.3 * | +5.8 | +12.0 * |
| vs GBT-T ‡ | +15.2 * | +2.6 | +5.6 * | +46.0 * | +29.6 * | +16.0 * |
| vs Chronos-2-X | −39.6 † | −0.4 | +1.0 | +14.2 * | −2.5 | +0.3 |
| vs TimesFM-X | +5.6 | +7.1 * | +4.9 | +16.3 * | +4.6 * | +2.9 |
| vs TimesFM (load only) | −54.8 † | +5.6 * | +2.8 | +2.1 | +1.7 | −3.8 (+) |
| Resolved better than, of 20 | 10 | 16 | 16 | 18 | 15 | 16 |
| Resolved worse than, of 20 | 0 | 0 | 0 | 0 | 0 | 1 |
| ANKYRA mean per-unit rank | **5.0** | 5.6 | **5.1** | **6.7** | **6.4** | 7.3 |
| ANKYRA position | 1 | 2 | 1 | 1 | 1 | 2 |

\* resolved in ANKYRA's favour; (+) resolved against ANKYRA. ‡ Corrected implementation; see
[Correction of the GBT-T baseline](#correction-of-the-gbt-t-baseline).

† BDG2 unit means are dominated by three meters reading about 0.0002 kW. The full result is kept, and a sensitivity
analysis is reported beside it:

- without the three meters (11 of 474 windows), the improvement is +1.6% against TimesFM and −3.0% against Chronos-2-X;
- the intervals stay wide, because other low-load units also carry extreme ratios;
- ANKYRA's mean rank is 4.95 with the three meters and 4.73 without them, first either way;
- against all nine models of Figure 3, the median unit favours ANKYRA (58–92% of units).

The three meters are the BDG2 units whose largest hourly load over their panel windows is at most 0.001 kW
(Lamb_education_Harold, Lamb_education_Hillary, Lamb_office_Jo). Both versions of every comparison, full and late
windows, are in [`results/bdg2_near_zero_sensitivity.csv`](../results/bdg2_near_zero_sensitivity.csv).

Mean per-unit rank averaged over the six test populations:

| Forecaster | Mean rank |
|---|---:|
| **ANKYRA** | **6.00** |
| per-unit ridge | 7.25 |
| Chronos-2-X | 7.80 |
| iTransformer-X | 8.13 |
| TimesFM | 8.42 |
| TimesFM-X | 8.55 |

By position, ANKYRA is first or second on each of the six test populations. No other forecaster is in the top two on
more than two of them: the per-unit ridge ranges from first to fifth, Chronos-2-X to 11th, TimesFM to 12th and GBT-T to
18th (Figure 12).

![Position on every population](../figures/fig12_consistency.png)

### Preview and reserved populations

- **Oslo:** GBT-T (−18.0%) and iTransformer-X (−9.2%) are resolvably better than ANKYRA. ANKYRA ranks 5th of 21 in
  the late windows.
- **Drammen:** several trained models have small unresolved leads (7th of 21).
- **CINELDI:** 3rd of 21.
- **Suzhou park:** 1st of 21.
- **LCL** (load-only comparison): 3rd of 14.

Across all ten scored populations ANKYRA's mean rank is 5.88, ahead of the per-unit ridge (6.85), iTransformer-X (7.02)
and Chronos-2-X (7.54).

**Full windows.** The comparison without the trained models covers 14 forecasters on all 11 populations:

- ANKYRA ranks first on seven;
- its mean rank is 3.09, against 3.88 for the ridge and 4.11 for Chronos-2-X;
- no contrast is resolved against it.

### Loss metrics of every forecaster

![Loss metrics of all 21 forecasters](../figures/fig8_loss_metrics.png)

Figure 8 gives the conventional losses of all 21 forecasters on the same late windows, for the six test populations and
the Suzhou industrial park (a preview population with four aggregate series). The values were computed when the panel
was scored; the export reads them and recomputes nothing. RMSE and MAE are means over units in kW, so larger units weigh
more; CV(RMSE) and WAPE are taken at the median unit.

| ANKYRA's position among 21 | BDG2 | Cambridge | HEEW | EWELD | GoiEner NH | GoiEner HH | Suzhou park |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| RMSE (unit mean) | 1 | 2 | 2 | 2 | 3 | 2 | 1 |
| MAE (unit mean) | 1 | 3 | 2 | 3 | 4 | 5 | 1 |
| CV(RMSE) (median unit) | 3 | 2 | 1 | 2 | 2 | 2 | 2 |
| WAPE (median unit) | 2 | 2 | 2 | 2 | 4 | 5 | 2 |
| WAPE (pooled) | 2 | 3 | 3 | 3 | 4 | 5 | 1 |

- ANKYRA is between first and fifth on every metric and population, and first in 5 of the 28 cells of the figure. No
  baseline is lower on all of them.
- The forecasters lower than ANKYRA most often are Chronos-2-X (10 of the 28 cells), Chronos-2 (8), the per-unit ridge
  (6) and TimesFM (4).
- MAE and WAPE are minimised by the median of the predictive distribution, squared-error metrics by its mean. On MAE and
  WAPE, zero-shot Chronos-2 or TimesFM variants are lower than ANKYRA on EWELD and on both GoiEner populations.
- These metrics weight units differently from the unit-equal log ratio, which remains the primary estimand.
- GBT-T's EWELD errors remain the largest among the same-information models (unit-mean RMSE 153.9 kW, against 99.5
  for ANKYRA), because its per-window scaling still overshoots there (see the GBT-T correction below).

### Loss by forecast day

![Loss by forecast day](../figures/fig9_loss_by_day.png)

![Loss by forecast day relative to ANKYRA](../figures/fig10_loss_by_day_relative.png)

Figures 9 and 10 split the same late-window forecasts by forecast day. For unit $u$ and day $d$, $r_{u,d}$ is the RMSE
of that day's 24 hours over all the unit's windows and $\bar y_u$ the unit's mean load. The curves are geometric means of
$100\,r_{u,d}/\bar y_u$ over one fixed set of units whose daily errors are nonzero for all 21 forecasters: 132 of 142
units on BDG2, 108 of 108 on Cambridge, 133 of 138 on HEEW, 138 of 153 on EWELD, 453 of 477 on GoiEner non-household,
598 of 679 on households and all four Suzhou series. On this scale the ratio of two curves on day $d$ is the unit-equal
RMS ratio of the primary estimand restricted to that day.

The values come from the scored forecasts, and pooled over the month they give back the scored metrics and the primary
estimand exactly. The split was made after scoring; it is a description, and nothing was tuned on it.
[`results/lead_day_metrics.csv`](../results/lead_day_metrics.csv) also gives unit-mean RMSE and MAE in kW, and
median-unit CV(RMSE) and normalised MAE, for every day.

- **Position.** On every forecast day of every test population ANKYRA is among the six forecasters with the lowest
  loss of 21, and among the seven on the Suzhou park.
- **Growth with lead time.** From week 1 to week 4 ANKYRA's loss grows by ×1.19–1.57. That is less than TimesFM's
  (×1.24–1.68) and Chronos-2's (×1.25–1.80) on all seven populations.
- **The first day.** The zero-shot foundation models are lower on day 1 everywhere, and ANKYRA ranks third to fifth of 21.
- **From the second week.** On BDG2, Cambridge, HEEW and the Suzhou park ANKYRA is lowest or second-lowest on 13–16 of
  the 24 days from day 8. On EWELD it is on 5 of them.
- **GoiEner.** On the non-household set zero-shot TimesFM, Chronos-2 and Chronos-2-X are lower on every day; on
  households all four foundation-model variants are.

**Why the monthly comparison differs.** With $R_u$ the unit's RMS over the whole window, $R_u^2$ is the mean of its 31
daily MSEs. So $\log R_u$ is the mean of $\log r_{u,d}$ over the days plus $J_u\ge0$ (Jensen), and $J_u$ grows with how
uneven the unit's daily errors are. Averaged over units, the primary estimand splits exactly:

$$\frac1N\sum_u\log\frac{R_u^{A}}{R_u^{B}}=\frac1{31N}\sum_{u,d}\log\frac{r^{A}_{u,d}}{r^{B}_{u,d}}+\frac1N\sum_u\big(J^{A}_u-J^{B}_u\big).$$

The daily errors of TimesFM, Chronos-2 and Chronos-2-X are more uneven than ANKYRA's on all seven populations. Over the
month their larger-error days weigh more, so the monthly comparison moves towards ANKYRA. Against TiDE, iTransformer-X,
GBT-T and the per-unit ridge the unevenness runs the other way, except for GBT-T on EWELD.

| Fixed unit set, improvement $100[1-\exp(r)]$ | vs TimesFM: daily | month | vs Chronos-2: daily | month | vs Chronos-2-X: daily | month |
|---|---:|---:|---:|---:|---:|---:|
| BDG2 | +2.0 | +4.9 | +3.4 | +9.3 | −3.3 | +0.5 |
| Cambridge | +4.0 | +5.6 | +5.5 | +7.2 | −0.5 | −0.4 |
| HEEW | +1.1 | +2.9 | +3.7 | +5.6 | −0.7 | 0.0 |
| EWELD | −2.0 | +2.5 | −4.9 | +0.3 | −1.0 | +4.3 |
| GoiEner non-household | −2.9 | +1.8 | −8.7 | −0.5 | −11.2 | −3.2 |
| GoiEner households | −7.5 | −0.7 | −10.0 | −0.8 | −9.2 | −0.6 |
| Suzhou park | +5.2 | +7.3 | +16.9 | +19.9 | +8.7 | +12.1 |

"Daily" is the average of the daily log ratios, "month" the monthly log ratio on the same units; positive favours
ANKYRA. On all units the month column becomes the primary estimand of the test table. The fixed set leaves out units
whose error is exactly zero on some day for some forecaster: meters that are off, read near zero or hold a constant
value. On BDG2 these are 10 units, among them the three near-zero meters. On EWELD they are 59: 44 with a mean load below
10⁻⁶ kW and 15 that switch off on some days. There the month column differs from the primary estimand on all units.

### Monthly energy error

![Monthly energy error against every baseline](../figures/fig11_energy_error.png)

A month's energy error is $744\,\ell(e)$ kWh, 744 times the level error (P3). ANKYRA's design acts on this quantity:
its level and daily path come from the unit's own history, and its within-day shape is TimesFM's. On the same late
windows, Figure 11 compares the monthly energy error of ANKYRA with that of each of the 20 baselines. The estimand is the
unit-equal RMS ratio of the primary estimand applied to the level error, with the same unit-and-month bootstrap
intervals. It was computed after scoring and is a description, not a planned test
([`results/energy_error.csv`](../results/energy_error.csv), which also gives the median-unit absolute percentage energy
error of every forecaster).

- **No resolved deficit.** On all seven populations ANKYRA is never resolvably worse than any of the 20 baselines. It is
  resolvably better than 17 of them on GoiEner non-household, 14 on Cambridge and EWELD, 12 on households, 9 on HEEW,
  6 on the Suzhou park and 4 on BDG2.
- **Where the hourly view favours the foundation models.** On GoiEner households ANKYRA's monthly energy error is 22–27%
  lower than that of TimesFM, Chronos-2, Chronos-2-X and TimesFM-X, each resolved; on GoiEner non-household it is 18–25%
  lower, resolved against three of them. The within-day shape, where the foundation models are as good or better, carries
  most of these populations' hourly error (about 80% at the median unit), and energy is the part that ANKYRA changes.
- **Against TimesFM**, whose within-day shape ANKYRA uses, the energy error is 4–25% lower on six populations, resolved
  on Cambridge and both GoiEner sets.
- **BDG2.** The unit means are dominated by the three near-zero meters. The comparisons with the three zero-shot
  foundation models, MSTL and the previous-month profile are negative and unresolved. Without the three meters every
  point estimate favours ANKYRA, and five are resolved.
- **Small unresolved deficits** remain against the per-unit ridge and three profile or naive models on households (3–6%),
  iTransformer-X on Cambridge (4%) and TimesFM-X on the Suzhou park (4%).

### Why ANKYRA loses on Norwegian schools

The deficit is in the within-day block and falls on specific days. ANKYRA's within-day error is higher than GBT-T's
by:

| Day type (Oslo) | ANKYRA's within-day error vs GBT-T |
|---|---:|
| ordinary working days | +22% |
| closure-like working days | +42% |
| public holidays | +53% |
| weekends | level |

Closure-like days are calendar working days whose load fell below half of the recent working-day level. They are
identified from the load itself, not from operating calendars. The gap grows with the forecast week.

- **The shape is unlikely to be the main cause.** An oracle rescales each day's TimesFM shape by its best factor, using
  the realised data. It closes the gap to GBT-T on Oslo (+2.0%, unresolved).
- **A constant amplitude error is not the cause either.** A constant per-unit factor recovers under 2%.
- **This is consistent with a missing day-level activity signal.** In Oslo and Drammen, closure-like days are shared
  across units: when a unit has one, 7–14 times more other units have one on the same date than usual. They also
  recur: a unit with one on a date a year earlier has one again with probability 23–31%.

Cross-unit models trained with calendar features and the one-year lag can learn such regularities. A unit's own history
combined with a foundation model that sees eight weeks cannot.

The oracle bound and the correlations narrow the cause down but do not identify it. A free per-day factor can also
absorb other errors, and the operating reasons behind the closure-like days are unknown.

### A condition-matched extension that was not adopted

Condition-matched analog days from the unit's own history (same day type, same season, same daylight-saving state,
similar temperature) are the most informative pre-origin source of day-level activity in every population. On
holidays they are informative everywhere.

Four versions supplying this information to ANKYRA were tested against a fixed no-harm criterion on the development
store (within-day upper interval bound ≤ +0.01):

| Version | What the analog days supply | Development-store result |
|---|---|---|
| 1 | full 24-hour shape (±45 days) | revised before scoring |
| 2 | full 24-hour shape | 13.6% worse |
| 3 | one absolute amplitude factor per day | +0.001 [−0.005, +0.016] |
| 4 | one relative activity factor per day | +0.004 [−0.000, +0.012] |

- None passed, so none was tested or adopted.
- Holidays improved consistently (1.3–1.7%).
- The remaining harm sat on ordinary days of the Spanish population, whose departures are not predictable from any
  pre-origin source, and in strength estimates from only three pseudo-origins.

### What the handover contributes

An ablation specified before it was run varied only the weight on the model's daily means. It kept the candidates, the
within-day shape and the off-state rule fixed, and compared four weights:

- no weight (A0);
- a fixed half (A½);
- one weight per unit and month, estimated like the weekly ones (AM);
- ANKYRA's four weekly weights (AW).

LCL, the reserved set, was not used. The recomputed AW reproduces the evaluated ANKYRA forecasts to within 0.002 kW.

| Test population | A½ vs A0 | AW vs A½ | AW vs AM | Share of AW's gain captured by A½ |
|---|---:|---:|---:|---:|
| BDG2 2017 | +3.6 * | +2.0 | +0.4 | 0.64 |
| Cambridge | +0.1 | +1.2 * | −0.2 | 0.10 |
| HEEW Arizona | +3.7 * | +0.2 | +0.2 | 0.96 |
| EWELD | +3.3 * | +1.6 | −0.1 | 0.67 |
| GoiEner non-household | +1.8 * | +1.0 * | −0.2 (+) | 0.63 |
| GoiEner households | +2.2 * | +0.8 * | −0.1 | 0.74 |

Unit-equal improvement of the first arm; * resolved in its favour, (+) resolved against it.

- **Mixing.** Mixing in the model's daily means at a fixed half weight gives most of the gain on five test populations.
- **Per-unit weights.** Estimating the weight per unit adds 0.8–1.2%, resolved on three test populations.
- **Weekly weights.** Separate weekly weights add nothing over one weight per unit and month.
- **Preview populations.** On the four preview populations, where the fixed division is already strong, a fixed half
  weight lowers accuracy (unresolved). The per-unit weights reduce this loss.

The plan fixed the wording in advance: the claim is per-unit, error-weighted mixing, not weekly resolution. All ten
populations and the weekly breakdown are in [`results/handover_granularity.csv`](../results/handover_granularity.csv).

### Departures from normal operation persist

The weekly handover and the off-state rule rest on a measured property of the load rather than on tuned thresholds.
The analyses below are descriptive. They were specified in writing before they were run, and they read only stored
records and saved forecasts.

**Definition.** A day departs from normal operation when its mean falls outside hysteresis bands around a calendar
expectation. The expectation is the median of same-type days around the same date one year earlier. The four states
are off (below 5%), low (below 55%), high (above 150%) and normal. Recurring holidays and school breaks are part of the
expectation, so a departure is unscheduled by construction.

**Duration dependence.** The statistic compares exit rates in days 1–3 of a departure with days 8–30, within each unit
(Mantel–Haenszel log ratio). A value above zero means that a departure that has lasted longer is more likely to
continue.

| Population | Low | Off | High |
|---|---|---|---|
| Spanish development (4 categories) | 0.76–1.00 | 0.73–1.14 | 0.81–1.00 |
| EWELD (3 categories) | 0.65–0.79 | 0.82–1.01 | 0.77–1.02 |
| Drammen | 1.97 [1.57, 2.48] | — | 0.77 [0.62, 0.95] |
| Oslo | 1.12 [0.88, 1.36] | — | 0.85 [0.65, 1.06] |
| Cambridge | 0.75 [0.59, 0.91] | — | 1.05 [0.88, 1.21] |
| CINELDI | 0.92 [0.63, 1.20] | — | 0.94 [0.54, 1.32] |
| GoiEner households | 0.42 [0.37, 0.47] | 0.21 [−0.07, 0.42] | 0.67 [0.61, 0.73] |

- Pooled survival curves overstate duration dependence, because mixing units with different constant exit rates
  produces falling pooled rates. The within-unit ratios are 20–50% smaller than the pooled ones, but remain above zero.
- Gamma-frailty Weibull shapes are below one in most calendar-referenced cells (0.67–0.97; households 1.03–1.07).
- Out of time, a semi-Markov model beats a Markov model in 12 of 19 cells, with 5 favouring Markov and 2 ties.
- After temperature normalisation, the within-unit ratio stays above zero in 27 of 31 estimable cells.

**What this means for the forecast.** If departures were Markov, the value of the foundation model's recent
information would not depend on how long the current departure had lasted. It does.

- Windows whose departure had lasted at least 15 days at the origin favoured TimesFM over the fixed division more than
  windows with departures of at most 3 days.
  - Within units, excluding EWELD, the difference in ½ log MSE ratio was +0.28 [0.15, 0.42] in days 1–7 and
    +0.16 [0.05, 0.28] in days 15–31. This comparison was written after the pre-specified pooled one (+1.13 and
    +1.12), which EWELD shutdowns dominate.
  - Elapsed duration therefore marks the model's relative accuracy over the whole horizon, not a slower decay of it.
- ANKYRA uses this through its error weights, not through an explicit duration rule.
  - A rule that raised the model weight with elapsed duration (F1-τ) failed its fixed criterion.
  - It failed because the weights already move towards the model during long departures. On windows with departures
    of at least 15 days, the mean ½ log MSE ratio to TimesFM fell from F0 to F1 as follows: development 0.69 → 0.30,
    Cambridge 0.46 → 0.06, CINELDI 0.30 → 0.05.
- A zero week is the most persistent departure. 343 of 349 zero months in EWELD were preceded by one, and in that case
  the off-state rule hands the whole window to the model.

### Readouts

- **Peak operator:**
  - against the maximum of the same trajectory, 22–77% lower peak error on all 11 populations (all resolved);
  - against last month's observed peak, better on Drammen, Oslo and HEEW (12–16%) and worse on CINELDI (19%).
  See [`results/peak_readout.csv`](../results/peak_readout.csv).
- **Interval (GoiEner households):**
  - 79.2% coverage at nominal 80%;
  - Winkler score 4.3% better than the same interval around the fixed division and 7.5% better than TimesFM's native
    band (both resolved);
  - not distinguishable from Chronos-2's native quantiles.
  See [`results/intervals_households.json`](../results/intervals_households.json) and Figure 13.

![Prediction intervals on households](../figures/fig13_intervals.png)

## Cost

Timed on one machine: RTX 5060 Laptop GPU (8 GB), Ryzen 9 8940HX, 16 GB RAM. The sample is 64 Drammen windows; no
targets are used. Each value is the median of three timed repeats after a warm-up. CPU parts run on one thread.

| Per 744-hour window | First run | Pseudo-origins reused | Model load (once) | GPU memory |
|---|---:|---:|---:|---:|
| TimesFM alone, per-core batch 64 | 15 ms | — | 1.9 s | 3.0 GiB |
| TimesFM alone, study configuration (per-core batch 1) | 0.50 s | — | 1.9 s | 0.9 GiB |
| ANKYRA, batch 64 | 0.50 s | 0.11 s | 1.9 s | 3.0 GiB |
| ANKYRA, study configuration | 3.9 s | 0.60 s | 1.9 s | 0.9 GiB |
| Chronos-2-X | 55 ms | — | 7.3 s | 0.5 GiB |
| Per-unit ridge (CPU) | 97 ms | — | — | — |

ANKYRA's parts:

- reference estimator at the origin: 97 ms;
- six fixed-division pseudo-forecasts: 0.30 s;
- seven TimesFM contexts at batch 64: 0.10 s;
- peak readout: 34 µs;
- interval, when requested: 0.46 s.

The two TimesFM configurations give forecasts within 3×10⁻⁵ kW of each other.

"Pseudo-origins reused" assumes the six pseudo-origin forecasts come from earlier runs. This holds when forecasts are
issued every 744 hours, or when a window is re-run.

## Limitations

- **Pretraining exposure.** Most populations were public before TimesFM 2.5 and Chronos-2 were trained. Seven BDG2
  sites are in their pretraining corpora.
- **Design exposure.** Eight of the eleven populations were seen when some component was specified. The three
  first-read populations (Cambridge, CINELDI, HEEW) are the clean evidence for the handover.
- **Data.** Oslo temperature is used as a proxy for CINELDI. The Suzhou park has four aggregate series, so read its
  point estimates only.
- **Near-zero meters.** The off-state threshold misses near-zero but non-zero meters (three BDG2 meters).
- **Interval.** The interval was evaluated on households only.

## Reproduction record

[`results/REPRODUCTION_CHECK.json`](../results/REPRODUCTION_CHECK.json) records five comparisons of this package with
the evaluated forecasts, run where the data are available. All match exactly (maximum absolute difference 0.0 kW):

- ANKYRA forecasts on 613 windows of two populations, including every off-state window;
- the TimesFM adapter on 64 Drammen windows;
- the peak operator on 200 Cambridge windows;
- the within-day default on the same 200 Cambridge windows;
- the household intervals: bands on all 4,770 windows, and residual quantiles recomputed from the store on 12 windows.
