# Exact properties

ANKYRA is assembled from identities and elementary bounds rather than from fitted relationships. This page states
them, numbered P1–P19 in the order of the pipeline. They make the construction auditable:

- any division of labour between two forecasters can be scored from block losses;
- every weight has a stated support requirement and a bound on how far it can move;
- every readout has a guarantee or a counterexample that marks where the guarantee stops.

Each property is implemented in [`ankyra/operators.py`](../ankyra/operators.py) (or `blocks`, `readouts`, `metrics`) and
checked in [`tests/test_operators.py`](../tests/test_operators.py), counterexamples included. Where a study measured a
property's consequence on data, the evidence follows the statement.

- *Earlier study* means the first version of this model (HCR-Load), evaluated on Spanish supply points and BDG2.
- Unit-equal log RMS ratios are reported with 95% unit-and-month (UM) bootstrap intervals, and percentages are
  $100[1-\exp(r)]$.

Several statements are standard, and they are marked as such. None of them is an accuracy guarantee: accuracy is
measured in [EVALUATION.md](EVALUATION.md).

![Exact properties on a test window](../figures/fig7_operators.png)

| | Property | Used for | Code |
|---|---|---|---|
| P1 | Block identity | assigning each block to a source | `blocks.block_losses` |
| P2 | Four blocks; no weekly Fourier bin | day types instead of a weekly component | `operators.four_block_losses` |
| P3 | Energy is the level | the energy readout | `blocks.level` |
| P4 | Exact replacement and the level-share bound | scoring any division from block losses | `operators.replace_blocks` |
| P5 | Two-source division: pooled optimum, unit-level asymmetry | why a fixed division is not enough | `operators.division_log_ratio` |
| P6 | Correction accounting | diagnosing a correction | `operators.correction_accounting` |
| P7 | Completed error support | how much history the weights need | `operators.completed_windows` |
| P8 | Shrinkage bounds | how far the weights can move | `operators.mixture_mass_bounds` |
| P9 | Deletion renormalises the mixture | when the bounds stop holding | `operators.retained_data_share` |
| P10 | Least squares versus inverse MSE under shared errors | the weekly handover weights | `operators.two_source_weights` |
| P11 | Clipping cannot increase any hour's error | the delivered trajectory | `operators.clip_nonnegative` |
| P12 | Energy, nonnegativity and no-harm are incompatible | reading energy from the level | `operators.project_to_mean` |
| P13 | Day-level projection: a conditional guarantee | an optional projection | `operators.daily_projection` |
| P14 | A mean path underestimates the expected peak | a separate peak readout | — |
| P15 | Scalar form and bounds of the peak operator | the peak readout | `readouts.peak_readout` |
| P16 | Peak error decomposition | how level gains reach the peak | `operators.peak_error_decomposition` |
| P17 | Finite-support median property | what the envelope estimates | `operators.max_lower_median` |
| P18 | Asymmetric peak costs | choosing a peak method under a cost | `operators.asymmetric_peak_cost` |
| P19 | Pooled versus unit-equal summaries | why several estimands are reported | `metrics.pooled_ratio_decomposition` |

## Blocks

**P1. Block identity (standard).** A 744-hour trajectory covers $D=31$ origin-aligned days of $H=24$ hours. Its level
$\ell$, centred daily path $b_d$ and within-day path $w_{d,h}$ are orthogonal projections of ranks 1, 30 and 713, so for
an error $e=F-y$

$$\frac1T\sum_{d,h}e_{d,h}^2=\ell(e)^2+\frac1D\sum_d b_d(e)^2+\frac1T\sum_{d,h}w_{d,h}(e)^2 .$$

**P2. Four blocks, and no weekly Fourier bin.** Split the within-day error into its hour-of-day mean
$\bar w_h=D^{-1}\sum_d w_{d,h}$ and the day-by-hour interaction $u_{d,h}=w_{d,h}-\bar w_h$. With $J_n=n^{-1}\mathbf 1\mathbf 1^\top$
and the day index outermost, consider the four projections

$$J_D\otimes J_H,\qquad (I-J_D)\otimes J_H,\qquad J_D\otimes(I-J_H),\qquad (I-J_D)\otimes(I-J_H).$$

They are symmetric, idempotent and mutually orthogonal, sum to the identity and have ranks 1, 30, 23 and 690, so

$$\frac1T\sum e^2=\ell^2+\frac1D\sum_d b_d^2+\frac1H\sum_h\bar w_h^2+\frac1T\sum_{d,h}u_{d,h}^2 .$$

$J_D\otimes I_H$ projects onto 24-hour periodic sequences. On the 744-hour window these are spanned by the DFT
frequencies $f$ with $31\mid f$.

A DFT bin is 168-hour periodic only if $7f/31$ is an integer. Because 7 and 31 are coprime, that again means $31\mid f$.
The window therefore has no weekly Fourier subspace separate from the daily harmonics. Weekly effects fall into the
between-day and interaction blocks, and ANKYRA represents them by day types. Day types are one modelling choice, not a
mathematical necessity.

**P3. Energy is the level.** The window's energy error is $744\,\ell(e)$ kWh for loads in kW. The constant direction is
the smallest subspace that carries this energy functional.

- For one window and a positive denominator, a smaller squared level error means a smaller absolute percentage energy
  error.
- Aggregated over windows and units, the two can rank methods differently.

## Replacement

**P4. Exact replacement.** Take fixed estimates $\ell^\ast$ and a centred $b^\ast$. The replacement
$F'=\ell^\ast+b^\ast+w(F)$ changes the MSE by exactly the change in the replaced blocks' losses. Replacements with
fixed estimates are idempotent and commute.

Let $\pi_k$ be the old block shares of the MSE and $\rho_k$ the block RMS ratios. Then

$$\frac{\mathrm{MSE}'}{\mathrm{MSE}}=1+\sum_k\pi_k(\rho_k^2-1).$$

A level-only replacement can therefore reduce the MSE by at most the level share $\pi_\ell$, however accurate the new
level. Replacements are scored from block losses, so they recover no peak and no absolute loss.

*Evidence (earlier study; 486 Spanish supply points).*

- Replacing the level and daily path of trained forecasters improved DLinear by 5.0% (log −0.0513 [−0.0715, −0.0335]).
- For PatchTST the effect was unresolved (−0.0042 [−0.0234, +0.0229]), and replacing the level alone gave an adverse
  point estimate.
- For the compact neural model the level held 20.8% of pooled hourly squared error, but only about 5% for the median
  unit. A large level gain therefore gave a small hourly gain.

A replacement has to be checked for each base forecaster.

**P5. Two-source division.** Pooled block losses add. Taking each block from the source with the smaller pooled block
loss therefore gives the pooled optimum among the eight block-wise divisions of two sources.

For a single unit, let $\pi$ be the modified source's share of its own MSE in the replaced blocks, and $r$ the ratio
of the donor's squared error there to the source's. The division's log RMS ratio to the modified source is

$$\tfrac12\log\big[1+\pi(r-1)\big].$$

A gain is bounded below by $\tfrac12\log(1-\pi)$; a loss is unbounded in $r$.

*Consequence.* A fixed division can be the pooled optimum and still lose on the unit-equal estimand. A minority of
units whose historical daily means fail badly can outweigh a majority that gain.

- On the Spanish development store the fixed division (history's level and daily path, TimesFM's shape) was the pooled
  optimum of the two sources.
- 67.6% of units favoured it over TimesFM, yet the unit-equal mean favoured TimesFM.

ANKYRA's per-unit weights and weekly handover respond to this: each unit's own record decides how much of each source
it uses.

**P6. Correction accounting.** Let $e=y-\hat y$ be a reference error and $D$ a correction. Then

$$\Delta\mathrm{MSE}=\mathbb E[D^2]-2\,\mathbb E[eD].$$

- The correction helps if and only if $2\mathbb E[eD]>\mathbb E[D^2]$.
- $\mathbb E[eD]\le0$ means it points the wrong way.
- $0<2\mathbb E[eD]<\mathbb E[D^2]$ means it points the right way but is too large.

At a single window, changing an error $r$ by $\delta$ helps exactly when $\delta(2r+\delta)<0$. The share of errors
with one sign cannot decide this on its own.

*Evidence (earlier study; BDG2 weather diagnostic on two development surfaces).*

- Building-equal, a fully weather-adjusted level improved on the adaptive combination by 5.98% and 5.79%.
- Site-equal, the improvement was only 0.70% and 3.26%.
- At individual sites, the identity separated corrections that pointed the wrong way from corrections that pointed the
  right way but were too large.

## Historical weights

**P7. Completed error support.** Pseudo-origins are spaced 744 h apart, each needs a 1,344-hour context, and there are
at most 12. A complete record of $m$ hours then yields

$$K_{\rm eff}(m)=\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$$

completed errors. Marking hours as missing can only lower this count.

The weights need two errors. The data share is therefore $K_{\rm eff}/(K_{\rm eff}+8)$ for $K_{\rm eff}\ge2$, and zero
below that (equal weights):

- 0.20 after 2,832 h (118 days);
- about 0.33, 0.47 and 0.53 after 6, 9 and 12 months;
- 0.60 from 10,272 h.

The annual candidate also needs its lag window at each pseudo-origin. Its two errors therefore need
$8{,}760+2\times744=10{,}248$ h, about 14 months: a year of observations supplies an annual prediction but not its error
record.

These are necessary support lengths, not accuracy guarantees. The counts are not independent sample sizes, because
contexts overlap.

*Evidence (earlier study; Spanish development store, 487 units).*

- Restricting load history to 12, 9 and 6 months at the same origins worsened geometric level RMS by 6.18%, 14.17% and
  20.62% against full history, with intervals above zero. An 18-month cap was unresolved.
- The median effective pseudo-origins (12, 9, 7 and 4) matched the formula.
- At 12 months no annual candidate had two errors. Removing the annual candidates from both arms made the 12-month loss
  unresolved (+0.52%).

**P8. Shrinkage bounds.** Let $w=(1-\rho)p+\rho q$, with prior $p$ and data weights $q$ on the same support.

- Every candidate subset $B$ satisfies $(1-\rho)p(B)\le w(B)\le(1-\rho)p(B)+\rho$.
- A combined prediction moves from the prior combination by at most $\rho R_h\,\mathrm{TV}(q,p)$, where $R_h$ is the
  range of the candidate predictions. For a uniform prior on $m$ candidates this is at most $\rho(1-1/m)R_h$.

For the four non-annual level candidates of the historical estimator with matched support $k\ge2$, $\rho=k/(k+8)$.
The total weather weight therefore lies in $[(1-\rho)/2,(1+\rho)/2]$: [0.4, 0.6] at $k=2$, [1/3, 2/3] at 4 and
[0.2, 0.8] at 12. ANKYRA's level adds the model candidate. Its prior weather mass is then 3/7 when all seven candidates are supported
(2/5 before the annual candidates are), and the general bound applies with that $p(B)$.

These bounds limit movement from the prior, not forecast error.

**P9. Deletion renormalises the mixture.** Suppose only a set $R$ of candidates is available at the real origin, with
prior mass $P$ and data mass $Q$. The renormalised weights are then a mixture with

$$\rho_R=\frac{\rho Q}{(1-\rho)P+\rho Q},$$

and the bounds of P8 must be re-evaluated.

- *Counterexample.* Take four candidates with a uniform prior, $q$ concentrated on the third, $\rho=0.2$ and
  $R=\lbrace1,3\rbrace$. Then $\rho_R=1/3$, and the weather mass becomes 2/3, above the old bound 0.6 (Figure 7c).
- *Discontinuity.* The two-error threshold is a jump. In a limiting example, going from one error (equal weights) to
  two moves the weights by an L1 distance of 0.3.

**P10. Least squares versus inverse MSE under shared errors.** When two forecasts of the same load share an error
component, the two weights behave differently:

- the inverse-MSE weight $\mathrm{MSE}_a/(\mathrm{MSE}_a+\mathrm{MSE}_b)$ tends to 1/2 as the shared variance grows;
- the least-squares weight $\langle y-a,\,b-a\rangle/\Vert b-a\Vert^2$ depends only on the part in which the forecasts
  differ.

ANKYRA's weekly handover therefore uses the least-squares weight [Bates and Granger, 1969], shrunk towards 1/2 with
$K_0=2$. Shared errors are the rule here: on the Spanish development store, the within-day errors of the earlier
historical model and TimesFM correlated at 0.83 (pooled).

## Nonnegativity and energy

**P11. Clipping cannot increase any hour's error (standard).** If realised load is nonnegative, then
$|\max(x_h,0)-y_h|\le|x_h-y_h|$ for every hour. Hourly MSE, MAE and every quantile of the window's error distribution
therefore cannot increase.

- The clip raises delivered energy by $\Delta=\sum_{d,h}\max(-F_{d,h},0)$, which is known at the origin.
- It is positively homogeneous, so it does not correct scale errors.
- The guarantee does not hold for net-metered loads, which can be negative.

**P12. Energy, nonnegativity and no-harm are incompatible.** No map can keep the energy readout, return nonnegative
load and guarantee no increase in error, all at once.

Two hours are enough to show it (Figure 7d). Take the forecast $p=(-1,3)$, whose mean is 1, and the truth $y=(0,4)$.

- The nonnegative trajectories with mean 1 lie on the line $x_1+x_2=2$.
- That line is tangent at $p$ to the disc $\Vert x-y\Vert^2\le\Vert p-y\Vert^2=2$, so every feasible point is strictly worse than
  $p$.
- The best feasible point, $(0,2)$, has squared error 4. Clipping gives $(0,3)$, with error 1.

ANKYRA therefore reads energy from the level and projects only the delivered trajectory. In the earlier study the
clip raised delivered energy by 4.8 and 3.9 kWh per window on two Spanish cohorts.

**P13. Day-level projection: a conditional guarantee.** This option projects the 31 daily means onto
$\mathcal A=\lbrace x\ge0:\bar x=\max(\hat\ell,0)\rbrace$ before clipping, and keeps the within-day deviations.

*Condition.* The forecast level is nonnegative, the load is nonnegative, and the level is not under-forecast by more
than the smallest true daily mean: $\ell^\ast-\hat\ell\le\min_d m^\ast_d$.

*Guarantee.* Under the condition, the daily-mean error cannot increase, and therefore neither can the hourly MSE.

*Proof.*

1. The shifted truth $\tilde m=m^\ast+(\hat\ell-\ell^\ast)\mathbf 1$ lies in $\mathcal A$.
2. Projection onto a closed convex set moves no point farther from any member of the set.
3. On $\mathcal A$, the distance to $m^\ast$ equals the distance to $\tilde m$ plus the constant
   $31(\hat\ell-\ell^\ast)^2$.

The guarantee is relative to the unprojected trajectory, not to the clipped one.

*Evidence (earlier study; exposed Spanish cohort).*

- Against hourly clipping alone the option was non-inferior: −0.0009 [−0.0030, +0.0002] on live windows, pooled MSE
  ratio 1.00003.
- There was no violation in the 139 windows covered by the condition.
- In 93 of the 173 windows outside it, the daily-mean error rose, as the condition allows.

The option is provided as `operators.daily_projection`. ANKYRA's evaluated forecasts use the hourly clip.

## Peak

**P14. A mean path underestimates the expected peak (standard).** For exact conditional means, by convexity of the
maximum,

$$\max_{d,h}\mathbb E[y_{d,h}\mid\mathcal F_o]\le\mathbb E\big[\max_{d,h}y_{d,h}\mid\mathcal F_o\big].$$

Fitted forecasters are median-type summaries, not exact conditional means. The inequality therefore motivates a
separate readout; it does not guarantee that any particular correction helps.

**P15. Scalar form and bounds.** Let $A_t$ be the largest daily excursion above the day's own mean among the four most
recent context days of type $t$. Because maxima commute, the hour-wise envelope equals a scalar maximum:

$$U=\max_{d,h}\big(\hat L_d+\max_{j\in\mathcal J(\tau_d)}a_{j,h}\big)=\max_d\,(\hat L_d+A_{\tau_d}).$$

- Only daily peak excursions enter, not peak timing.
- Excursions have zero day mean, so $A_t\ge0$ and $U\ge\max_d\hat L_d\ge\bar F$.
- $\hat P_\kappa=\bar F+\kappa(U-\bar F)\ge U$ for $\kappa\ge1$. ANKYRA uses $\kappa=1$.

**P16. Peak error decomposition.** Let $d^\ast$ be the realised peak day, $\hat d$ the selected day and
$a_d(y)=\max_h w_{d,h}(y)$. Then

$$U-M(y)=\ell(e)+\big[b_{d^\ast}(F)-b_{d^\ast}(y)\big]+\big[A_{\tau_{d^\ast}}-a_{d^\ast}(y)\big]+\Delta_{\rm sel},\qquad \Delta_{\rm sel}\ge0,$$

and $\hat P_\kappa-M(y)=U-M(y)+(\kappa-1)(U-\bar F)$.

The forecast's level and daily path enter the peak directly, so ANKYRA's level gains carry into it. The amplitude term
has no universal sign, and the net error has to be measured. On the Cambridge test window of Figure 7f the terms are
−2.7 kW (level), −8.0 (between-day), −16.4 (amplitude) and +6.2 (selection).

**P17. Finite-support median property.** Assume:

- daily levels are constant within type;
- future daily excursions are drawn independently from each retained empirical sample;
- a type that attains the envelope has $m$ samples and $n$ future days.

If $((m-1)/m)^n<1/2$, the lower median of the future maximum equals the envelope. With four samples, three future days
of that type suffice.

Neither assumption can be dropped:

- excursions (0, 1, 2, 3) over two equal-level days give a median of 2, not 3;
- three days with levels (0, −100, −100) give a median of 1.

Under continuous iid sampling, the joint maximum of $m$ historical and $n$ future values is historical with probability
$m/(m+n)$. This is an unconditional sampling fact, not coverage for a particular building.

**P18. Asymmetric peak costs.** Let $\bar u$ and $\bar o$ be a method's mean under- and over-forecast of the peak.
Charge $\lambda$ per kW under and 1 per kW over, normalised so that $\lambda=1$ gives the MAE. The cost is

$$\frac{2(\lambda\bar u+\bar o)}{1+\lambda}=2\big[\tau\bar u+(1-\tau)\bar o\big],\qquad \tau=\frac{\lambda}{1+\lambda},$$

which is twice the pinball loss at level $\tau$ [Koenker and Bassett, 1978]. Each method is summarised by its pair
$(\bar u,\bar o)$, and the best method for any $\lambda$ lies on the lower envelope of the lines
$\tau\bar u+(1-\tau)\bar o$.

*Evidence for the peak operator.*

- Earlier study, 678 BDG2 buildings:
  - TimesFM's peak APE fell from 14.74% (raw trajectory maximum) to 8.40% with the specified readout and to 8.27% with
    the envelope alone ($\kappa=1$);
  - its share of under-predicted peaks fell from 0.93 to 0.54, and Chronos-2's APE fell from 16.21% to 8.66%;
  - in kW the corrected peaks were slightly worse;
  - the readout was not resolvably better than last month's observed peak (−0.22 APE points [−1.01, +0.54]).
- This study: against the maximum of ANKYRA's own trajectory, the readout reduced peak error by 22–77% on all eleven
  populations ([`results/peak_readout.csv`](../results/peak_readout.csv)).

## Estimands

**P19. Pooled versus unit-equal summaries.** Let unit $i$ have $n_i$ windows, reference RMS $R_i$ and RMS ratio
$\rho_i$. The two summaries weight units differently:

- the pooled MSE ratio is $\sum_i\omega_i\rho_i^2$, with $\omega_i\propto n_iR_i^2$;
- the unit-equal estimand is $N^{-1}\sum_i\log\rho_i$.

The two have opposite signs when units with large $n_iR_i^2$ have $\rho_i>1$.

Because $\rho_i$ has $R_i$ in its denominator, weights and ratios are mechanically coupled. The sign of a
disagreement therefore does not say which units benefit, and testing a size effect needs a size variable that is not
built from the errors. This is why the evaluation reports four summaries side by side: the unit-equal log ratio, the
mean per-unit rank, the pooled ratio and conventional metrics.

*Evidence (earlier study).* Disagreements occurred in both directions:

- the fixed division had 7.6% lower pooled MSE than TimesFM, while the unit-equal point estimate favoured TimesFM
  (+0.0111, unresolved);
- TimesFM improved on the compact neural model by 9.9% unit-equal, while its pooled MSE was 2.5% higher.
