# 理论：ANKYRA 背后的精确性质

[English](README.md) · [证明](PROOFS.md) · [算子](operators.py) · [数值检验](test_operators.py) · [返回预测器](../README.zh-CN.md)

本文件夹收录放在预测器旁边的数学贡献。预测器是 [`ankyra/`](../ankyra/) 这个包，包里没有任何代码引用本文件夹。这里的内容解释并限定它的设计：

- 为什么把月前预测拆成水平、日路径和日内形状；
- 权重需要多少历史，最多能离开等权多远；
- 电量读出和峰值读出能保证什么、不能保证什么；
- 评估为什么并列报告几种估计目标。

每条性质有三种支撑：

| 文件 | 内容 |
|---|---|
| [PROOFS.md](PROOFS.md) | 陈述、证明，以及标出适用边界的反例；某项研究在数据上测过后果的，附上该证据 |
| [operators.py](operators.py) | 把性质写成函数，适用于任何预测器的 744 小时轨迹 |
| [test_operators.py](test_operators.py) | 数值检验，含反例（29 项） |

```bash
python -m unittest discover -s theory -t .
```

![一个测试窗口上的精确性质](../figures/fig7_operators.png)

## 二十条性质

标为“标准”的性质是设计所依赖的已知结论；它们收录在这里，但不作为新贡献。其余性质在第三列的条件下成立。没有一条是精度保证：精度是在 [docs/EVALUATION.md](../docs/EVALUATION.md) 里测量的。

| | 性质 | 成立条件 | ANKYRA 用它做什么 | 代码 | 检验 |
|---|---|---|---|---|---|
| P1 | [块恒等式](PROOFS.md#blocks)（标准） | 总是 | 把每一块交给一个来源 | `ankyra.blocks.block_losses` | `BlockGeometryTests` |
| P2 | [四块；没有周频的傅里叶分量](PROOFS.md#blocks) | 总是（744 小时窗口） | 用日类型代替周分量 | `operators.four_block_losses` | `BlockGeometryTests` |
| P3 | [电量就是水平](PROOFS.md#blocks) | 总是 | 电量读出 | `ankyra.blocks.level` | `BlockGeometryTests` |
| P4 | [精确替换与水平份额界](PROOFS.md#replacement) | 替换用的估计是固定的 | 由块损失给任意分工打分 | `operators.replace_blocks` | `ReplacementTests` |
| P5 | [两来源分工：合并最优与单位层面的不对称](PROOFS.md#replacement) | 两个来源、按块 | 固定分工为什么不够 | `operators.division_log_ratio` | `ReplacementTests` |
| P6 | [修正量核算](PROOFS.md#replacement)（标准） | 总是 | 诊断一项修正 | `operators.correction_accounting` | `ReplacementTests` |
| P7 | [已完成误差的支撑](PROOFS.md#historical-weights) | 记录完整；缺失的小时只会减少个数 | 权重需要多少历史 | `operators.completed_windows` | `SupportTests` |
| P8 | [收缩界](PROOFS.md#historical-weights) | 支撑一致，起报时没有候选缺失 | 权重最多能移动多远 | `operators.mixture_mass_bounds` | `ShrinkageTests` |
| P9 | [候选缺失时混合重新归一](PROOFS.md#historical-weights) | 总是；一个反例标出 P8 在哪里失效 | 界何时不再成立 | `operators.retained_data_share` | `ShrinkageTests` |
| P10 | [共享误差下的最小二乘权与逆 MSE 权](PROOFS.md#historical-weights) | 各预测含共同的误差成分 | 分周交接的权重 | `operators.two_source_weights` | `ShrinkageTests` |
| P11 | [截断到零不会增大任何一个小时的误差](PROOFS.md#nonnegativity-and-energy)（标准） | 负荷非负 | 交付的轨迹 | `operators.clip_nonnegative` | `FeasibilityTests` |
| P12 | [电量、非负与不增误差三者不可兼得](PROOFS.md#nonnegativity-and-energy) | 总是（两小时的反例） | 电量从水平读出 | `operators.project_to_mean` | `FeasibilityTests` |
| P13 | [日层面的投影：有条件的保证](PROOFS.md#nonnegativity-and-energy) | 水平与负荷非负；水平的低估不超过最小的真实日均值 | 一个可选的投影 | `operators.daily_projection` | `FeasibilityTests` |
| P14 | [均值路径低估期望峰值](PROOFS.md#peak)（标准） | 精确的条件均值 | 单独的峰值读出 | — | `PeakTests` |
| P15 | [峰值算子的标量形式与界](PROOFS.md#peak) | 总是 | 峰值读出 | `ankyra.readouts.peak_readout` | [tests/](../tests/test_blocks_and_readouts.py) 里的 `ReadoutTests` |
| P16 | [峰值误差分解](PROOFS.md#peak) | 总是；幅度项没有固定的符号 | 水平的收益怎样传到峰值 | `operators.peak_error_decomposition` | `PeakTests` |
| P17 | [有限支撑中位数性质](PROOFS.md#peak) | 同类型日内水平不变、独立抽取、$((m-1)/m)^n<1/2$ | 包络估计的是什么 | `operators.max_lower_median` | `PeakTests` |
| P18 | [非对称的峰值成本](PROOFS.md#peak)（标准） | 总是 | 在给定成本下选择峰值方法 | `operators.asymmetric_peak_cost` | `PeakTests` |
| P19 | [合并汇总与单位等权汇总](PROOFS.md#estimands) | 总是（恒等式） | 为什么并列报告几种估计目标 | `ankyra.metrics.pooled_ratio_decomposition` | `EstimandTests` |
| P20 | [候选选择的证据界](PROOFS.md#evidence-bound)（标准结果；零基准为恒等式） | 每个候选有 T 个伪起报点误差 | 为什么水平权重要收缩、为什么预测锚定收益的是记录统计量而不是权重 | `operators.aggregation_rate`、`operators.exchangeable_hit_rate` | `EvidenceBoundTests` |

`operators.*` 指本文件夹里的 [operators.py](operators.py)；`ankyra.*` 是预测器，P1、P3、P15 和 P19 由它自身的函数承载。检验名是 [test_operators.py](test_operators.py) 里的测试类，注明了文件夹的除外。

## 这些性质怎样进入预测器

- **块（P1–P3）。** 预测由三个正交的块拼成，所以每一块可以取自把它估得最好的来源，电量只从水平读出。
- **分工（P4–P6）。** 两个预测器之间的任何分工都可以由块损失打分，但在合并误差上最优的分工，对典型单位仍可能是亏的。所以 ANKYRA 按每个单位自己的记录给它定权。
- **权重（P7–P10）。** $m$ 小时的记录支撑 $\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$ 个已完成误差；不足两个时权重相等。收缩限定权重能移动多远；交接用最小二乘权，因为共享误差会把逆 MSE 权拉向二分之一。
- **电量与非负（P11–P13）。** 截断不会让任何一个小时变差，但没有映射能同时保持电量、非负和不增误差，所以电量在截断之前读出。（在关停窗口和微负荷窗口上，预测器原样返回基础模型的轨迹，不做截断。）
- **峰值（P14–P18）。** 平滑预测的最大值会低估峰值，所以峰值从历史偏移包络读出；它有精确的标量形式、误差分解，以及在写明的工作分布下的中位数性质。
- **估计目标（P19）。** 合并汇总和单位等权汇总可能因代数原因符号相反，所以评估并列报告单位等权 log 比、平均单位排名、合并比和常规指标。

1.1.1 及以前的版本里，这些算子是包内的 `ankyra.operators`，证明是 `docs/THEORY.md`；从 1.2.0 起它们放在这里，与预测器分开。
