# Theory: the exact properties behind ANKYRA

[中文](README.zh-CN.md) · [Proofs](PROOFS.md) · [Operators](operators.py) · [Checks](test_operators.py) · [Back to the forecaster](../README.md)

This folder holds the mathematical contributions that sit beside the forecaster. The forecaster is the package
[`ankyra/`](../ankyra/), and nothing in it imports this folder. What is here explains and bounds its design:

- why a month-ahead forecast is split into a level, a daily path and a within-day shape;
- how much history the weights need, and how far they can move from equal;
- what the energy and peak readouts can and cannot guarantee;
- why the evaluation reports several estimands side by side.

Each property is supported in three ways:

| File | What it gives |
|---|---|
| [PROOFS.md](PROOFS.md) | statement, proof and the counterexamples that mark where it stops; where a study measured a consequence on data, that evidence |
| [operators.py](operators.py) | the property as a function that applies to any forecaster's 744-hour trajectory |
| [test_operators.py](test_operators.py) | a numerical check, counterexamples included (29 checks) |

```bash
python -m unittest discover -s theory -t .
```

![Exact properties on a test window](../figures/fig7_operators.png)

## The nineteen properties

Properties marked *standard* are known results that the design relies on; they are collected here, not claimed as new.
The others hold under the conditions in the third column. None is an accuracy guarantee: accuracy is measured in
[docs/EVALUATION.md](../docs/EVALUATION.md).

| | Property | Holds when | What ANKYRA uses it for | Code | Check |
|---|---|---|---|---|---|
| P1 | [Block identity](PROOFS.md#blocks) (standard) | always | assigning each block to a source | `ankyra.blocks.block_losses` | `BlockGeometryTests` |
| P2 | [Four blocks; no weekly Fourier bin](PROOFS.md#blocks) | always (744-hour window) | day types instead of a weekly component | `operators.four_block_losses` | `BlockGeometryTests` |
| P3 | [Energy is the level](PROOFS.md#blocks) | always | the energy readout | `ankyra.blocks.level` | `BlockGeometryTests` |
| P4 | [Exact replacement and the level-share bound](PROOFS.md#replacement) | fixed replacement estimates | scoring any division from block losses | `operators.replace_blocks` | `ReplacementTests` |
| P5 | [Two-source division: pooled optimum, unit-level asymmetry](PROOFS.md#replacement) | two sources, block-wise | why a fixed division is not enough | `operators.division_log_ratio` | `ReplacementTests` |
| P6 | [Correction accounting](PROOFS.md#replacement) (standard) | always | diagnosing a correction | `operators.correction_accounting` | `ReplacementTests` |
| P7 | [Completed error support](PROOFS.md#historical-weights) | complete records; missing hours only lower the count | how much history the weights need | `operators.completed_windows` | `SupportTests` |
| P8 | [Shrinkage bounds](PROOFS.md#historical-weights) | matched support, no deletion at the origin | how far the weights can move | `operators.mixture_mass_bounds` | `ShrinkageTests` |
| P9 | [Deletion renormalises the mixture](PROOFS.md#historical-weights) | always; a counterexample shows where P8 stops | when the bounds stop holding | `operators.retained_data_share` | `ShrinkageTests` |
| P10 | [Least squares versus inverse MSE under shared errors](PROOFS.md#historical-weights) | forecasts share an error component | the weekly handover weights | `operators.two_source_weights` | `ShrinkageTests` |
| P11 | [Clipping cannot increase any hour's error](PROOFS.md#nonnegativity-and-energy) (standard) | nonnegative load | the delivered trajectory | `operators.clip_nonnegative` | `FeasibilityTests` |
| P12 | [Energy, nonnegativity and no-harm are incompatible](PROOFS.md#nonnegativity-and-energy) | always (two-hour counterexample) | reading energy from the level | `operators.project_to_mean` | `FeasibilityTests` |
| P13 | [Day-level projection: a conditional guarantee](PROOFS.md#nonnegativity-and-energy) | nonnegative level and load; level under-forecast by at most the smallest true daily mean | an optional projection | `operators.daily_projection` | `FeasibilityTests` |
| P14 | [A mean path underestimates the expected peak](PROOFS.md#peak) (standard) | exact conditional means | a separate peak readout | — | `PeakTests` |
| P15 | [Scalar form and bounds of the peak operator](PROOFS.md#peak) | always | the peak readout | `ankyra.readouts.peak_readout` | `ReadoutTests` in [tests/](../tests/test_blocks_and_readouts.py) |
| P16 | [Peak error decomposition](PROOFS.md#peak) | always; the amplitude term has no fixed sign | how level gains reach the peak | `operators.peak_error_decomposition` | `PeakTests` |
| P17 | [Finite-support median property](PROOFS.md#peak) | constant levels within type, independent draws, $((m-1)/m)^n<1/2$ | what the envelope estimates | `operators.max_lower_median` | `PeakTests` |
| P18 | [Asymmetric peak costs](PROOFS.md#peak) (standard) | always | choosing a peak method under a cost | `operators.asymmetric_peak_cost` | `PeakTests` |
| P19 | [Pooled versus unit-equal summaries](PROOFS.md#estimands) | always (identity) | why several estimands are reported | `ankyra.metrics.pooled_ratio_decomposition` | `EstimandTests` |

`operators.*` is [operators.py](operators.py) in this folder; `ankyra.*` is the forecaster, whose own functions carry
P1, P3, P15 and P19. Check names are test classes in [test_operators.py](test_operators.py) unless a folder is given.

## How the properties enter the forecaster

- **Blocks (P1–P3).** The forecast is assembled from three orthogonal blocks, so each can come from the source that
  estimates it best, and energy is read from the level alone.
- **Division of labour (P4–P6).** Any division between two forecasters can be scored from block losses, but a division
  that is optimal on pooled error can still lose for the typical unit. ANKYRA therefore weights each unit by its own
  record.
- **Weights (P7–P10).** A record of $m$ hours supports $\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$ completed
  errors; below two the weights are equal. Shrinkage bounds how far they move, and the handover uses least-squares
  weights because shared errors pull inverse-MSE weights towards one half.
- **Energy and nonnegativity (P11–P13).** Clipping cannot hurt any hour, but no map keeps energy, nonnegativity and
  no-harm together, so energy is read before the clip. (On off-state and micro-load windows the forecaster returns the
  foundation model's trajectory unchanged, without the clip.)
- **Peak (P14–P18).** The maximum of a smooth forecast underestimates the peak, so the peak is read from a historical
  excursion envelope with an exact scalar form, an error decomposition and a median property under a stated working
  distribution.
- **Estimands (P19).** Pooled and unit-equal summaries can disagree in sign for an algebraic reason, so the evaluation
  reports the unit-equal log ratio, the mean per-unit rank, the pooled ratio and conventional metrics together.

Until release 1.1.1 the operators were part of the package as `ankyra.operators` and the proofs were `docs/THEORY.md`;
from 1.2.0 they are kept here, apart from the forecaster.
