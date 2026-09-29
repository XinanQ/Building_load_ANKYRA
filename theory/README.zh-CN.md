# 理论：ANKYRA 背后的精确性质

[English](README.md) · [证明](PROOFS.md) · [算子](operators.py) · [数值检验](test_operators.py) · [返回预测模型](../README.zh-CN.md)

本文件夹收录预测模型之外的数学贡献。预测模型本身是 [`ankyra/`](../ankyra/) 包，它不引用本文件夹。这里的内容解释并限定模型的设计：

- 为什么把月前预测拆成水平、日路径和日内形状三块；
- 权重需要多少历史，最多能偏离等权多远；
- 电量与峰值读出能保证什么、不能保证什么；
- 评估为什么要并列报告几种估计量。

每条性质都有三种支撑：

| 文件 | 内容 |
|---|---|
| [PROOFS.md](PROOFS.md) | 陈述、证明，以及标出适用边界的反例；有数据测量结果的，附在陈述之后 |
| [operators.py](operators.py) | 把性质写成函数，适用于任何预测模型的 744 小时轨迹 |
| [test_operators.py](test_operators.py) | 数值检验，含反例（29 项） |

```bash
python -m unittest discover -s theory -t .
```

![测试窗口上的精确性质](../figures/fig7_operators.png)

## 十九条性质

标为“标准”的是已知结论，设计依赖它们，这里收录但不作为新贡献；其余在第三列写明的条件下成立。它们都不是精度保证，精度见 [docs/EVALUATION.md](../docs/EVALUATION.md)。

| | 性质 | 成立条件 | 在 ANKYRA 中的用途 | 代码 | 检验 |
|---|---|---|---|---|---|
| P1 | [三块恒等式](PROOFS.md#blocks)（标准） | 总是 | 每块交给估得最好的来源 | `ankyra.blocks.block_losses` | `BlockGeometryTests` |
| P2 | [四块分解；没有周频 Fourier 分量](PROOFS.md#blocks) | 总是（744 小时窗口） | 用日类型代替周分量 | `operators.four_block_losses` | `BlockGeometryTests` |
| P3 | [电量就是水平](PROOFS.md#blocks) | 总是 | 电量读出 | `ankyra.blocks.level` | `BlockGeometryTests` |
| P4 | [精确替换与水平份额上界](PROOFS.md#replacement) | 替换值固定 | 用块损失给任意分工打分 | `operators.replace_blocks` | `ReplacementTests` |
| P5 | [两来源分工：合并最优与单位层面的不对称](PROOFS.md#replacement) | 两个来源、按块 | 固定分工为什么不够 | `operators.division_log_ratio` | `ReplacementTests` |
| P6 | [修正量核算](PROOFS.md#replacement)（标准） | 总是 | 诊断一项修正 | `operators.correction_accounting` | `ReplacementTests` |
| P7 | [已完成误差的支撑长度](PROOFS.md#historical-weights) | 记录完整；缺失只会减少计数 | 权重需要多少历史 | `operators.completed_windows` | `SupportTests` |
| P8 | [收缩界](PROOFS.md#historical-weights) | 支撑一致、起报时无候选缺失 | 权重最多移动多远 | `operators.mixture_mass_bounds` | `ShrinkageTests` |
| P9 | [候选缺失时混合重新归一](PROOFS.md#historical-weights) | 总是；反例说明 P8 在哪里失效 | 界何时不再成立 | `operators.retained_data_share` | `ShrinkageTests` |
| P10 | [共享误差下的最小二乘权与逆 MSE 权](PROOFS.md#historical-weights) | 两个预测含共同误差 | 分周交接的权重 | `operators.two_source_weights` | `ShrinkageTests` |
| P11 | [截断到零不会增大任何小时的误差](PROOFS.md#nonnegativity-and-energy)（标准） | 负荷非负 | 交付的轨迹 | `operators.clip_nonnegative` | `FeasibilityTests` |
| P12 | [电量、非负与不增误差三者不可兼得](PROOFS.md#nonnegativity-and-energy) | 总是（两小时反例） | 电量从水平读出 | `operators.project_to_mean` | `FeasibilityTests` |
| P13 | [日层面投影：有条件的保证](PROOFS.md#nonnegativity-and-energy) | 水平与负荷非负；水平低估不超过最小真实日均值 | 可选的投影 | `operators.daily_projection` | `FeasibilityTests` |
| P14 | [均值路径低估期望峰值](PROOFS.md#peak)（标准） | 精确条件均值 | 单独的峰值读出 | — | `PeakTests` |
| P15 | [峰值算子的标量形式与界](PROOFS.md#peak) | 总是 | 峰值读出 | `ankyra.readouts.peak_readout` | [tests/](../tests/test_blocks_and_readouts.py) 中的 `ReadoutTests` |
| P16 | [峰值误差分解](PROOFS.md#peak) | 总是；幅度项没有固定符号 | 水平的改进如何传到峰值 | `operators.peak_error_decomposition` | `PeakTests` |
| P17 | [有限样本中位数性质](PROOFS.md#peak) | 同类型日水平不变、独立抽样、$((m-1)/m)^n<1/2$ | 包络估计的是什么 | `operators.max_lower_median` | `PeakTests` |
| P18 | [非对称峰值成本](PROOFS.md#peak)（标准） | 总是 | 按成本选择峰值方法 | `operators.asymmetric_peak_cost` | `PeakTests` |
| P19 | [合并与单位等权汇总](PROOFS.md#estimands) | 总是（恒等式） | 为什么并列报告几种估计量 | `ankyra.metrics.pooled_ratio_decomposition` | `EstimandTests` |

`operators.*` 指本文件夹的 [operators.py](operators.py)；`ankyra.*` 是预测模型，P1、P3、P15、P19 由模型自身的函数承载。检验名是 [test_operators.py](test_operators.py) 中的测试类，另注文件夹的除外。

## 这些性质怎样进入模型

- **三块（P1–P3）**：预测由三个正交块组成，每块可以取自估得最好的来源，电量只由水平决定。
- **分工（P4–P6）**：两个模型之间的任何分工都能用块损失打分，但合并误差最优的分工仍可能让典型单位变差，所以 ANKYRA 按每个单位自己的记录定权。
- **权重（P7–P10）**：$m$ 小时的记录支撑 $\min\lbrace12,\lfloor(m-1344)/744\rfloor\rbrace_+$ 个已完成误差，少于两个时等权；收缩界限定权重的移动；共享误差会把逆 MSE 权拉向一半，所以交接用最小二乘权。
- **电量与非负（P11–P13）**：截断不会伤害任何小时，但没有映射能同时保持电量、非负和不增误差，所以电量在截断前读出。
- **峰值（P14–P18）**：平滑预测的最大值会低估峰值，所以峰值由历史偏移包络读出；它有精确的标量形式、误差分解，以及在写明的工作分布下的中位数性质。
- **估计量（P19）**：合并与单位等权汇总可能因代数原因符号相反，所以评估并列报告单位等权 log 比、平均单位排名、合并比与常规指标。

1.1.1 及以前，这些算子是包内的 `ankyra.operators`，证明在 `docs/THEORY.md`；从 1.2.0 起单独放在这里，与预测模型分开。
