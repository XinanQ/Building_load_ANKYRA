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

## Estimands

**Unit-equal log RMS ratio (primary).** For unit $i$, $R_i$ is the RMS of its hourly errors over its windows, and
$r=N^{-1}\sum_i\log(R_i^{A}/R_i^{B})$. It is reported as the improvement $100[1-\exp(r)]$; positive favours ANKYRA.

**Intervals.** 95% intervals come from 2,000 bootstrap replicates that resample units and target-midpoint months
independently (UM). A contrast is *resolved* when its interval excludes zero.

**Mean per-unit rank.** Models are ranked within each unit by RMSE, with ties averaged. This summary stays defined
where some units have exactly zero error.

**Conventional metrics.** RMSE and MAE (unit mean, kW); CV(RMSE), NMBE and WAPE (unit median, %). See
[`results/conventional_metrics.csv`](../results/conventional_metrics.csv).

## Results

### Test populations (late windows, 21 forecasters)

| | BDG2 | Cambridge | HEEW | EWELD | GoiEner NH | GoiEner HH |
|---|---:|---:|---:|---:|---:|---:|
| ANKYRA mean per-unit rank | **4.9** | 5.6 | **5.1** | **6.5** | **6.2** | 7.3 |
| ANKYRA position | 1 | 2 | 1 | 1 | 1 | 2 |
| vs TiDE | +13.6 * | +16.3 * | +18.9 * | +33.1 * | +13.8 * | +14.7 * |
| vs iTransformer-X | +3.5 | −1.5 | +5.3 * | +20.3 * | +5.8 | +12.0 * |
| vs GBT-T | +10.6 * | +2.6 | +2.7 | +99.8 * | +67.7 * | +26.0 * |
| vs Chronos-2-X | −39.6 † | −0.4 | +1.0 | +14.2 * | −2.5 | +0.3 |
| vs TimesFM-X | +5.6 | +7.1 * | +4.9 | +16.3 * | +4.6 * | +2.9 |
| vs TimesFM (load only) | −54.8 † | +5.6 * | +2.8 | +2.1 | +1.7 | −3.8 (+) |

\* resolved in ANKYRA's favour; (+) resolved against ANKYRA.

† BDG2 unit means are pulled by three meters reading about 0.0002 kW. Against all nine models of Figure 3 the median unit
favours ANKYRA (59–92% of units).

Mean per-unit rank averaged over the six test populations:

| Forecaster | Mean rank |
|---|---:|
| **ANKYRA** | **5.94** |
| per-unit ridge | 7.21 |
| Chronos-2-X | 7.72 |
| iTransformer-X | 8.06 |
| TimesFM | 8.34 |
| TimesFM-X | 8.48 |

### Preview and reserved populations

- **Oslo:** GBT-T (−18.0%) and iTransformer-X (−9.2%) are resolvably better than ANKYRA. ANKYRA ranks 6th of 21 in
  the late windows.
- **Drammen:** several trained models have small unresolved leads (7th of 21).
- **CINELDI:** 3rd of 21.
- **Suzhou park:** 1st of 21.
- **LCL** (load-only comparison): 3rd of 14.

Across all ten scored populations ANKYRA's mean rank is 5.85, ahead of the per-unit ridge (6.83), iTransformer-X (6.99)
and Chronos-2-X (7.50).

**Full windows.** The comparison without the trained models covers 14 forecasters on all 11 populations:

- ANKYRA ranks first on seven;
- its mean rank is 3.09, against 3.88 for the ridge and 4.11 for Chronos-2-X;
- no contrast is resolved against it.

### Why ANKYRA loses on Norwegian schools

The deficit is in the within-day block and falls on specific days. ANKYRA's within-day error is higher than GBT-T's
by:

| Day type (Oslo) | ANKYRA's within-day error vs GBT-T |
|---|---:|
| ordinary working days | +22% |
| closure-like working days | +40% |
| public holidays | +54% |
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
  See [`results/intervals_households.json`](../results/intervals_households.json).

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

[`results/REPRODUCTION_CHECK.json`](../results/REPRODUCTION_CHECK.json) records four comparisons of this package with
the evaluated forecasts, run where the data are available. All match exactly (maximum absolute difference 0.0 kW):

- ANKYRA forecasts on 613 windows of two populations, including every off-state window;
- the TimesFM adapter on 64 Drammen windows;
- the peak operator on 200 Cambridge windows;
- the within-day default on the same 200 Cambridge windows;
- the household intervals: bands on all 4,770 windows, and residual quantiles recomputed from the store on 12 windows.
