# Data: sources and preparation

This page says where the eleven populations of the main evaluation and the two populations of the frozen-model
checks (HKUST, Helsinki) come from and how the study prepared them. It is written for
a reader who wants to rebuild the evaluation inputs from the public sources.

## What is and is not in this repository

- **In the repository:** the forecaster ([`ankyra/`](../ankyra)), the scoring code ([`evaluation/`](../evaluation)),
  the scored results ([`results/`](../results)), the figures, and one example window from the University of
  Cambridge estate archive (CC BY 4.0).
- **Not in the repository:** raw data, prepared data stores and model weights. None of them is redistributed. Follow
  each provider's access route and terms.
- **Foundation models.** The study used local snapshots with verified hashes:
  - TimesFM 2.5 200M (Apache-2.0), revision `1d952420fba87f3c6dee4f240de0f1a0fbc790e3`;
  - Chronos-2 (`amazon/chronos-2`, Apache-2.0), revision `29ec3766d36d6f73f0696f85560a422f50e8498c`.
- **Sources.** The references and DOIs are those of
  [EVALUATION.md](EVALUATION.md#populations-and-tiers). Archive identifiers, file sizes and hashes below are the ones
  the study recorded when it obtained the files. Where the study recorded none, this page says so.

Where the study's working notes do not hold a fact, the entry reads "not recorded here; see the provider". Nothing on
this page is a guess. The working notes and preparation scripts themselves are not part of this repository.

## The input format the forecaster expects

Every population was brought to one format, the `History` record of [`ankyra/history`](../ankyra/history), plus three
arguments of `ankyra.forecast`.

| Input | Content |
|---|---|
| `load_kw` | Hourly load in kW, from the record anchor up to the origin. The last 1,344 hours must be completely observed. Earlier gaps are allowed as NaN; they remove support for candidates and pseudo-origins. |
| `observed` | Optional boolean mask of the load, same length. `False` marks an hour as unobserved even if a value is present; an hour marked `True` must hold a finite value. Default: every finite hour is observed. |
| `temperature_c` | Hourly outdoor temperature in °C, same length as the load, finite everywhere. Nothing after the origin. |
| `day_types` | One integer per hour for the history plus the 744 forecast hours: Monday = 0 … Sunday = 6, public holiday = 7. Constant within each calendar day of the grid. |
| `start_timestamp` | The record anchor: an ISO timestamp on 1 January 00:00 with a `+00:00` offset. Index 0 of every array is this hour. |
| `group` | One of Industrial, Office, Public, Residential, Commercial. It selects the fixed temperature-signature prior. Commercial has no prior and gives a zero temperature signature ([METHOD.md](METHOD.md#the-category-commercial-has-no-prior)). |
| `temp_sigma_std` | One positive scalar per population: the standard deviation of the daily-mean temperature about its 31-day moving mean, in units of 10 °C (0.25 means 2.5 °C). The weather-adjusted candidates take their expectation over an anomaly of this size. Fitted on temperature recorded before the first origin and then kept fixed. The recipe is given below. |
| `dst_region` | "EU", "US" or "none": the daylight-saving rule used only to match analog days. |

The first five rows are fields of `History`; the last three are arguments of `ankyra.forecast`.

**How the study computed `temp_sigma_std`.**

1. Standardise the temperature as (T − 15 °C) / 10 °C.
2. Take daily means.
3. Subtract a centred 31-day moving mean. What remains is the daily temperature anomaly.
4. `temp_sigma_std` is the standard deviation of that anomaly, pooled over the units of the population, on the first
   244 days of the record (15 days are dropped at each end, where the centred mean is incomplete).

The value is therefore in units of 10 °C. It is fitted once, before the first origin, and kept fixed. The package
does not compute it and checks only that it is a finite positive number. The values used for the eleven populations
are not listed in this repository.

Points that matter when rebuilding:

- **Loads must be in kW.** The off-state and micro-load thresholds are absolute values in kW. An energy reading in
  kWh per hour equals the mean kW of that hour; Wh per hour is divided by 1,000; four 15-minute kWh values are summed.
- **No hidden time handling.** The forecaster does no resampling, no interpolation and no daylight-saving conversion.
  The grid must be a regular hourly grid before it is passed in.
- **The anchor is a label on a fixed grid.** For several populations the study placed the data on the provider's
  fixed-offset local grid (for example UTC+1 for Norway) and gave that grid to the forecaster with a `+00:00` anchor.
  Day types then follow the local calendar. The entries below state the grid of each population.
- **The 1 January anchor fixes the phase of the annual temperature harmonic.** A record that starts later in the year
  is padded back to 1 January with unobserved load (NaN), not shifted.
- **Day types** are the weekday of the grid's calendar date, replaced by 7 on a public holiday of the population's
  country.

## Common window rules

- **Origins.** The first hour of each calendar month and the hour before it. When a population was thinned, only the
  month-start origins were kept.
- **Complete window.** A window needs a completely observed 1,344-hour context and 744-hour target.
- **Minimum history at the source.** The source preparations required 10,248 hours (8,760 + 2 × 744) before the
  origin, so that two annual pseudo-errors are possible. For Oslo, Cambridge, HEEW, CINELDI, BDG2, the Suzhou park
  and LCL this is counted from the unit's first observation. For Drammen and the GoiEner households it is counted
  from the start of the time axis, so some household units have less than 10,248 hours of their own record
  ([history length](EVALUATION.md#history-length)). For EWELD and GoiEner non-household the counting rule is not
  recorded here.
- **Six pseudo-origins.** The evaluation panel keeps a window only if the load is complete from six monthly steps
  before the context to the origin (at least 5,808 hours).
- **Thinning.** Panels are capped at 1,500 windows per population by a fixed rule: month-start origins only, then
  every *k*-th window per unit in origin order, with *k* = ⌈N / cap⌉; if one window per unit is still too many, every
  *m*-th unit in sorted order.
- **Masking.** Hours that a provider imputed, replaced or zero-filled are set to missing where the provider documents
  it or where the stated rule below detects it. A masked hour makes its window ineligible; it is never filled.
- **Late windows.** Trained baselines are fitted on targets that end before a cutoff and scored on origins after it.
  The cutoff is the first day of the month that contains the population's median evaluation origin.

| Population | Training cutoff of the trained baselines |
|---|---|
| BDG2 2017 | 2017-08-01 |
| Cambridge | 2013-07-01 |
| HEEW Arizona | 2018-12-01 |
| EWELD | 2019-08-01 |
| GoiEner non-household | 2019-05-01 |
| GoiEner households | 2019-07-01 |
| Oslo | 2019-10-01 |
| Drammen | 2020-09-01 |
| CINELDI | 2021-02-01 |
| Suzhou park | 2018-09-01 |
| LCL households | 2013-09-01 |

Unit and window counts (all / late) are in the table of
[EVALUATION.md](EVALUATION.md#populations-and-tiers).

## The populations

### 1. BDG2 2017 (building meters, USA / Europe)

- **Source.** Miller et al., *Sci. Data* 2020, [doi:10.1038/s41597-020-00712-x](https://doi.org/10.1038/s41597-020-00712-x).
  Archive identifier, version, file size and hash: not recorded here; see the provider.
- **Record used.** Hourly electricity meters, 2016–2017, anchor 2016-01-01. Two building pools prepared earlier in the
  study, disjoint from each other, were joined.
- **Windows.** Month-start origins in 2017 that satisfy the common rules. Windows with a missing target hour were
  excluded.
- **Load column and unit conversion, temperature source, time zone handling, holiday calendar, category mapping,
  daylight-saving region:** not recorded here; see the provider.
- **Caveats.**
  - Seven BDG2 sites (Bear, Bull, Cockatoo, Fox, Hog, Panther, Rat) are listed in a public pretraining corpus of the
    foundation models. Unlisted does not mean unseen.
  - The signature prior of the forecaster was fitted once on BDG2 windows ending before July 2016.
  - Nine meters at one site read 0.0002–0.0005 kW for months
    ([details](EVALUATION.md#the-near-zero-meters-and-the-micro-load-rule-201)). They are kept as released.
  - 13 units carry the category Commercial, for which the forecaster has no signature prior and uses a zero
    temperature signature ([METHOD.md](METHOD.md#the-category-commercial-has-no-prior)).

### 2. University of Cambridge estate (UK)

- **Source.** Langtry & Choudhary 2024, [doi:10.5281/zenodo.10955332](https://doi.org/10.5281/zenodo.10955332)
  (CC BY 4.0). Version 2.0 of the archive. File size and hash: not recorded here.
- **Load.** The processed per-building electricity files, one per year, column `equipment load [kWh]`, hourly. kWh per
  hour is used as kW. Years up to 2022.
- **Masking.** The provider writes missing readings as zeros. Runs of three or more consecutive zero hours are treated
  as missing; single and double zero hours are kept. This is a heuristic. The provider clips values at ten times the
  mean.
- **Temperature.** The Met Office weather files shipped in the archive (Bedford, `air_temperature [degC]`,
  2000–2022). One series for all buildings. Gaps are linearly interpolated.
- **Grid.** UTC, as in the files; anchor 2000-01-01.
- **Holidays.** England and Wales bank holidays 2000–2023, computed from the Easter rule, the fixed dates and the
  documented substitutions and one-off holidays.
- **Category.** Public for every building.
- **Daylight-saving region.** EU.
- **Windows.** Origins from April 2001; 119 buildings and 1,456 windows in the panel, 202 target months.

### 3. HEEW, Arizona State University (USA)

- **Source.** Dong et al., *Sci. Data* 2025, [doi:10.1038/s41597-025-06010-8](https://doi.org/10.1038/s41597-025-06010-8).
  Data archive: figshare 10.6084/m9.figshare.28425647, version 1 (CC BY 4.0), file `HEEW-20250912.zip`, MD5
  `b3ad8aa2ba8c40d74f001d483963cea9`. 147 buildings, hourly, 2014–2022.
- **Load.** Column `Electricity` of the raw per-building files, kWh per hour used as kW, gross of PV.
- **Masking.** The archive has a raw and a cleaned file for each building. An hour is missing if the raw value is
  empty or below −0.01, if the cleaned value is −1 or not a number, or if raw and cleaned differ by more than 10⁻³
  (the provider replaced or imputed it). Then runs of three or more zero hours are treated as missing, as for
  Cambridge.
- **Temperature.** Column `Temperature` of the archive's cleaned weather file. The values are converted from °F to °C
  if their median exceeds 45. Gaps are linearly interpolated. One series for all buildings.
- **Grid.** The provider's local clock, fixed at UTC−7 (Arizona has no daylight-saving time); anchor 2014-01-01,
  labelled `+00:00` for the forecaster.
- **Holidays.** US federal holidays with the observed-day rules; Juneteenth from 2021.
- **Category.** Public for every building.
- **Daylight-saving region.** none.
- **Windows.** Origins from March 2015; 142 buildings and 1,282 windows scored, 73 target months (April 2015 to
  December 2022).
- **Caveat.** The first build labelled the anchor with a −07:00 offset, which the forecaster rejects. The build was
  repeated with the `+00:00` label before any window was scored. The data themselves were not changed.

### 4. EWELD (industrial and commercial meters, China)

- **Source.** Liu et al., *Sci. Data* 2023, [doi:10.1038/s41597-023-02503-6](https://doi.org/10.1038/s41597-023-02503-6).
  Data archive: Figshare 21893808, version 3; 258,090,540 bytes; MD5 `eea1455aff6518aae1fbfc397b178111`. 386 meters
  in three anonymised cities (12 / 372 / 2).
- **Load.** 15-minute kWh. Hourly kW is the sum of the four quarter-hour values; an hour with a missing quarter is
  missing.
- **Masking.** Runs of at least eight identical positive quarter-hour values (0.4% of values) are masked as fill
  traces. Runs of zeros (13% of values) are kept as data: a shutdown and a filled gap cannot be told apart.
- **Temperature.** The archive's weather file of the meter's city (15-minute, °F), converted to °C and averaged to
  hours. Gaps are linearly interpolated.
- **Grid.** Hourly, assumed UTC+8 with no daylight-saving time. The source does not document the time zone; the
  assumption was checked against the pooled weekday profile. Anchor 2016-01-01.
- **Holidays.** Chinese statutory holidays 2016–2022, transcribed from the State Council notices. Make-up workdays
  were transcribed with them.
- **Category.** By ISIC section letter: A, C, D, E, F, H → Industrial (266 meters); G, J, K, L, M, N → Office (85);
  I, O, P, Q, S → Public (35).
- **Daylight-saving region.** none.
- **Windows.** Origins from April 2017. The main population is the second city (350 meters). The panel has 274 meters
  and 1,023 windows.
- **Caveat.** Many contexts are entirely zero. Windows whose target is entirely zero are kept.

### 5. GoiEner non-household supply points (Spain)

- **Source.** Quesada et al., *Sci. Data* 2024, [doi:10.1038/s41597-023-02846-0](https://doi.org/10.1038/s41597-023-02846-0).
  Archive identifier, version, file size and hash: not recorded here; see the provider.
- **Units.** Category-labelled supply points, not certified individual buildings: 486 units (Industrial 159,
  Office 80, Public 247). They are disjoint from the supply points of the Spanish development store: a separate set
  of GoiEner non-household supply points on which the method was developed. That store is not one of the eleven
  populations and is not scored in any table.
- **Grid.** Anchor 2018-01-01.
- **Daylight-saving region.** EU.
- **Load column and unit conversion, temperature source, holiday calendar, the rule that assigns the categories:**
  not recorded here; see the provider.
- **Caveats.**
  - The preparation kept the provider's documented treatment of the clock-change hours. Its details are not recorded
    here.
  - Origins at 23:00 and 00:00 of the same month boundary have targets that overlap for 743 hours. The panel keeps
    month-start origins only.
  - Many units have short histories; the annual candidate is then not available.

### 6. GoiEner households (Spain)

- **Source.** As for population 5.
- **Units.** A store of 6,226 households on a time axis from 2018-01-01 to 2020-01-31, with 24 origins in 2019. It was
  thinned to month-start origins and every sixth window per household, then to the panel's 1,109 households and 1,258
  windows.
- **Minimum history.** The origin must lie at least 10,248 hours after the start of the time axis. This is not counted
  from the household's first reading.
- **Category.** Residential.
- **Grid.** Anchor 2018-01-01.
- **Daylight-saving region.** EU.
- **Load column and unit conversion, temperature source, holiday calendar:** not recorded here; see the provider.
- **Caveat.** The clock-change treatment is that of population 5.

### 7. COFACTOR-SBHUB Oslo schools (Norway)

- **Source.** Lien et al., *Data in Brief* 2025, [doi:10.1016/j.dib.2025.112288](https://doi.org/10.1016/j.dib.2025.112288).
  Data obtained from data.sintef.no ([doi:10.60609/czgf-5e46](https://doi.org/10.60609/czgf-5e46), CC BY 4.0);
  111,225,480 bytes (the byte count matched the portal's). Hash: not recorded here.
- **Load.** 48 school files in the same format as Drammen. Column `ElImp` (Wh per hour) divided by 1,000.
- **Temperature.** Column `Tout` of each file. Before a building's first row, the hourly mean of the other buildings
  is used; all are in Oslo.
- **Grid.** The provider's fixed UTC+1 grid; anchor 2012-01-01. Records start between October 2012 and January 2021
  and end between December 2013 and August 2024.
- **Holidays.** Norwegian statutory holidays 2012–2025, computed from the Easter rule (12 days a year).
- **Category.** Public for every school.
- **Daylight-saving region.** EU.
- **Windows.** Origins from April 2013. Each building needs 10,248 hours of its own record before the origin.
  45 schools are eligible.

### 8. COFACTOR Drammen municipal buildings (Norway)

- **Source.** Lien et al., *Sci. Data* 2025, [doi:10.1038/s41597-025-04708-3](https://doi.org/10.1038/s41597-025-04708-3).
  Data archive: Zenodo record 14752397, version 3; 22,417,463 bytes; MD5 `13640361f6fcb2bf428dfad3cfa60888`.
  45 building files.
- **Load.** Column `ElImp` (Wh per hour) divided by 1,000. Gaps stay missing.
- **Temperature.** Column `Tout` of each file (a reanalysis temperature). Gaps are linearly interpolated within each
  building.
- **Grid.** The provider's fixed UTC+1 grid, timestamps labelling the start of the hour; anchor 2018-01-01. Rows with
  another offset, off the hour or duplicated are dropped.
- **Holidays.** Norwegian statutory holidays 2018–2022 (12 days a year; 24 and 31 December are not labelled).
- **Category.** 20 kindergartens, 16 schools and 7 nursing homes → Public; 2 offices → Office.
- **Daylight-saving region.** EU.
- **Windows.** 70 origins from April 2019; 35 target months.

### 9. CINELDI industrial customers (Norway)

- **Source.** Sandell et al., *Data in Brief* 2023, [doi:10.1016/j.dib.2023.109121](https://doi.org/10.1016/j.dib.2023.109121).
  Data archive: Zenodo record 10361330, version 2.3. File size and hash: not recorded here.
- **Load.** 45 customer files with rows `Bus_ID;Timestamp;Load_kWh`, hourly, 1 March 2019 to 17 March 2022. kWh per
  hour is used as kW.
- **Grid.** The files use the local wall clock, with a repeated hour in autumn and a missing hour in spring. The
  stamps are placed on a fixed UTC+1 grid: duplicates are averaged and the missing hour stays missing.
- **Temperature.** The record has none. The study uses the city-mean outdoor temperature of the Oslo school data
  (population 7) as a proxy: the same climate region, about 90 km away.
- **Holidays.** Norwegian statutory holidays, as for Oslo.
- **Category.** The record has no customer categories. Every customer is set to Industrial, after the title of the
  record.
- **Daylight-saving region.** EU.
- **Windows.** Origins from May 2020; 45 customers, 929 windows, 22 target months.
- **Caveats.** The temperature is a proxy and the category is assumed. Both are stated as limitations in
  [EVALUATION.md](EVALUATION.md#limitations).

### 10. Suzhou industrial park (China)

- **Source.** Zhou et al., *Sci. Data* 2023, [doi:10.1038/s41597-023-02786-9](https://doi.org/10.1038/s41597-023-02786-9).
  Archive identifier, version, file size and hash: not recorded here; see the provider.
- **Units.** Four category aggregates, 2016–2019; anchor 2016-01-01.
- **Daylight-saving region.** none.
- **Load column and unit conversion, how the aggregates were formed, temperature source, holiday calendar:** not
  recorded here; see the provider.
- **Caveats.**
  - An earlier preparation had errors in the timing and filling of the weather series. It was corrected and the
    affected results were rebuilt. Results from before and after the correction are not interchangeable.
  - With four series, only point estimates should be read.
  - One of the four series carries the category Commercial and is forecast with a zero temperature signature
    ([METHOD.md](METHOD.md#the-category-commercial-has-no-prior)).

### 11. Low Carbon London households (UK)

- **Source.** UK Power Networks,
  [London Datastore](https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d).
  File names, sizes and hashes: not recorded here; see the provider.
- **Record used.** Households from 23 November 2011 to 28 February 2014.
- **Padding.** The forecaster needs a 1 January anchor, so the record is padded back to 2011-01-01 (7,824 hours).
  In the padded segment the load is unobserved (NaN) and the temperature is a fixed 15 °C. An earlier preparation
  copied the temperature of the same hours one year later into the padding; the final evaluation does not.
- **Temperature-anomaly scale.** Fitted on the earliest 244 days of the record, which end before the earliest
  pseudo-origin ([recipe](#the-input-format-the-forecaster-expects)).
- **Windows.** Month-start origins under the common rules: 1,215 windows of 965 households; 710 late windows.
- **Daylight-saving region.** EU.
- **Load column and the conversion from the provider's readings to hourly kW, temperature source, time zone handling,
  holiday calendar, the category label:** not recorded here; see the provider.
- **Caveat.** LCL was held out of the ten-population comparison and scored once with the frozen 2.0.1 forecaster.
  ANKYRA 2.1 was re-scored on it afterwards, as a re-evaluation.
  Its 1.x result had been seen earlier, so it is not an unexposed population
  ([LCL evaluation](LCL_AND_CLOSEOUT.md#lcl-final-stage)).

## Populations scored with the forecaster frozen

These two populations were prepared after ANKYRA 2.0.1 was fixed. No rule or constant of the forecaster was chosen on
them. ANKYRA 2.1 was adopted after they had been scored; its numbers on them are re-evaluations
([FROZEN_MODEL_CHECKS.md](FROZEN_MODEL_CHECKS.md)). Results: [FROZEN_MODEL_CHECKS.md](FROZEN_MODEL_CHECKS.md).

### 12. HKUST campus incomer meters (Hong Kong)

- **Source.** Li, Wang, Qu, Chui and Leung-Shea, *Sci. Data* 11, 1284 (2024); Dryad
  [doi:10.5061/dryad.k3j9kd5h6](https://doi.org/10.5061/dryad.k3j9kd5h6), file `All_Data.zip` (1.43 GB), "Clean" data.
- **Units.** The building incomer meters named in the dataset's Brick metadata (type `ACB_Incomer`); parallel incomers
  of one entity are summed. 33 units, 134 windows (30 units with nonzero load).
- **Load.** The clean files hold a cumulative reading. Hourly energy is the sum of the differences inside the hour (kWh
  per hour = mean kW); an hour is missing when a needed reading is missing or a difference is negative. Many meters are
  quantised at 10 or 100 kWh.
- **Grid.** Fixed UTC+8 (no daylight saving), anchor 2022-01-01. `dst_region` none.
- **Temperature.** ERA5 2 m temperature at the campus through the Open-Meteo archive interface.
- **Day types.** Hong Kong general holidays as gazetted by the HKSAR Government = 7.
- **Windows.** Month-start origins with the common rules (six pseudo-origins, complete context and target).
- **Temperature-anomaly scale.** Fitted on the 243 complete days before the first origin (it had first been fitted on
  the first 244 days, which included 24 hours after the origin of four windows; every HKUST forecast was recomputed,
  [details](FROZEN_MODEL_CHECKS.md#a-population-never-used-before)).

### 13. Helsinki city service buildings (Finland)

- **Source.** City of Helsinki, Urban Environment Division: energy consumption of the city's service properties, Nuuka
  Open API (`helsinki-openapi.nuuka.cloud`, no authentication), published 2020-04-16. Licence listed as CC BY 4.0 in the
  Helsinki Region Infoshare and national open-data catalogues. Pulled 2026-10-05; the pull is not redistributed.
- **Sample.** 300 property codes drawn by SHA-256 of the code from the city's property list (647 codes), after
  excluding three properties looked at before the protocol was frozen; 285 electricity series, 201 with at least one
  complete window, 1,168 windows.
- **Load.** kWh per hour as returned (= mean kW). Exact duplicates removed; conflicting values and negative values
  would be set missing (none occurred).
- **Grid.** The provider's local wall clock (Europe/Helsinki) is moved to a fixed UTC+2 grid, anchor 2023-01-01:
  summer-time records shift by one hour; the autumn repeated hour, which the provider reports as one record holding
  two hours, is split evenly over the two grid hours and flagged (flagged hours are left out of hourly scoring and kept
  in energy). `dst_region` EU.
- **Temperature.** ERA5 2 m temperature at 60.17 N, 24.94 E through the Open-Meteo archive interface.
- **Day types.** Paid public holidays listed by the University of Helsinki Almanac Office, plus Midsummer Day, Midsummer
  Eve and Christmas Eve = 7.
- **Windows.** Eleven month-start origins, 2025-11 to 2026-09, after the public release of both foundation models;
  common window rules; no thinning.

## What cannot be rebuilt from this page

- **GoiEner (both populations), BDG2, the Suzhou park and LCL.** The archive version, the load column, the unit
  conversion, the temperature source and the holiday calendar are not recorded here. For GoiEner and the park the
  rule that assigns or forms the categories is not recorded either.
- **Unit and window lists.** The exact units and origins of each panel are not published. The rules above reproduce
  the selection only if the same archive version and the same unit order are used.
- **The temperature-anomaly scale.** The recipe for `temp_sigma_std` is given
  [above](#the-input-format-the-forecaster-expects), but its value is not listed per population. The study's working
  notes say that the preparation scripts for two sources contain a path that fills temperature gaps from the full
  record; whether it was triggered was not assessed.
- **File hashes.** Hashes are recorded for Drammen, EWELD and HEEW only.
- **Licences of the sources** (checked on the providers' pages on 5 October 2026): CC BY 4.0 for BDG2 (Zenodo
  10.5281/zenodo.3887306), the Cambridge estate archive, HEEW, EWELD (figshare 10.6084/m9.figshare.21893808.v3),
  GoiEner (Zenodo 10.5281/zenodo.7362094 and 10.5281/zenodo.7859413), COFACTOR Drammen (Zenodo
  10.5281/zenodo.14752397), COFACTOR-SBHUB Oslo (data.sintef.no, 10.60609/czgf-5e46), CINELDI (Zenodo
  10.5281/zenodo.10361330) and the Suzhou park (OSF 10.17605/OSF.IO/AGK8S);
  "Creative Commons Attribution" (version not given on the page) for LCL on the London Datastore; CC0 for HKUST
  (Dryad). The Helsinki data are listed as CC BY 4.0 in the national catalogues, but the provider's pages could not be
  opened from the study's network, so that licence is not confirmed. The repository redistributes no raw data except the Cambridge example
  window (CC BY 4.0, attributed in `results/example_window_cambridge.json`); `results/bdg2_micro_load_windows.csv`
  names BDG2 meters with monthly means and maxima (CC BY 4.0, Miller et al. 2020).
- **Provider-side processing.** A complete, finite prepared series does not show that every value is a direct
  physical observation. Gap filling by the provider, later quality control of weather archives and the pretraining
  corpora of the foundation models lie outside what this page documents
  ([METHOD.md](METHOD.md#information-at-the-origin)).
- **The Spanish development store.** A separate set of GoiEner non-household supply points, disjoint from
  population 5, on which the method was developed. It is not one of the eleven populations, it is not scored in any
  table, and its units and preparation are not described here.
- **Prepared stores and forecasts.** The prepared arrays, the foundation-model forecasts and the trained baselines'
  checkpoints are not distributed. The scored statistics are in [`results/`](../results).
