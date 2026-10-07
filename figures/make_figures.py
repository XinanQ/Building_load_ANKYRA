"""Figures of the ANKYRA repository, generated from ../results only.

    pip install -e ".[figures]"               # matplotlib is an optional dependency
    python figures/make_figures.py            # writes figures/*.pdf (vector) and figures/*.png (300 dpi)

The figures show the ten populations of the main comparison; Figures 9 and 9b add LCL, HKUST, Helsinki and UNICON
(results/lcl_by_day.csv, hkust_by_day.csv, helsinki_by_day.csv, unicon_by_day.csv).
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                   # noqa: E402
from matplotlib.colors import LinearSegmentedColormap              # noqa: E402
from matplotlib.lines import Line2D                                # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle, Patch   # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results"

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
    "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
    "mathtext.sf": "Arial", "mathtext.fallback": "stixsans",
    "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 6.8, "legend.frameon": False, "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "lines.linewidth": 1.0, "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 300,
    "axes.titleweight": "bold", "axes.titlelocation": "left",
})

ANKYRA = "#B2182B"
HIST = "#C0762A"          # the unit's own history
FM = "#5E4FA2"            # the foundation model
CLASS_COLOR = {
    "same information, trained": "#253494",
    "same information, zero-shot foundation model": "#1D91C0",
    "load only, zero-shot foundation model": "#807DBA",
    "load only, trained": "#EC7014",
    "load only, statistical": "#41AB5D",
    "per-unit regression": "#8C6D31",
    "zero-shot gradient boosting": "#9E9E9E", "profile": "#9E9E9E", "naive": "#BDBDBD",
}
CLASS_LEGEND = [("Same information · trained", "#253494"), ("Same information · zero-shot foundation model", "#1D91C0"),
                ("Load only · zero-shot foundation model", "#807DBA"), ("Load only · statistical", "#41AB5D"),
                ("Load only · trained", "#EC7014"), ("Per-unit regression (calendar, temperature)", "#8C6D31"),
                ("Profiles, naive, zero-shot GBT", "#9E9E9E")]
TEST = ["BDG2 2017", "Cambridge", "HEEW Arizona", "EWELD", "GoiEner non-household", "GoiEner households"]
PREVIEW = ["Oslo", "Drammen", "CINELDI", "Suzhou park"]
SHORT = {"BDG2 2017": "BDG2", "Cambridge": "Cambridge", "HEEW Arizona": "HEEW", "EWELD": "EWELD",
         "GoiEner non-household": "GoiEner NH", "GoiEner households": "GoiEner HH", "Oslo": "Oslo", "Drammen": "Drammen",
         "CINELDI": "CINELDI", "Suzhou park": "Suzhou park"}
TWO_LINE = {"GoiEner non-household": "GoiEner\nNH", "GoiEner households": "GoiEner\nHH"}
NICE = {"Holt-Winters": "Holt–Winters"}
GREY = "#595959"


def rows(name):
    with open(RES / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pct(r):
    return 100.0 * (1.0 - math.exp(r))


def save(fig, stem):
    fig.savefig(HERE / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.03, metadata={"CreationDate": None})
    fig.savefig(HERE / f"{stem}.png", bbox_inches="tight", pad_inches=0.03, dpi=300)
    plt.close(fig)


def label(m):
    return NICE.get(m, m)


# ============================================================================ Figure 1: architecture
def fig_architecture():
    fig = plt.figure(figsize=(7.2, 4.1))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(-7.0, 54); ax.axis("off")
    ink = "#1F1F1F"

    def box(x, y, w, h, title, fc, ec, tc=None, lw=0.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.0", fc=fc, ec=ec, lw=lw, zorder=1))
        ax.text(x + 1.1, y + h - 1.4, title, ha="left", va="top", fontsize=7.4, fontweight="bold", color=tc or ink, zorder=3)

    def txt(x, y, s, color=GREY, fs=6.1, **kw):
        ax.text(x, y, s, ha=kw.pop("ha", "left"), va=kw.pop("va", "top"), fontsize=fs, color=color, linespacing=1.4, zorder=3, **kw)

    def arrow(pts, color="#8C8C8C", lw=0.9):
        xs, ys = zip(*pts)
        if len(pts) > 2:
            ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, solid_capstyle="round", zorder=2)
        ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=7.5, lw=lw, color=color, shrinkA=0, shrinkB=0, zorder=2))

    def spark(x, y, w, h, yv, color, lw=0.8, step=False):
        yv = np.asarray(yv, float); xs = np.linspace(0, 1, len(yv)); yn = (yv - yv.min()) / max(np.ptp(yv), 1e-9)
        (ax.step if step else ax.plot)(x + w * xs, y + h * yn, color=color, lw=lw, zorder=3, **({"where": "mid"} if step else {}))

    # column headers
    for xc, t in ((10.5, "Known at the origin o"), (42.5, "Three orthogonal blocks"), (73.5, "Error-weighted handover"), (92.3, "Output")):
        ax.text(xc, 52.8, t, ha="center", va="center", fontsize=6.9, color="#8C8C8C", fontstyle="italic")

    # ---- inputs
    box(1, 18.5, 19.2, 31.8, "Unit's own history", "#EEF3FA", "#9DB4D6")
    txt(2.1, 45.6, "hourly load, temperature\nand calendar before o")
    t = np.arange(24 * 14)
    load = 1 + 0.6 * np.clip(np.sin(2 * np.pi * (t - 7) / 24), 0, None) * (np.floor(t / 24) % 7 < 5)
    spark(2.4, 34.8, 16.4, 4.6, load, "#4A6FA5", lw=0.55)
    txt(2.1, 31.4, "pseudo-origins o − 744k", color=ink, fs=6.1)
    xs = np.linspace(3.0, 17.8, 8)
    ax.plot([2.6, 18.6], [26.2, 26.2], color="#9DB4D6", lw=0.7, zorder=2)
    for i, xx in enumerate(xs):
        last = i == len(xs) - 1
        ax.plot([xx, xx], [25.2, 27.2], color=ANKYRA if last else "#4A6FA5", lw=1.1 if last else 0.7, zorder=3)
    ax.text(xs[-1], 27.7, "o", fontsize=6.2, color=ANKYRA, ha="center", va="bottom", fontweight="bold")
    txt(2.1, 23.8, "completed forecasts give every\ncandidate its own error record", fs=5.8)
    box(1, 2, 19.2, 14.5, "TimesFM 2.5", "#F2F0F8", "#B4ADD6", tc=FM)
    txt(2.1, 12.3, "zero-shot, load only\n1,344 h → 744 h, issued at\no and at o − 744k (k ≤ 6)", fs=5.9)
    hh = np.arange(24 * 5)
    spark(2.4, 3.0, 16.0, 2.6, 1 + 0.45 * np.clip(np.sin(2 * np.pi * (hh - 7) / 24), 0, None) + 0.04 * hh / len(hh), FM, lw=0.6)

    # ---- blocks
    box(24, 35.8, 37.5, 14.5, r"Level  $\ell$", "#FFF6EC", "#E8B67A", tc=HIST)
    txt(25.1, 46.2, "six historical candidates: recent, long-history\nand annual means, with and without weather", fs=5.9)
    txt(25.1, 40.7, "+ TimesFM window mean", color=FM, fs=5.9)
    txt(25.1, 38.1, r"weights $\propto$ 1/MSE at pseudo-origins, shrunk to equal ($K_0$ = 8)", fs=5.6)
    wts = [0.10, 0.22, 0.06, 0.13, 0.19, 0.05, 0.25]
    for i, wv in enumerate(wts):
        ax.add_patch(Rectangle((52.5 + 1.15 * i, 42.3), 0.8, 30 * wv * 0.28, fc=FM if i == 6 else HIST, ec="none", alpha=0.9, zorder=3))
    box(24, 18.5, 37.5, 14.8, r"Centred daily path  $b$", "#FFF6EC", "#E8B67A", tc=HIST)
    txt(25.1, 29.1, "seven historical candidate paths: 8-, 4- and 2-week\nday types, the annual window, the weather response", fs=5.9)
    txt(25.1, 22.5, r"same error weighting ($K_0$ = 2);  $\Sigma_d\, b_d = 0$", fs=5.9)
    spark(51.0, 20.8, 9.2, 3.4, [0.25, 0.9, 0.85, 0.9, 0.8, 0.12, 0.05] * 2, HIST, lw=0.8, step=True)
    box(24, 2, 37.5, 14.5, r"Within-day shape  $w$", "#F6F1F4", "#C4A3C9", tc=FM)
    txt(25.1, 12.3, r"day-demeaned TimesFM trajectory  $w^{T}$", color=FM, fs=5.9)
    txt(25.1, 9.7, r"+ the unit's analog-day shape  $S$: same day type," + "\n±14 days of year, up to 8 past days", color=HIST, fs=5.6)
    txt(25.1, 4.6, r"$w=w^{T}+\omega\,(S-w^{T})$,  $\omega\leq$ ½ from the unit's errors" + "\nat 3 pseudo-origins, shrunk to 0 (one value since 2.1)", fs=5.4)
    tt = np.linspace(0, 3, 160)
    spark(51.5, 11.0, 9.0, 3.6, np.sin(2 * np.pi * tt - 1.6) + 0.35 * np.sin(4 * np.pi * tt), FM, lw=0.8)

    # ---- handover
    box(65.2, 18.5, 17.4, 31.8, "Week-by-week\nhandover", "#FBEDEE", "#E3A0A6", tc=ANKYRA)
    ax.text(73.9, 41.9, r"$m_d=(1-\alpha_w)\,m_d^{H}+\alpha_w\,m_d^{T}$", ha="center", va="center", fontsize=6.9, color=ink, zorder=3)
    txt(66.3, 39.4, r"$m^{H}$: history ($\ell$ + $b$)", color=HIST, fs=5.9)
    txt(66.3, 36.9, r"$m^{T}$: TimesFM daily means", color=FM, fs=5.9)
    txt(66.3, 34.3, r"$\alpha_w$: least squares on ≤ 6" + "\npseudo-origin pairs (fixed\ndivision vs TimesFM),\n" + r"shrunk to ½ ($K_0$ = 2)", fs=5.5)
    al = [0.64, 0.52, 0.47, 0.41]
    for i, a in enumerate(al):
        ax.add_patch(Rectangle((67.4 + 3.3 * i, 20.6), 2.3, 7.6 * a, fc=ANKYRA, ec="none", alpha=0.85, zorder=3))
        ax.text(68.55 + 3.3 * i, 20.2, f"W{i + 1}", ha="center", va="top", fontsize=5.3, color=GREY)
    ax.plot([66.8, 80.5], [20.6 + 3.8, 20.6 + 3.8], color="#7F7F7F", lw=0.5, ls=(0, (2, 2)), zorder=4)
    ax.text(80.8, 24.4, "½", fontsize=5.6, color="#7F7F7F", va="center")

    # ---- output
    box(85.4, 18.5, 14.0, 31.8, "ANKYRA", "#FFFFFF", ANKYRA, tc=ANKYRA, lw=1.1)
    txt(86.5, 45.6, r"$F_{d,h}=m_d+w_{d,h}$" + "\nprojected onto F ≥ 0", color=ink, fs=6.1)
    txt(86.5, 39.8, "no training on the\ntarget series", fs=5.9)
    h = np.arange(24 * 6)
    spark(86.6, 30.6, 11.6, 3.8, 1 + 0.55 * np.clip(np.sin(2 * np.pi * (h - 7) / 24), 0, None) * (h // 24 < 5), ANKYRA, lw=0.6)
    ax.add_patch(FancyBboxPatch((86.3, 19.4), 12.2, 9.4, boxstyle="round,pad=0.15,rounding_size=0.8", fc="#FBEDEE", ec="#E3A0A6", lw=0.6, zorder=2))
    txt(86.9, 28.3, "off / micro-load switch", color=ANKYRA, fs=5.6, fontweight="bold")
    txt(86.9, 26.1, r"last 168 h $\leq 10^{-6}$ kW, or" + "\n" + r"all 1,344 h $\leq 10^{-3}$ kW" + "\n→ TimesFM unchanged", fs=5.3)
    box(85.4, 2, 14.0, 14.5, "Readouts", "#FFFFFF", "#9E9E9E")
    txt(86.5, 12.4, r"energy  $744\,\ell$", color=ink, fs=5.9)
    txt(86.5, 9.4, r"peak  $\mathrm{max}_d\,(\hat L_d+A_{\tau_d})$", color=ink, fs=5.9)
    txt(86.5, 6.4, "interval  pseudo-origin\nresidual quantiles", color=ink, fs=5.9)

    # ---- arrows (horizontal or right-angled, no crossings)
    g = "#8C8C8C"
    arrow([(20.5, 43.0), (23.7, 43.0)], HIST)
    arrow([(20.5, 25.9), (23.7, 25.9)], HIST)
    arrow([(20.5, 9.2), (23.7, 9.2)], FM)
    arrow([(20.5, 20.3), (22.3, 20.3), (22.3, 14.2), (23.7, 14.2)], HIST)
    arrow([(61.8, 43.0), (64.9, 43.0)], HIST)
    arrow([(61.8, 25.9), (64.9, 25.9)], HIST)
    arrow([(82.9, 34.4), (85.1, 34.4)], ANKYRA, lw=1.1)
    arrow([(61.8, 5.4), (83.6, 5.4), (83.6, 29.1), (85.1, 29.1)], FM)
    arrow([(92.4, 18.2), (92.4, 16.8)], g)

    ax.text(50, -0.4, r"Exact identity:  $\mathrm{MSE}=\ell(e)^2+\langle b_d(e)^2\rangle_d+\langle w_{d,h}(e)^2\rangle_{d,h}$"
            "  — the blocks are orthogonal, so each source is scored and anchored block by block (all three since 2.0).",
            ha="center", va="top", fontsize=6.4, color=GREY)
    ax.legend(handles=[Patch(fc=HIST, label="from the unit's own history"), Patch(fc=FM, label="from TimesFM 2.5"),
                       Patch(fc=ANKYRA, label="ANKYRA's error-weighted handovers")], loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
              fontsize=6.1, handlelength=1.0, handleheight=0.7, columnspacing=1.6, frameon=False)
    save(fig, "fig1_architecture")


# ============================================================================ Figure 2: test-set ranks and head-to-head
def fig_test_ranks():
    rk = [r for r in rows("benchmark_mean_unit_rank.csv") if r["subset"] == "late" and r["tier"] == "test"]
    pw = [r for r in rows("benchmark_pairwise.csv") if r["subset"] == "late" and r["tier"] == "test"]
    cls = {r["model"]: r["model_class"] for r in pw}
    lab = {r["model"]: r["model_label"] for r in rk}
    models = sorted({r["model"] for r in rk})
    M = np.array([[next(float(r["mean_unit_rank"]) for r in rk if r["model"] == m and r["set"] == s) for s in TEST] for m in models])
    order = np.argsort(M.mean(1), kind="stable"); models = [models[i] for i in order]; M = M[order]
    n = len(models)
    fig = plt.figure(figsize=(7.2, 4.55))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.05, left=0.19, right=0.985, top=0.83, bottom=0.17)
    ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1], sharey=ax)
    cmap = LinearSegmentedColormap.from_list("rank", ["#08306B", "#2171B5", "#6BAED6", "#C6DBEF", "#F7FBFF"])
    data = np.column_stack([M, M.mean(1)])
    ax.imshow(data, cmap=cmap, vmin=1, vmax=21, aspect="auto", interpolation="nearest")
    for i in range(n):
        for j in range(data.shape[1]):
            v = data[i, j]
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=5.9, color="white" if v < 8.5 else "#1A1A1A",
                    fontweight="bold" if models[i] == "ANKYRA" or j == data.shape[1] - 1 else "normal")
    ax.axvline(len(TEST) - 0.5, color="white", lw=2.4)
    ax.set_xticks(range(len(TEST) + 1)); ax.set_xticklabels([TWO_LINE.get(s, SHORT[s]) for s in TEST] + ["Mean"], fontsize=6.2, linespacing=1.05)
    ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=2)
    ax.set_yticks(range(n)); ax.set_yticklabels([label(lab[m]) for m in models], fontsize=6.6); ax.tick_params(axis="y", length=0, pad=9)
    for t_, m in zip(ax.get_yticklabels(), models):
        if m == "ANKYRA":
            t_.set_color(ANKYRA); t_.set_fontweight("bold")
    for i, m in enumerate(models):
        c = ANKYRA if m == "ANKYRA" else CLASS_COLOR.get(cls.get(m, ""), "#9E9E9E")
        ax.scatter([-0.78], [i], s=12, color=c, clip_on=False, marker="s", zorder=5)
    ia = models.index("ANKYRA")
    ax.add_patch(Rectangle((-0.5, ia - 0.5), data.shape[1], 1, fill=False, ec=ANKYRA, lw=1.5, zorder=6))
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("a   Mean per-unit rank on the six test sets (lower is better)", fontsize=7.6, pad=22)
    win = np.zeros(n); tie = np.zeros(n); loss = np.zeros(n)
    for i, m in enumerate(models):
        for r in pw:
            if r["model"] == m:
                lo, hi = float(r["um_low"]), float(r["um_high"])
                win[i] += hi < 0; loss[i] += lo > 0; tie[i] += not (hi < 0 or lo > 0)
    y = np.arange(n)
    bx.barh(y, win, color="#2166AC", height=0.62)
    bx.barh(y, tie, left=win, color="#D9D9D9", height=0.62)
    bx.barh(y, loss, left=win + tie, color=ANKYRA, height=0.62)
    for i in range(n):
        if models[i] == "ANKYRA":
            bx.text(0.12, i, "reference", va="center", fontsize=6.2, color=ANKYRA, fontstyle="italic")
        elif win[i] > 0:
            bx.text(win[i] - 0.12, i, f"{int(win[i])}", va="center", ha="right", fontsize=5.9, color="white", fontweight="bold")
    bx.set_xlim(0, 6); bx.set_xticks(range(7)); bx.set_xlabel("Number of test sets", fontsize=6.9, labelpad=2)
    bx.tick_params(axis="y", left=False, labelleft=False); bx.spines["left"].set_visible(False)
    bx.set_title("b   Head-to-head on the test sets", fontsize=7.6, pad=22)
    bx.legend(handles=[Patch(fc="#2166AC", label="ANKYRA better"), Patch(fc="#D9D9D9", label="not resolved"),
                       Patch(fc=ANKYRA, label="ANKYRA worse")], loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=3,
              fontsize=6.0, handlelength=1.0, handleheight=0.8, columnspacing=0.8, handletextpad=0.3)
    handles = [Line2D([], [], marker="s", ls="", color=c, markersize=4.3, label=t_) for t_, c in CLASS_LEGEND]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=4, fontsize=6.0, handletextpad=0.25, columnspacing=1.0)
    fig.text(0.01, 0.985, "21 forecasters on the late windows (origins after each set's training cutoff). Five baselines are given ANKYRA's information set;",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.955, "ANKYRA 2.1, re-evaluated on test sets first scored for 1.x; BDG2 includes the micro-load rule, written after its "
             "result was seen. NH/HH: non-/households. b: 95% bootstrap interval.", fontsize=6.3, color=GREY, va="top")
    save(fig, "fig2_test_ranks")


# ============================================================================ Figure 3: pairwise improvements with intervals
def fig_test_forest():
    pw = [r for r in rows("benchmark_pairwise.csv") if r["subset"] == "late" and r["tier"] == "test"]
    models = ["TiDE", "iTransformer-X", "GBT-T", "Chronos-2-X", "TimesFM-X", "TimesFM", "Chronos-2", "Holt-Winters", "MSTL"]
    cls = {r["model"]: r["model_class"] for r in pw}
    lo_x, hi_x = -30, 45
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.35), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.125, right=0.99, top=0.86, bottom=0.175, hspace=0.34, wspace=0.08)
    y = np.arange(len(models))[::-1].astype(float)
    for ax, s in zip(axs.ravel(), TEST):
        ax.axvspan(0, hi_x, color="#F3F6FA", zorder=0)
        ax.axvline(0, color="#7F7F7F", lw=0.6, zorder=1)
        ax.axhline(3.5, color="#BDBDBD", lw=0.5, ls=(0, (2, 2)))
        for yy, m in zip(y, models):
            r = next(rr for rr in pw if rr["set"] == s and rr["model"] == m)
            p, a, b = float(r["improvement_pct"]), pct(float(r["um_high"])), pct(float(r["um_low"]))
            c = CLASS_COLOR[cls[m]]
            sig_better, sig_worse = float(r["um_high"]) < 0, float(r["um_low"]) > 0
            ax.plot([max(a, lo_x), min(b, hi_x)], [yy, yy], color=c, lw=1.1, solid_capstyle="butt", zorder=2)
            for edge, beyond, d in ((lo_x, a < lo_x, 3.5), (hi_x, b > hi_x, -3.5)):
                if beyond:
                    ax.annotate("", xy=(edge, yy), xytext=(edge + d, yy), arrowprops=dict(arrowstyle="-|>", color=c, lw=0.8, mutation_scale=5))
            pc = min(max(p, lo_x + 1.2), hi_x - 1.2)
            face = ANKYRA if sig_worse else (c if sig_better else "white")
            ax.scatter([pc], [yy], s=17, color=face, edgecolor=ANKYRA if sig_worse else c, lw=0.9, zorder=3)
            if p > hi_x or p < lo_x:
                ax.text(pc + (-2.2 if p > hi_x else 2.2), yy + 0.42, f"{p:+.0f}%", fontsize=5.3, color=c, ha="right" if p > hi_x else "left",
                        va="center", bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"), zorder=4)
        title = {"BDG2 2017": "BDG2 †", "GoiEner non-household": "GoiEner non-household", "GoiEner households": "GoiEner households"}.get(s, SHORT[s])
        ax.set_title(title, fontsize=7.4)
        ax.set_xlim(lo_x, hi_x); ax.set_ylim(-0.7, len(models) - 0.3)
        ax.set_yticks(y); ax.set_yticklabels([label(m) for m in models], fontsize=6.4); ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#E5E5E5", lw=0.4, zorder=0)
    for ax in axs[1]:
        ax.set_xlabel("ANKYRA improvement over the model (%)", fontsize=6.8)
    fig.text(0.125, 0.975, "Unit-equal improvement 100[1 − exp(r)] in hourly RMS, 95% unit-and-month bootstrap intervals; filled = interval excludes zero, red = ANKYRA worse.",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.125, 0.945, "Above the dashed line: the five baselines given ANKYRA's information set. Below: foundation models and statistical models on load only.",
             fontsize=6.3, color=GREY, va="top")
    handles = [Line2D([], [], marker="o", ls="", color=c, markersize=4, label=t_) for t_, c in CLASS_LEGEND[:4]]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.1, bbox_to_anchor=(0.55, 0.058), handletextpad=0.2, columnspacing=1.0)
    nz = {r["model"]: float(r["improvement_pct"]) for r in rows("bdg2_near_zero_sensitivity.csv") if r["unit_set"] == "without the three near-zero meters" and r["subset"] == "late"}
    fig.text(0.125, 0.030, "† BDG2 includes the micro-load rule (since 2.0.1), written after the 2.0.0 result was seen: meters reading 0.0002–0.0005 kW are handed to TimesFM. Three of them "
             "still dominate the unit", fontsize=5.6, color="#7F7F7F")
    fig.text(0.125, 0.006, "means: for ANKYRA against models that do poorly on them, against it versus MSTL. Without the three meters: "
             + ", ".join(f"{label(m)} {nz[m]:+.0f}%" for m in ("TiDE", "iTransformer-X", "GBT-T", "Chronos-2-X", "TimesFM-X", "TimesFM")) + ".", fontsize=5.6, color="#7F7F7F")
    save(fig, "fig3_test_pairwise")


# ============================================================================ Figure 4: what the handover does
def fig_mechanism():
    ab = rows("ablation.csv"); lw_ = rows("lead_weeks_first_read.csv"); hg = rows("handover_granularity.csv")
    order = TEST + PREVIEW
    fig = plt.figure(figsize=(7.2, 5.3))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], hspace=0.5, wspace=0.34, left=0.105, right=0.985, top=0.895, bottom=0.085)
    y = np.arange(len(order))[::-1]

    def forest(ax, series, title, xlabel, legend_loc, xmax=None):
        ax.axhspan(y[len(TEST) - 1] - 0.5, y[0] + 0.5, color="#F3F6FA", zorder=0)
        ax.axvline(0, color="#7F7F7F", lw=0.6)
        for yy, s_ in zip(y, order):
            for get, mk, col, dy, _ in series:
                r = get(s_)
                if r is None:
                    continue
                p_, a, b = float(r["improvement_pct"]), pct(float(r["um_high"])), pct(float(r["um_low"]))
                sig = float(r["um_high"]) < 0 or float(r["um_low"]) > 0
                if xmax is not None and b > xmax:                         # interval runs past the axis: clip and mark
                    ax.annotate("", xy=(xmax, yy + dy), xytext=(xmax - 2.5, yy + dy), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.7, mutation_scale=4)); b = xmax
                ax.plot([a, b], [yy + dy, yy + dy], color=col, lw=0.9)
                ax.scatter([p_], [yy + dy], marker=mk, s=15 if mk == "o" else 11, color=col if sig else "white", edgecolor=col, lw=0.8, zorder=3)
        ax.set_yticks(y); ax.set_yticklabels([SHORT[s_] for s_ in order], fontsize=6.4)
        for t_, s_ in zip(ax.get_yticklabels(), order):
            if s_ in TEST:
                t_.set_fontweight("bold")
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel(xlabel, fontsize=6.8); ax.set_title(title, fontsize=7.6)
        if xmax is not None:
            ax.set_xlim(right=xmax)
        ax.legend(handles=[Line2D([], [], marker=mk, ls="", color=col, markersize=3.8 if mk == "o" else 3.2, label=lab) for _, mk, col, _, lab in series],
                  loc=legend_loc, fontsize=5.9, handletextpad=0.2, borderaxespad=0.1)

    def ab_row(key):
        return lambda s_: next((rr for rr in ab if rr["set"] == s_ and rr["ablation"].startswith(key)), None)

    def hg_row(key):
        return lambda s_: next((rr for rr in hg if rr["set"] == s_ and rr["contrast"] == key), None)

    ax = fig.add_subplot(gs[0, 0])
    forest(ax, [(ab_row("fixed division"), "o", ANKYRA, 0.32, "vs F0 (1.x fixed division)"), (ab_row("without off-state"), "D", "#4D4D4D", 0.16, "vs F1 (1.x without off-state rule)"),
                (ab_row("ANKYRA 1.x"), "s", HIST, 0.0, "vs 1.x (no within-day anchoring)"), (ab_row("ANKYRA 2.0.0"), "^", "#8C6D31", -0.16, "vs 2.0.0 (no micro-load rule)"),
                (ab_row("ANKYRA 2.0.1"), "v", "#5E8C61", -0.32, "vs 2.0.1 (trust per lead block)")],
           "a   Ablation", "ANKYRA 2.1 improvement (%)", "lower right", xmax=45.0)
    ax.text(ax.get_xlim()[1], y[len(TEST) - 1] - 0.22, "test sets ", fontsize=6, color="#4A6FA5", fontstyle="italic", ha="right", va="center")
    ax.set_ylim(y[-1] - 0.75, y[0] + 0.65)
    dx = fig.add_subplot(gs[0, 1])
    forest(dx, [(hg_row("C1 AW vs Ah"), "o", ANKYRA, 0.17, "vs fixed ½ mixture"), (hg_row("C2 AW vs AM"), "s", FM, -0.17, "vs one weight per month")],
           "b   Weekly per-unit weights against simpler mixing", "Improvement of ANKYRA's weekly weights (%)", "lower right")
    dx.set_ylim(y[-1] - 0.75, y[0] + 0.65)
    dx.legend(handles=[Line2D([], [], marker="o", ls="", color=ANKYRA, markersize=3.8, label="vs fixed ½ mixture"),
                       Line2D([], [], marker="s", ls="", color=FM, markersize=3.2, label="vs one weight per month")],
              loc="lower right", bbox_to_anchor=(1.0, 0.11), fontsize=5.8, handletextpad=0.2, borderaxespad=0.15)

    bx = fig.add_subplot(gs[1, 0]); cx = fig.add_subplot(gs[1, 1])
    marks = {"Cambridge": "o", "CINELDI": "s", "HEEW Arizona": "^"}
    wk = np.arange(1, 5)
    bx.axhline(0, color="#7F7F7F", lw=0.6)
    for s_, mk in marks.items():
        rr = [r for r in lw_ if r["set"] == s_]
        bx.plot(wk, [pct(float(r["fixed_division_vs_timesfm_log_ratio"])) for r in rr], color="#9E9E9E", ls=(0, (3, 2)), marker=mk, ms=3.2, mfc="white", lw=0.9)
        bx.plot(wk, [pct(float(r["ankyra_1x_vs_timesfm_log_ratio"])) for r in rr], color=HIST, ls=(0, (1.5, 1.5)), marker=mk, ms=3.0, mfc="white", lw=0.9)
        bx.plot(wk, [pct(float(r["ankyra_vs_timesfm_log_ratio"])) for r in rr], color=ANKYRA, marker=mk, ms=3.4, lw=1.1)
        cx.plot(wk, [float(r["mean_weight_on_model"]) for r in rr], color=FM, marker=mk, ms=3.4, lw=1.0, label=SHORT[s_])
    bx.set_xticks(wk); bx.set_xticklabels([f"W{i}" for i in wk]); bx.set_xlabel("Forecast week", fontsize=6.8)
    bx.set_ylabel("Improvement over TimesFM (%)", fontsize=6.8)
    bx.set_title("c   Lead-week profile vs TimesFM", fontsize=7.6)
    bx.legend(handles=[Line2D([], [], color=ANKYRA, lw=1.1, label="ANKYRA 2.1"), Line2D([], [], color=HIST, ls=(0, (1.5, 1.5)), lw=0.9, label="ANKYRA 1.x"),
                       Line2D([], [], color="#9E9E9E", ls=(0, (3, 2)), lw=0.9, label="fixed division (F0)")],
              loc="lower right", fontsize=5.6, handlelength=1.8, labelspacing=0.25)
    cx.axhline(0.5, color="#BDBDBD", lw=0.6, ls=(0, (2, 2)))
    cx.text(4.15, 0.5, "prior", fontsize=5.5, color="#9E9E9E", va="center")
    cx.set_ylim(0.25, 0.75); cx.set_xticks(wk); cx.set_xticklabels([f"W{i}" for i in wk]); cx.set_xlabel("Forecast week", fontsize=6.8)
    cx.set_ylabel(r"Mean weight on the model  $\alpha_w$", fontsize=6.8)
    cx.set_title("d   Estimated handover", fontsize=7.6)
    cx.legend(fontsize=5.9, loc="upper right", handlelength=1.4)
    fig.text(0.105, 0.985, "a: 2.1 against its reduced versions (shaded: test sets; filled: interval excludes zero). F0, F1 and 1.x lack the within-day anchoring; 2.0.0 and 2.0.1 "
             "estimate its trust per lead block; the micro-load rule acts on BDG2 only and was written after its result was seen.", fontsize=6.2, color=GREY, va="top")
    fig.text(0.105, 0.962, "b, d: the daily-mean handover, unchanged since 1.x, on the populations scored first after it was fixed. c: 2.1 and 1.x against TimesFM by forecast week "
             "on the same populations.", fontsize=6.2, color=GREY, va="top")
    save(fig, "fig4_handover_and_ablation")


# ============================================================================ Figure 5: peak operator
def fig_peak():
    pk = rows("peak_readout.csv"); order = [s_ for s_ in TEST + PREVIEW if any(rr["set"] == s_ for rr in pk)]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True)
    fig.subplots_adjust(left=0.11, right=0.99, top=0.80, bottom=0.17, wspace=0.08)
    y = np.arange(len(order))[::-1]
    for a_, comp, title in ((ax, "trajectory maximum", "a   vs the maximum of the same trajectory"), (bx, "previous-window peak", "b   vs last month's observed peak")):
        a_.axhspan(y[len(TEST) - 1] - 0.5, y[0] + 0.5, color="#F3F6FA", zorder=0)
        a_.axvline(0, color="#7F7F7F", lw=0.6)
        for yy, s in zip(y, order):
            r = next(rr for rr in pk if rr["set"] == s and rr["comparator"] == comp)
            p, lo, hi = float(r["improvement_pct"]), pct(float(r["um_high"])), pct(float(r["um_low"]))
            better, worse = float(r["um_high"]) < 0, float(r["um_low"]) > 0
            col = "#2166AC" if better else (ANKYRA if worse else "#8C8C8C")
            if comp == "trajectory maximum":
                a_.barh(yy, p, color=col, height=0.6, alpha=0.9)
                a_.plot([lo, hi], [yy, yy], color="#262626", lw=0.7)
            else:
                a_.plot([max(lo, -60), min(hi, 40)], [yy, yy], color=col, lw=1.0)
                a_.scatter([p], [yy], s=16, color=col if (better or worse) else "white", edgecolor=col, lw=0.9, zorder=3)
        a_.set_title(title, fontsize=7.6)
        a_.set_xlabel("Improvement in monthly peak error (%)", fontsize=6.8)
    ax.set_yticks(y); ax.set_yticklabels([SHORT[s] for s in order], fontsize=6.4); ax.tick_params(axis="y", length=0)
    for t_, s in zip(ax.get_yticklabels(), order):
        if s in TEST:
            t_.set_fontweight("bold")
    bx.set_xlim(-60, 40)
    fig.text(0.11, 0.985, r"Peak operator  $U=\mathrm{max}_d\,(\hat L_d+A_{\tau_d})$: ANKYRA's daily means plus the largest recent excursion of the same day type.",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.11, 0.935, "Unit-equal improvement in absolute peak error with 95% unit-and-month intervals; test sets shaded. "
             "Blue: better; red: worse; open: not resolved.", fontsize=6.3, color=GREY, va="top")
    save(fig, "fig5_peak_operator")


# ============================================================================ Figure 6: one test window
def fig_example():
    ex = [r for r in rows("example_window_cambridge.csv") if int(r["hour"]) >= -336]      # last two context weeks
    meta = json.loads((RES / "example_window_cambridge.json").read_text(encoding="utf-8"))
    h = np.array([int(r["hour"]) for r in ex]); y = np.array([float(r["load_kw"]) for r in ex])
    tf = np.array([float(r["timesfm_kw"]) if r["timesfm_kw"] else np.nan for r in ex])
    an = np.array([float(r["ankyra_kw"]) if r["ankyra_kw"] else np.nan for r in ex])
    fut = h >= 0
    fig = plt.figure(figsize=(7.2, 3.45))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.35, 1], width_ratios=[1.6, 1], hspace=0.62, wspace=0.22, left=0.075, right=0.99, top=0.9, bottom=0.15)
    ax = fig.add_subplot(gs[0, :])
    ax.axvspan(h[0], 0, color="#F2F2F2", zorder=0)
    ax.plot(h[~fut], y[~fut], color="#7F7F7F", lw=0.55)
    ax.plot(h[fut], y[fut], color="#1A1A1A", lw=0.55, label="observed")
    ax.plot(h[fut], tf[fut], color="#807DBA", lw=0.8, label="TimesFM 2.5")
    ax.plot(h[fut], an[fut], color=ANKYRA, lw=0.8, label="ANKYRA")
    ax.axvline(0, color="#4D4D4D", lw=0.6, ls=(0, (2, 2)))
    ax.text(-6, np.nanmax(y) * 0.99, "context", ha="right", va="top", fontsize=6.2, color="#7F7F7F")
    ax.text(6, np.nanmax(y) * 0.99, "forecast origin", ha="left", va="top", fontsize=6.2, color="#4D4D4D")
    ax.set_xlim(h[0], h[-1]); ax.set_xlabel("Hours from the forecast origin", fontsize=6.8); ax.set_ylabel("kW", fontsize=6.8)
    ax.legend(loc="upper right", ncol=3, fontsize=6.3, bbox_to_anchor=(1.0, 1.2), handlelength=1.6)
    ax.set_title(f"a   {meta['set']} test set · building {meta['building'].split('_')[-1]} · forecast for 1 Sep – 1 Oct 2011", fontsize=7.6, pad=10)
    d = np.arange(1, 32)
    dm = lambda v: v[fut].reshape(31, 24).mean(1)                                   # noqa: E731
    bx = fig.add_subplot(gs[1, 0])
    for v, c, lab_ in ((y, "#1A1A1A", "observed"), (tf, "#807DBA", "TimesFM 2.5"), (an, ANKYRA, "ANKYRA")):
        bx.step(d, dm(v), where="mid", color=c, lw=0.9, label=lab_)
    bx.set_xlim(0.5, 31.5); bx.set_xlabel("Forecast day", fontsize=6.8); bx.set_ylabel("Daily mean (kW)", fontsize=6.8)
    bx.set_title("b   Daily means: level and daily path", fontsize=7.6)
    cx = fig.add_subplot(gs[1, 1])
    wk = [(0, 7), (7, 14), (14, 21), (21, 31)]
    rt = [np.sqrt(np.mean((tf[fut][a * 24:b * 24] - y[fut][a * 24:b * 24]) ** 2)) for a, b in wk]
    ra = [np.sqrt(np.mean((an[fut][a * 24:b * 24] - y[fut][a * 24:b * 24]) ** 2)) for a, b in wk]
    x = np.arange(4)
    cx.bar(x - 0.18, rt, 0.34, color="#807DBA", label="TimesFM 2.5"); cx.bar(x + 0.18, ra, 0.34, color=ANKYRA, label="ANKYRA")
    cx.set_xticks(x); cx.set_xticklabels([f"W{i + 1}" for i in x]); cx.set_ylabel("Hourly RMSE (kW)", fontsize=6.8)
    cx.set_title("c   Error by forecast week", fontsize=7.6); cx.legend(fontsize=6.0, loc="upper left", handlelength=1.2)
    fig.text(0.075, 0.012, "Load rises from its August level during September. TimesFM carries the recent level forward; ANKYRA's history-weighted level "
             "anticipates the rise. Data: University of Cambridge estate archive (CC BY 4.0).", fontsize=5.9, color="#7F7F7F")
    save(fig, "fig6_example_window")


# ============================================================================ Figure 7: exact properties
def fig_operators():
    import sys
    sys.path.insert(0, str(HERE.parent))
    import torch
    from ankyra import blocks, readouts
    from ankyra.history import estimate_from_history
    from theory import operators as op
    from ankyra.synthetic import synthetic_history
    torch.set_num_threads(1)
    ex = rows("example_window_cambridge.csv"); meta = json.loads((RES / "example_window_cambridge.json").read_text(encoding="utf-8"))
    h = np.array([int(r["hour"]) for r in ex]); load = np.array([float(r["load_kw"]) for r in ex])
    fut = h >= 0; y = load[fut]; ctx = load[~fut]
    T = np.array([float(r["timesfm_kw"]) for r in ex if int(r["hour"]) >= 0])
    A = np.array([float(r["ankyra_kw"]) for r in ex if int(r["hour"]) >= 0])
    ct = np.array(meta["context_day_types"])[None]; tt = np.array(meta["target_day_types"])[None]
    exc = readouts.historical_excursions(ctx[None], ct, tt)[0]

    fig = plt.figure(figsize=(7.2, 4.85))
    gs = fig.add_gridspec(2, 3, hspace=0.62, wspace=0.52, left=0.075, right=0.985, top=0.9, bottom=0.095)

    # a  exact accounting of block replacement on the test window (P4)
    ax = fig.add_subplot(gs[0, 0])
    lvA, bpA = blocks.level(A), blocks.daily_path(A)
    arms = [("TimesFM", T), ("+ ANKYRA level", op.replace_blocks(T, level=lvA)),
            ("+ ANKYRA daily path\n(= ANKYRA)", op.replace_blocks(T, level=lvA, daily_path=bpA))]
    cols = ["#C0762A", "#E8B67A", "#807DBA"]; names = ["level", "daily path", "within-day"]
    tot0 = sum(blocks.block_losses(T, y))
    for i, (lab, F) in enumerate(arms):
        parts = blocks.block_losses(F, y); left = 0.0
        for j, v in enumerate(parts):
            ax.barh(i, v, left=left, color=cols[j], height=0.62, label=names[j] if i == 0 else None, lw=0); left += v
        ax.text(left + tot0 * 0.02, i, f"{left:.0f}", va="center", fontsize=6.2)
    ax.set_yticks(range(3)); ax.set_yticklabels([a_[0] for a_ in arms], fontsize=6.1); ax.invert_yaxis()
    ax.set_xlim(0, tot0 * 1.17); ax.set_xlabel("Hourly MSE on the window (kW²)", fontsize=6.6)
    ax.legend(fontsize=5.7, loc="lower right", handlelength=0.9, borderaxespad=0.1)
    ax.set_title("a   Replacement: block losses add", fontsize=7.4)

    # b  historical support (P7)
    bx = fig.add_subplot(gs[0, 1])
    m = np.arange(0, 24 * 760, 6)
    share = np.array([op.data_share(op.effective_pseudo_origins(x)) for x in m])
    bx.step(m / 730.0, share, where="post", color="#4A6FA5", lw=1.1)
    for k in (2, 4, 8, 12):
        mm = 1344 + 744 * k
        bx.plot([mm / 730.0], [op.data_share(k)], "o", ms=2.4, color="#4A6FA5")
        bx.text(mm / 730.0 + 0.35, op.data_share(k) - 0.045, f"K={k}", fontsize=5.6, color="#4A6FA5")
    ya = op.annual_support_hours(2) / 730.0
    bx.axvspan(0, ya, color="#F3F3F3", lw=0, zorder=0)
    bx.axvline(ya, color=GREY, lw=0.6, ls=(0, (2, 2)))
    bx.text(ya + 0.4, 0.13, "annual candidate\nweighted from\n10,248 h (14 mo)", fontsize=5.5, color=GREY, va="bottom")
    bx.text(0.4, 0.66, "equal weights\nbelow 2 errors", fontsize=5.5, color=GREY, va="top")
    bx.set_xlim(0, 24); bx.set_ylim(0, 0.7)
    bx.set_xlabel("History before the origin (months)", fontsize=6.6)
    bx.set_ylabel(r"Data share  $K_{\mathrm{eff}}/(K_{\mathrm{eff}}+8)$", fontsize=6.6)
    bx.set_title("b   Support: how much history", fontsize=7.4)

    # c  shrinkage bounds of the weather weight (P8, P9)
    cx = fig.add_subplot(gs[0, 2])
    ks = np.arange(2, 13); lo = [op.weather_weight_bounds(x)[0] for x in ks]; hi = [op.weather_weight_bounds(x)[1] for x in ks]
    cx.fill_between(ks, lo, hi, color="#EEF3FA", lw=0, label="bound (P8)")
    cx.plot(ks, lo, color="#9DB4D6", lw=0.8); cx.plot(ks, hi, color="#9DB4D6", lw=0.8)
    pts = []
    for hours in (2900, 3700, 4392, 5200, 6000, 6576, 7400, 8200, 9000, 9800, 10600):
        dg = estimate_from_history(synthetic_history(hours), group="Office", temp_sigma_std=0.25).diagnostics
        pts.append((dg["level_k_eff"], dg["weather_weight"]))
    cx.scatter([p_[0] for p_ in pts], [p_[1] for p_ in pts], s=11, color=ANKYRA, zorder=3, lw=0, label="reference estimator")
    cx.scatter([2], [2 / 3], s=16, facecolors="white", edgecolors="#1A1A1A", lw=0.8, zorder=4, label="after deletion (P9)")
    cx.annotate("2/3 > 0.6", (2, 2 / 3), (3.3, 0.9), fontsize=5.6, color="#1A1A1A",
                arrowprops=dict(arrowstyle="-", lw=0.5, color="#1A1A1A"))
    cx.axhline(0.5, color="#BDBDBD", lw=0.6, ls=(0, (2, 2)))
    cx.set_xlabel("Matched error support k", fontsize=6.6); cx.set_ylabel("Total weather weight", fontsize=6.6)
    cx.set_ylim(0, 1); cx.set_xlim(1.5, 12.5); cx.set_xticks([2, 4, 6, 8, 10, 12])
    cx.legend(fontsize=5.5, loc="lower left", handlelength=1.0, borderaxespad=0.1)
    cx.set_title("c   Shrinkage bounds the weights", fontsize=7.4)

    # d  nonnegativity: clipping versus any energy-preserving projection (P10, P11)
    dx = fig.add_subplot(gs[1, 0])
    p0, yt = np.array([-1.0, 3.0]), np.array([0.0, 4.0])
    dx.add_patch(Rectangle((0, 0), 6, 6.1, color="#F4F4F4", lw=0, zorder=0))
    dx.text(5.85, 0.15, "nonnegative\nload", fontsize=5.5, color=GREY, ha="right", va="bottom")
    tline = np.linspace(-1.8, 2.8, 50)
    dx.plot(tline, 2 - tline, color="#7F7F7F", lw=0.7, ls=(0, (3, 2)))
    dx.plot([0, 2], [2, 0], color=FM, lw=2.0, solid_capstyle="butt")
    th = np.linspace(0, 2 * np.pi, 200); r0 = np.sqrt(2)
    dx.plot(yt[0] + r0 * np.cos(th), yt[1] + r0 * np.sin(th), color="#1A1A1A", lw=0.6)
    dx.plot(*p0, "o", color="#1A1A1A", ms=3.2); dx.text(-1.15, 2.78, "forecast", fontsize=5.8, ha="right", va="top")
    dx.plot(*yt, "*", color="#1A1A1A", ms=6); dx.text(0.16, 4.18, "truth", fontsize=5.8)
    dx.plot(0, 3, "o", color=ANKYRA, ms=3.4)
    dx.annotate("clip: error 1", (0.06, 3.0), (1.75, 3.0), fontsize=5.8, color=ANKYRA, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=ANKYRA))
    dx.plot(0, 2, "o", color=FM, ms=3.2)
    dx.annotate("best nonnegative point\nwith the same energy:\nerror 4", (0.06, 2.0), (1.75, 2.05), fontsize=5.8, color=FM,
                va="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=FM))
    dx.text(1.75, 6.05, "the same-energy line is\ntangent to the no-worse\ndisc at the forecast", fontsize=5.5, color=GREY, va="top")
    dx.set_xlim(-2.0, 6.0); dx.set_ylim(-0.3, 6.1); dx.set_aspect("equal")
    dx.axhline(0, color="#BDBDBD", lw=0.5); dx.axvline(0, color="#BDBDBD", lw=0.5)
    dx.set_xlabel("hour 1 (kW)", fontsize=6.6); dx.set_ylabel("hour 2 (kW)", fontsize=6.6)
    dx.set_title("d   Energy: clip, never re-balance", fontsize=7.4)

    # e  the peak operator on the test window (P14)
    ex_ = fig.add_subplot(gs[1, 1])
    L = A.reshape(31, 24).mean(1); U = readouts.peak_readout(A, ctx[None], ct, tt)[0]
    d = np.arange(1, 32)
    ex_.bar(d, L, color="#F3C4C8", width=0.78, lw=0, label=r"daily mean $\hat L_d$")
    ex_.bar(d, exc, bottom=L, color=ANKYRA, width=0.78, lw=0, alpha=0.85, label=r"+ excursion $A_{\tau_d}$")
    ex_.axhline(y.max(), color="#1A1A1A", lw=0.9, ls=(0, (4, 2)), label=f"observed peak {y.max():.0f}")
    ex_.axhline(U, color=ANKYRA, lw=0.9, label=f"peak readout U = {U:.0f}")
    ex_.axhline(A.max(), color="#9E9E9E", lw=0.8, ls=(0, (1, 1.5)), label=f"trajectory max {A.max():.0f}")
    ex_.set_xlim(0.3, 31.7); ex_.set_ylim(0, 262)
    ex_.set_xlabel("Forecast day", fontsize=6.6); ex_.set_ylabel("kW", fontsize=6.6)
    hnd, lab = ex_.get_legend_handles_labels()
    order = [3, 4, 2, 0, 1]
    ex_.legend([hnd[k] for k in order], [lab[k] for k in order], fontsize=5.3, loc="upper left", ncol=2, handlelength=1.3,
               columnspacing=0.7, borderaxespad=0.1, labelspacing=0.3)
    ex_.set_title(r"e   Peak: $U=\mathrm{max}_d(\hat L_d+A_{\tau_d})$", fontsize=7.4)

    # f  the peak error decomposition on the same window (P15)
    fx = fig.add_subplot(gs[1, 2])
    dec = op.peak_error_decomposition(A, y, exc)
    terms = [("level", dec["level"], HIST), ("between-day", dec["between_day"], "#E8B67A"),
             ("amplitude", dec["amplitude"], "#807DBA"), ("selection", dec["selection"], "#9E9E9E")]
    run = 0.0
    for i, (nm, v, c) in enumerate(terms):
        fx.bar(i, v, bottom=run, color=c, width=0.62, lw=0)
        fx.text(i, run + v + (1.2 if v >= 0 else -1.2), f"{v:+.1f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=5.8)
        if i < len(terms) - 1:
            fx.plot([i + 0.31, i + 0.69], [run + v, run + v], color="#7F7F7F", lw=0.5)
        run += v
    fx.bar(4, run, color=ANKYRA, width=0.62, lw=0)
    fx.text(4, run - 1.2, f"{run:+.1f}", ha="center", va="top", fontsize=5.8, color=ANKYRA)
    fx.axhline(0, color="#1A1A1A", lw=0.6)
    fx.set_xticks(range(5)); fx.set_xticklabels([t_[0] for t_ in terms] + ["U − peak"], rotation=35, ha="right", fontsize=6.0)
    cum = np.cumsum([t_[1] for t_ in terms])
    fx.set_ylim(min(0, cum.min()) - 7, max(0, cum.max()) + 7); fx.set_ylabel("kW", fontsize=6.6)
    fx.set_title("f   Peak error: four exact terms", fontsize=7.4)

    fig.text(0.075, 0.985, "a, e, f: the Cambridge test window of Figure 6 (University of Cambridge estate archive, CC BY 4.0). "
             "b–d: exact properties. P-numbers: theory/README.md.",
             fontsize=6.0, color=GREY, va="top")
    save(fig, "fig7_operators")


# ============================================================================ Figure 8: loss metrics of every forecaster
LOSS_SETS = TEST + ["Suzhou park"]
LOSS_METRICS = [("RMSE_kW", "a   RMSE (kW, mean over units)", "kw"), ("MAE_kW", "b   MAE (kW, mean over units)", "kw"),
                ("CV_RMSE_pct", "c   CV(RMSE) (%, median unit)", "pct"), ("WAPE_pct", "d   WAPE (%, median unit)", "pct")]


def _loss_text(v, kind):
    if v >= 1000:                                                            # failed forecasters (GBT-T on EWELD)
        return f"{v:,.0f}"
    if kind == "pct":
        return f"{v:.1f}"
    return f"{v:#.4g}".rstrip(".")


def fig_loss_metrics():
    cm = rows("conventional_metrics_late.csv")
    rk = [r for r in rows("benchmark_mean_unit_rank.csv") if r["subset"] == "late" and r["tier"] == "test"]
    cls = {r["model"]: r["model_class"] for r in cm}
    lab = {r["model"]: r["model_label"] for r in cm}
    mean_rank = {m: np.mean([float(r["mean_unit_rank"]) for r in rk if r["model"] == m]) for m in sorted({r["model"] for r in rk})}
    models = sorted(sorted(mean_rank), key=lambda m: mean_rank[m])                 # the order of figure 2
    n, ns = len(models), len(LOSS_SETS)
    cmap = LinearSegmentedColormap.from_list("rel", [ANKYRA, "#F4A582", "#F7F7F7", "#92C5DE", "#2166AC"])
    lim = 30.0
    fig = plt.figure(figsize=(7.2, 8.4))
    gs = fig.add_gridspec(2, 2, left=0.175, right=0.99, top=0.885, bottom=0.105, wspace=0.05, hspace=0.13)
    ia = models.index("ANKYRA")
    for k, (col, title, kind) in enumerate(LOSS_METRICS):
        ax = fig.add_subplot(gs[k // 2, k % 2])
        V = np.array([[next(float(r[col]) for r in cm if r["set"] == s and r["model"] == m) for s in LOSS_SETS] for m in models])
        rel = 100.0 * (V / V[ia] - 1.0)                                         # loss relative to ANKYRA in the same column
        ax.imshow(np.clip(rel, -lim, lim), cmap=cmap, vmin=-lim, vmax=lim, aspect="auto", interpolation="nearest")
        best = V.argmin(0)
        for i in range(n):
            for j in range(ns):
                ax.text(j, i, _loss_text(V[i, j], kind), ha="center", va="center", fontsize=5.0,
                        color="white" if abs(rel[i, j]) > 21 else "#1A1A1A", fontweight="bold" if best[j] == i else "normal")
        ax.axvline(len(TEST) - 0.5, color="white", lw=2.4)
        ax.add_patch(Rectangle((-0.5, ia - 0.5), ns, 1, fill=False, ec=ANKYRA, lw=1.3, zorder=6))
        ax.set_xticks(range(ns))
        ax.set_xticklabels([TWO_LINE.get(s, SHORT[s]).replace("Suzhou park", "Suzhou\npark*") for s in LOSS_SETS], fontsize=5.9,
                           linespacing=1.0)
        ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=1.5)
        ax.set_yticks(range(n)); ax.tick_params(axis="y", length=0, pad=8)
        if k % 2 == 0:
            ax.set_yticklabels([label(lab[m]) for m in models], fontsize=6.2)
            for t_, m in zip(ax.get_yticklabels(), models):
                if m == "ANKYRA":
                    t_.set_color(ANKYRA); t_.set_fontweight("bold")
            for i, m in enumerate(models):
                c = ANKYRA if m == "ANKYRA" else CLASS_COLOR.get(cls.get(m, ""), "#9E9E9E")
                ax.scatter([-0.8], [i], s=10, color=c, clip_on=False, marker="s", zorder=5)
        else:
            ax.set_yticklabels([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, fontsize=7.4, pad=17)
    cax = fig.add_axes([0.30, 0.058, 0.40, 0.011])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(-lim, lim), cmap=cmap), cax=cax, orientation="horizontal")
    cb.set_ticks([-30, -15, 0, 15, 30]); cb.set_ticklabels(["≤ −30", "−15", "0", "+15", "≥ +30"]); cb.ax.tick_params(labelsize=5.8, length=2)
    cb.outline.set_linewidth(0.4)
    cb.set_label("Loss relative to ANKYRA in the same column (%): red lower than ANKYRA, blue higher", fontsize=6.0, labelpad=2)
    handles = [Line2D([], [], marker="s", ls="", color=c, markersize=4.0, label=t_) for t_, c in CLASS_LEGEND]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.01, -0.005), ncol=4, fontsize=5.7, handletextpad=0.25,
               columnspacing=0.9)
    fig.text(0.01, 0.992, "21 forecasters on the same late windows (origins after each set's training cutoff): the six test sets and the Suzhou",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.972, "industrial park. a, b: means over units, so larger units weigh more; c, d: the median unit. Bold: lowest in the column.",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.952, "* Preview population with four aggregate series; read its values as point values. Rows in the order of figure 2.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig8_loss_metrics")


# ============================================================================ Figure 9: hourly loss by forecast day; Figure 9b: energy to date
DAY_LINES = [("TimesFM", "#807DBA", "-"), ("Chronos-2", "#807DBA", "--"), ("Chronos-2-X", "#1D91C0", "-"),
             ("TimesFM-X", "#1D91C0", "--"), ("TiDE", "#253494", "-"), ("iTransformer-X", "#253494", "--"),
             ("GBT-T", "#253494", ":"), ("RIDGE-L", "#8C6D31", "-")]


EXTRA_SETS = [("lcl_by_day.csv", "LCL households"), ("hkust_by_day.csv", "HKUST campus\u2020"), ("helsinki_by_day.csv", "Helsinki\u2020"),
              ("unicon_by_day.csv", "UNICON campuses\u2021")]


def _day_panels(csv_name, value_col, extra_col):
    """(title, curves, labels, number of forecasters) for the seven late-window populations and the two frozen-check populations."""
    ld = rows(csv_name); lab = {r["model"]: r["model_label"] for r in ld}; out = []
    for s in LOSS_SETS:
        R = [r for r in ld if r["set"] == s]
        curve = {m: np.array([float(r[value_col]) for r in sorted((r for r in R if r["model"] == m), key=lambda r: int(r["day"]))])
                 for m in sorted({r["model"] for r in R})}
        n = R[0]["n_units_gm"] if "n_units_gm" in R[0] else R[0]["units_in_U"]
        out.append(({"Suzhou park": "Suzhou park* (4 series)"}.get(s, f"{s.replace(' 2017', '')} ({n} units)"), curve, lab, 21))
    for f, name in EXTRA_SETS:
        if not (RES / f).exists():
            continue
        R = rows(f); lab2 = {r["model"]: r["model_label"] for r in R}
        curve = {m: np.array([float(r[extra_col]) for r in sorted((r for r in R if r["model"] == m), key=lambda r: int(r["day"]))])
                 for m in sorted({r["model"] for r in R})}
        out.append((f"{name} ({R[0]['units_in_fixed_set']} units)", curve, {**lab, **lab2}, len(curve)))
    return out


def _day_figure(panels, ylabel, energy, stem, caption):
    days = np.arange(1, 32)
    nrow = (len(panels) + 2) // 2
    fig, axs = plt.subplots(nrow, 2, figsize=(7.2, 2.2 * nrow + 0.4))
    fig.subplots_adjust(left=0.085, right=0.985, top=1 - 0.95 / (2.2 * nrow + 0.4), bottom=0.04, hspace=0.45, wspace=0.17)
    flat = axs.ravel()
    for ax, (title, curve, lab, nf) in zip(flat, panels):
        top = (2.4 * curve["ANKYRA"][6:].max()) if energy else 1.6 * curve["ANKYRA"].max()
        low = 0 if energy else 0.88 * min(v.min() for v in curve.values())
        named = {"ANKYRA"} | {m for m, *_ in DAY_LINES}
        for m, v in curve.items():
            if m not in named:
                ax.plot(days, np.minimum(v, top * 1.2), color="#D0D0D0", lw=0.55, zorder=1)
        off = []
        for m, c, ls in DAY_LINES:
            if m not in curve:
                continue
            v = curve[m]
            if np.median(v) > top:
                off.append(label(lab[m])); continue
            ax.plot(days, v, color=c, ls=ls, lw=0.95, zorder=2)
        ax.plot(days, curve["ANKYRA"], color=ANKYRA, lw=1.9, zorder=3)
        for x in (7.5, 14.5, 21.5):
            ax.axvline(x, color="#E6E6E6", lw=0.5, zorder=0)
        ax.set_xlim(1, 31); ax.set_ylim(low, top); ax.set_xticks([1, 7, 14, 21, 28, 31])
        ax.set_title(title, fontsize=7.2)
        if energy:
            lowest = int(sum(all(curve["ANKYRA"][d] <= v[d] for v in curve.values()) for d in range(31)))
            ax.text(0.985, 0.04, f"ANKYRA lowest of {nf} on {lowest} of 31 days", transform=ax.transAxes, ha="right", va="bottom", fontsize=5.8, color=ANKYRA)
        if off:
            ax.text(0.985, 0.97, "off scale: " + ", ".join(off), transform=ax.transAxes, ha="right", va="top", fontsize=5.6, color=GREY)
        ax.grid(axis="y", color="#EFEFEF", lw=0.4, zorder=0)
    for ax in axs[:, 0]:
        ax.set_ylabel(ylabel, fontsize=6.6)
    for k, ax in enumerate(flat[:len(panels)]):
        if k >= len(panels) - 2:
            ax.set_xlabel("Forecast day", fontsize=6.8)
    lg = flat[len(panels)]; lg.axis("off")
    for ax in flat[len(panels) + 1:]:
        ax.axis("off")
    lab = panels[0][2]
    handles = [Line2D([], [], color=ANKYRA, lw=1.9, label="ANKYRA")]
    handles += [Line2D([], [], color=c, ls=ls, lw=0.95, label=label(lab[m])) for m, c, ls in DAY_LINES]
    handles += [Line2D([], [], color="#D0D0D0", lw=0.8, label="the other baselines")]
    lg.legend(handles=handles, loc="center", ncol=2, fontsize=6.4, handlelength=2.4, columnspacing=1.2, labelspacing=0.7)
    h = 2.2 * nrow + 0.4
    for j, line in enumerate(caption):
        fig.text(0.01, 1 - (0.08 + 0.17 * j) / h, line, fontsize=6.3, color=GREY, va="top")
    save(fig, stem)


DAGGER = ("LCL: 21 forecasters on its 710 common late windows. \u2020 HKUST, Helsinki: 14 forecasters (no trained baselines), the windows where "
          "the ridge is defined. \u2021 UNICON: external test of the frozen ANKYRA 2.1, 14 forecasters.")


def fig_lead_days():
    _day_figure(_day_panels("lead_day_metrics.csv", "GM_CV_RMSE_pct", "hourly_gm_cv_pct"), "CV(RMSE) of the day (%)", False, "fig9_loss_by_day",
                ["Loss by forecast day, 21 forecasters on the same late windows (origins after each set's training cutoff). For each unit,",
                 "the day's CV(RMSE) is the RMSE of that day's 24 hours over the unit's mean load; curves are geometric means over one fixed set",
                 "of units (all daily errors nonzero), the scale of the primary estimand. Vertical lines: week boundaries. * Preview population.",
                 DAGGER])


def fig_energy_by_day():
    """Figure 9b: error of the energy delivered through each forecast day (the quantity ANKYRA's level and daily path act on)."""
    _day_figure(_day_panels("lead_day_energy.csv", "GM_CV_cumulative_energy_pct", "energy_to_date_gm_cv_pct"), "Error of energy to date, CV (%)", True,
                "fig9b_energy_by_day",
                ["Error of the energy delivered through each forecast day, 21 forecasters on the same late windows. For each unit and day d, the RMS over the unit's",
                 "windows of the error of the mean load over days 1..d, divided by the unit's mean load; curves are geometric means over one fixed set of units, the",
                 "aggregation of figure 9 applied to energy instead of hourly load. Day 31 is the monthly energy error of figure 11. Computed after scoring. * Preview population.",
                 DAGGER])


def fig_lead_days_relative():
    ld = rows("lead_day_metrics.csv")
    lab = {r["model"]: r["model_label"] for r in ld}
    days = np.arange(1, 32)
    fig, axs = plt.subplots(4, 2, figsize=(7.2, 9.0), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.905, bottom=0.045, hspace=0.36, wspace=0.17)
    for ax, s in zip(axs.ravel(), LOSS_SETS):
        R = [r for r in ld if r["set"] == s]
        curve = {m: np.array([float(r["GM_CV_RMSE_pct"]) for r in sorted((r for r in R if r["model"] == m), key=lambda r: int(r["day"]))])
                 for m in sorted({r["model"] for r in R})}
        rels, off = {}, []
        for m, c, ls in DAY_LINES:
            rel = 100.0 * (curve[m] / curve["ANKYRA"] - 1.0)             # the baseline's loss relative to ANKYRA's, day by day
            if np.median(rel) > 60:
                off.append(label(lab[m])); continue
            rels[m] = rel
        vals = np.concatenate(list(rels.values()))
        lo, hi = min(-5.0, 5 * np.floor((vals.min() - 2) / 5)), max(5.0, 5 * np.ceil((vals.max() + 2) / 5))   # each panel on its own scale
        ax.axhspan(0, hi, color="#F3F6FA", zorder=0)
        ax.axhline(0, color=ANKYRA, lw=1.3, zorder=3)
        ax.text(30.6, 0, "ANKYRA = 0", color=ANKYRA, fontsize=5.8, ha="right", va="bottom", zorder=1)   # under the lines
        for m, c, ls in DAY_LINES:
            if m in rels:
                ax.plot(days, rels[m], color=c, ls=ls, lw=1.0, zorder=2)
        for x in (7.5, 14.5, 21.5):
            ax.axvline(x, color="#E6E6E6", lw=0.5, zorder=1)
        ax.set_xlim(1, 31); ax.set_ylim(lo, hi); ax.set_xticks([1, 7, 14, 21, 28, 31])
        title = {"Suzhou park": "Suzhou park* (4 series)"}.get(s, f"{s.replace(' 2017', '')} ({R[0]['n_units_gm']} units)")
        ax.set_title(title, fontsize=7.2)
        ax.text(0.015, 0.965, "baseline worse than ANKYRA", transform=ax.transAxes, fontsize=5.5, color=GREY, va="top")
        ax.text(0.015, 0.035, "baseline better than ANKYRA", transform=ax.transAxes, fontsize=5.5, color=GREY, va="bottom")
        if off:
            ax.text(0.985, 0.965, "off scale: " + ", ".join(off), transform=ax.transAxes, ha="right", va="top", fontsize=5.6, color=GREY)
        ax.grid(axis="y", color="#EFEFEF", lw=0.4, zorder=0)
    for ax in axs[:, 0]:
        ax.set_ylabel("Loss relative to ANKYRA (%)", fontsize=6.6)
    for ax in (axs[3, 0], axs[2, 1]):
        ax.set_xlabel("Forecast day", fontsize=6.8)
    axs[2, 1].tick_params(axis="x", labelbottom=True)
    lg = axs[3, 1]; lg.axis("off")
    handles = [Line2D([], [], color=ANKYRA, lw=1.3, label="ANKYRA: the reference, 0 by definition")]
    handles += [Line2D([], [], color=c, ls=ls, lw=1.0, label=label(lab[m])) for m, c, ls in DAY_LINES]
    lg.legend(handles=handles, loc="center", ncol=2, fontsize=6.4, handlelength=2.4, columnspacing=1.2, labelspacing=0.7)
    fig.text(0.01, 0.992, "Each baseline's loss relative to ANKYRA's on the same day, 100 (CV_model / CV_ANKYRA − 1), from the curves of figure 9. ANKYRA is the",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.974, "zero line by definition; its own loss, rising with the forecast day, is in figure 9. Above zero the baseline has the larger loss. Each panel",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.956, "has its own vertical scale. Over the whole month the comparison differs, because the monthly RMS weights days with large errors more.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig10_loss_by_day_relative")


# ============================================================================ Figure 11: monthly energy error
ENERGY_COLS = [("BDG2 2017", "all units", "BDG2 †"), ("BDG2 2017", "without the three near-zero meters", "BDG2\nw/o 3"),
               ("Cambridge", "all units", "Cambridge"), ("HEEW Arizona", "all units", "HEEW"), ("EWELD", "all units", "EWELD"),
               ("GoiEner non-household", "all units", "GoiEner\nNH"), ("GoiEner households", "all units", "GoiEner\nHH"),
               ("Suzhou park", "all units", "Suzhou\npark ‡")]


def fig_energy():
    en = rows("energy_error.csv")
    rk = [r for r in rows("benchmark_mean_unit_rank.csv") if r["subset"] == "late" and r["tier"] == "test"]
    mean_rank = {m: np.mean([float(r["mean_unit_rank"]) for r in rk if r["model"] == m]) for m in sorted({r["model"] for r in rk})}
    models = [m for m in sorted(sorted(mean_rank), key=lambda m: mean_rank[m]) if m != "ANKYRA"]      # figure 2 order
    lab = {r["model"]: r["model_label"] for r in en}
    cls = {r["model"]: r["model_class"] for r in en}
    cell = {(r["set"], r["unit_set"], r["model"]): r for r in en}
    n, k = len(models), len(ENERGY_COLS)
    P = np.array([[float(cell[(s, sub, m)]["improvement_pct"]) for s, sub, _ in ENERGY_COLS] for m in models])
    fig = plt.figure(figsize=(7.2, 4.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.8, 0.85], wspace=0.42, left=0.16, right=0.985, top=0.80, bottom=0.16)
    ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1], sharey=ax)
    cmap = LinearSegmentedColormap.from_list("energy", [ANKYRA, "#F4A582", "#F7F7F7", "#92C5DE", "#2166AC"])
    ax.imshow(np.clip(P, -50, 50), cmap=cmap, vmin=-50, vmax=50, aspect="auto", interpolation="nearest")
    for i, m in enumerate(models):
        for j, (s, sub, _) in enumerate(ENERGY_COLS):
            r = cell[(s, sub, m)]
            tag = "*" if float(r["um_high"]) < 0 else ("(+)" if float(r["um_low"]) > 0 else "")
            v = P[i, j]
            ax.text(j, i, f"{v:+.0f}{tag}" if abs(v) < 999.5 else f"{v:+,.0f}{tag}", ha="center", va="center", fontsize=5.2,
                    color="white" if abs(v) > 35 else "#1A1A1A", fontweight="bold" if tag == "*" else "normal")
    ax.axvline(1.5, color="white", lw=2.4); ax.axvline(k - 1.5, color="white", lw=2.4)
    ax.set_xticks(range(k)); ax.set_xticklabels([c[2] for c in ENERGY_COLS], fontsize=5.9, linespacing=1.0)
    ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=2)
    ax.set_yticks(range(n)); ax.set_yticklabels([label(lab[m]) for m in models], fontsize=6.3); ax.tick_params(axis="y", length=0, pad=8)
    for i, m in enumerate(models):
        ax.scatter([-0.8], [i], s=10, color=CLASS_COLOR.get(cls.get(m, ""), "#9E9E9E"), clip_on=False, marker="s", zorder=5)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("a   ANKYRA's improvement in monthly energy error over each baseline (%)", fontsize=7.4, pad=24)
    cols = [c for c in ENERGY_COLS if c[1] == "all units"]
    better = np.array([sum(float(cell[(s, sub, m)]["um_high"]) < 0 for m in models) for s, sub, _ in cols])
    worse = np.array([sum(float(cell[(s, sub, m)]["um_low"]) > 0 for m in models) for s, sub, _ in cols])
    tie = len(models) - better - worse
    bx.remove(); bx = fig.add_subplot(gs[1])
    y = np.arange(len(cols))
    bx.barh(y, better, color="#2166AC", height=0.62); bx.barh(y, tie, left=better, color="#D9D9D9", height=0.62)
    bx.barh(y, worse, left=better + tie, color=ANKYRA, height=0.62)
    for i in range(len(cols)):
        bx.text(better[i] - 0.3, i, f"{better[i]}", va="center", ha="right", fontsize=6.0, color="white", fontweight="bold")
    bx.set_yticks(y); bx.set_yticklabels([c[2].replace("\n", " ") for c in cols], fontsize=6.3); bx.invert_yaxis()
    bx.set_xlim(0, len(models)); bx.set_xticks([0, 5, 10, 15, 20]); bx.set_xlabel("Number of the 20 baselines", fontsize=6.8)
    bx.set_title("b   Head-to-head on energy", fontsize=7.4, pad=24)
    bx.legend(handles=[Patch(fc="#2166AC", label="ANKYRA better"), Patch(fc="#D9D9D9", label="not resolved"),
                       Patch(fc=ANKYRA, label="ANKYRA worse")], loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=3,
              fontsize=5.8, handlelength=1.0, handleheight=0.8, columnspacing=0.7, handletextpad=0.3)
    handles = [Line2D([], [], marker="s", ls="", color=c, markersize=4.0, label=t_) for t_, c in CLASS_LEGEND]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=4, fontsize=5.8, handletextpad=0.25, columnspacing=0.9)
    fig.text(0.01, 0.99, "Monthly energy error, 744 × the mean hourly error (P3), on the same late windows. Unit-equal RMS ratio with 95% unit-and-month",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.967, "bootstrap intervals; * resolved in ANKYRA's favour, (+) against it. Computed after scoring. † BDG2 includes the micro-load rule (since 2.0.1), written",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.944, "after its result was seen; three near-zero meters still dominate its unit means and the next column leaves them out. ‡ Suzhou park: preview, four series.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig11_energy_error")


# ============================================================================ Figure 12: position on every population
def fig_consistency():
    rk = [r for r in rows("benchmark_mean_unit_rank.csv") if r["subset"] == "late" and r["tier"] in ("test", "preview")]
    lab = {r["model"]: r["model_label"] for r in rk}
    cls = {r["model"]: r["model_class"] for r in rows("benchmark_pairwise.csv")}
    pos = {}
    for s in TEST + PREVIEW:
        order = sorted((r for r in rk if r["set"] == s), key=lambda r: float(r["mean_unit_rank"]))
        assert len(order) == 21, s
        for i, r in enumerate(order):
            pos.setdefault(r["model"], {})[s] = i + 1
    models = sorted(pos, key=lambda m: (np.mean([pos[m][s] for s in TEST]), m))
    fig, ax = plt.subplots(figsize=(7.2, 4.9))
    fig.subplots_adjust(left=0.2, right=0.985, top=0.86, bottom=0.1)
    for i, m in enumerate(models):
        c = ANKYRA if m == "ANKYRA" else CLASS_COLOR.get(cls.get(m, ""), "#9E9E9E")
        t = [pos[m][s] for s in TEST]; p = [pos[m][s] for s in PREVIEW]
        ax.plot([min(t), max(t)], [i, i], color=c, lw=2.2 if m == "ANKYRA" else 1.2, alpha=0.35, solid_capstyle="round", zorder=1)
        ax.scatter(t, [i - 0.13] * len(t), s=26 if m == "ANKYRA" else 16, color=c, zorder=3, lw=0)
        ax.scatter(p, [i + 0.17] * len(p), s=22 if m == "ANKYRA" else 14, facecolor="white", edgecolor=c, lw=0.9, zorder=3)
    ax.set_yticks(range(len(models))); ax.set_yticklabels([label(lab[m]) for m in models], fontsize=6.5)
    for t_, m in zip(ax.get_yticklabels(), models):
        if m == "ANKYRA":
            t_.set_color(ANKYRA); t_.set_fontweight("bold")
    ax.set_ylim(len(models) - 0.5, -0.6)
    ax.set_xlim(0.5, 21.5); ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21])
    ax.set_xlabel("Position among the 21 forecasters (1 = lowest mean per-unit rank)", fontsize=6.9)
    ax.grid(axis="x", color="#EFEFEF", lw=0.5, zorder=0)
    ax.axvspan(0.5, 2.5, color="#F3F6FA", zorder=0)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=GREY, markersize=4.5, label="test population"),
                       Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=GREY, markersize=4.5,
                              label="preview population"),
                       Line2D([], [], color=GREY, lw=1.6, alpha=0.4, label="range over the six test populations")],
              loc="upper right", fontsize=6.2, handletextpad=0.3, frameon=True, facecolor="white", edgecolor="#DDDDDD")
    fig.text(0.01, 0.985, "Where each forecaster lands on each population, late windows (all 21 forecasters on the same windows). ANKYRA is first or",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.962, "second on all six test populations; no other forecaster is in the top two on more than two of them. The position uses the mean",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.939, "per-unit rank, a secondary summary; the primary estimand is in the test table and figure 3. Rows: mean position on the test populations.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig12_consistency")


# ============================================================================ Figure 13: intervals on households
def fig_intervals():
    iv = json.loads((RES / "intervals_households.json").read_text(encoding="utf-8"))
    arms = [("ours_around_ANKYRA", "ANKYRA interval", ANKYRA), ("ours_around_F0", "same interval,\nfixed division", HIST),
            ("chronos_native", "Chronos-2\nnative", "#807DBA"), ("timesfm_native", "TimesFM\nnative 0.1–0.9", "#5E4FA2")]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw={"width_ratios": [1.35, 1.0], "wspace": 0.32})
    fig.subplots_adjust(left=0.075, right=0.985, top=0.78, bottom=0.2)
    x = np.arange(len(arms)); w = 0.36
    for j, (key, name, c) in enumerate(arms):
        a = iv["arms"][key]
        ax.bar(j - w / 2, 100 * a["cov80"], width=w, color=c, alpha=0.95)
        ax.text(j - w / 2, 100 * a["cov80"] + 1.5, f"{100 * a['cov80']:.1f}", ha="center", fontsize=5.8)
        if "cov90" in a:
            ax.bar(j + w / 2, 100 * a["cov90"], width=w, color=c, alpha=0.45)
            ax.text(j + w / 2, 100 * a["cov90"] + 1.5, f"{100 * a['cov90']:.1f}", ha="center", fontsize=5.8)
        else:
            ax.text(j + w / 2, 3, "n/a", ha="center", fontsize=5.6, color=GREY)
    ax.axhline(80, color="#1A1A1A", lw=0.7, ls="--"); ax.axhline(90, color="#1A1A1A", lw=0.7, ls=":")
    ax.text(3.62, 80.5, "nominal 80%", fontsize=5.6, ha="right", va="bottom"); ax.text(3.62, 90.5, "nominal 90%", fontsize=5.6, ha="right", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels([a[1] for a in arms], fontsize=6.0); ax.set_ylim(0, 100); ax.set_ylabel("Coverage of hours (%)", fontsize=6.6)
    ax.set_title("a   Coverage (dark: 80% band, light: 90% band)", fontsize=7.2)
    wk = [iv["arms"][k]["winkler80"] for k, *_ in arms]
    bx.bar(x, wk, color=[a[2] for a in arms], width=0.6)
    notes = {"ours_around_F0": "winkler80_oursANKYRA_vs_ours_around_F0", "chronos_native": "winkler80_oursANKYRA_vs_chronos_native",
             "timesfm_native": "winkler80_oursANKYRA_vs_timesfm_native"}
    for j, (key, *_rest) in enumerate(arms):
        bx.text(j, wk[j] + 0.012, f"{wk[j]:.3f}", ha="center", fontsize=5.8)
        if key in notes:
            c = iv["contrasts"][notes[key]]
            tag = "*" if c["UM"][1] < 0 else ("(+)" if c["UM"][0] > 0 else "")
            bx.text(j, 0.03, f"ANKYRA\n{c['pct']:+.1f}%{tag}", ha="center", fontsize=5.4, color="white", fontweight="bold")
    bx.set_xticks(x); bx.set_xticklabels([a[1] for a in arms], fontsize=6.0); bx.set_ylabel("Winkler score, 80% (kW)", fontsize=6.6)
    bx.set_ylim(0, max(wk) * 1.18)
    bx.set_title("b   Winkler score (lower is better)", fontsize=7.2)
    fig.text(0.01, 0.985, f"Prediction intervals on GoiEner households ({iv['units']:,} units, {iv['windows']:,} windows), the one population where intervals were scored.",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.93, "b: ANKYRA's improvement in the unit-equal Winkler score over each interval; * 95% unit-and-month interval excludes zero.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig13_intervals")


# ============================================================================ Figure 14: where the error sits (block attribution)
def fig_block_shares():
    bs = rows("block_shares.csv")
    sets = []
    for r in bs:
        if r["set"] not in sets:
            sets.append(r["set"])
    arms = [("ANKYRA", "ANKYRA 2.1", ANKYRA), ("ANKYRA 1.x", "ANKYRA 1.x", HIST), ("TimesFM", "TimesFM", FM)]
    blocks = [("level", "level", "#1A1A1A"), ("daily path", "daily path", "#7F7F7F"), ("within-day", "within-day", "#D9D9D9")]
    val = {(r["set"], r["model"], r["quantity"], r["block"]): float(r["value"]) for r in bs}
    fig = plt.figure(figsize=(7.2, 4.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.36, left=0.085, right=0.985, top=0.80, bottom=0.17)
    ax = fig.add_subplot(gs[0]); bx = fig.add_subplot(gs[1])
    x = np.arange(len(sets)); w = 0.26
    for j, (key, name, col) in enumerate(arms):
        left = np.zeros(len(sets))
        for k, (blk, _, shade) in enumerate(blocks):
            v = np.array([100 * val[(s, key, "median_unit_share", blk)] for s in sets])
            ax.bar(x + (j - 1) * w, v, bottom=left, width=w * 0.92, color=col, alpha=[1.0, 0.62, 0.3][k], edgecolor="white", lw=0.4)
            if k == 2:
                for i in range(len(sets)):
                    ax.text(x[i] + (j - 1) * w, left[i] + v[i] / 2, f"{v[i]:.0f}", ha="center", va="center", fontsize=5.0, color="#1A1A1A")
            left += v
    ax.set_xticks(x); ax.set_xticklabels([SHORT[s] for s in sets], fontsize=6.2, rotation=25, ha="right")
    ax.set_ylim(0, 118); ax.set_yticks([0, 20, 40, 60, 80, 100]); ax.set_ylabel("Share of the median unit's hourly squared error (%)", fontsize=6.6)
    ax.set_title("a   Which block carries the error", fontsize=7.2)
    ax.legend(handles=[Patch(fc=c, label=n) for _, n, c in arms] + [Patch(fc="#7F7F7F", alpha=a, label=f"{n} block") for (_, n, _), a in zip(blocks, [1.0, 0.62, 0.3])],
              loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=3, fontsize=5.6, handlelength=1.0, handleheight=0.8, columnspacing=0.8, frameon=False)
    # b: ANKYRA's improvement over TimesFM by block
    y = np.arange(len(sets))[::-1]; h = 0.2
    for k, (blk, name, shade) in enumerate(blocks + [("hourly", "hourly total", ANKYRA)]):
        v = np.array([val[(s, "ANKYRA vs TimesFM", "improvement_pct", blk)] for s in sets])
        bx.barh(y + (1.5 - k) * h, np.clip(v, -60, 60), height=h * 0.9, color=shade if blk != "hourly" else ANKYRA, alpha=1.0 if blk == "hourly" else 0.85)
        for i in range(len(sets)):
            if abs(v[i]) > 60:
                bx.text(np.sign(v[i]) * 61, y[i] + (1.5 - k) * h, f"{v[i]:+.0f}", fontsize=4.8, va="center", ha="left" if v[i] > 0 else "right")
    bx.axvline(0, color="#7F7F7F", lw=0.6)
    bx.set_yticks(y); bx.set_yticklabels([SHORT[s] for s in sets], fontsize=6.2); bx.tick_params(axis="y", length=0)
    bx.set_xlim(-65, 65); bx.set_xlabel("ANKYRA 2.1 improvement over TimesFM by block (%)", fontsize=6.6)
    bx.set_title("b   Where the gain over TimesFM comes from", fontsize=7.2)
    bx.legend(handles=[Patch(fc=c, label=n) for _, n, c in blocks] + [Patch(fc=ANKYRA, label="hourly total")], loc="lower right", fontsize=5.6,
              handlelength=1.0, handleheight=0.8, framealpha=0.9)
    fig.text(0.01, 0.985, "Block attribution on the late windows of the six test populations and the Suzhou park (the windows of Figures 8–11). The three blocks are orthogonal (P1),",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.962, "so a forecast's hourly MSE is the sum of its level, daily-path and within-day MSE. a: the median over units of each block's share (bars: ANKYRA 2.1, 1.x,",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.939, "TimesFM; medians of three shares need not add to 100). b: unit-equal RMS improvement of ANKYRA 2.1 over TimesFM in each block; BDG2 includes the",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.916, "micro-load rule, written after its result was seen. Descriptive, computed after scoring.", fontsize=6.3, color=GREY, va="top")
    save(fig, "fig14_block_attribution")


# ============================================================================ Figure 15: rank significance (Friedman / Nemenyi / Wilcoxon-Holm)
def fig_rank_tests():
    rt = rows("rank_tests.csv")
    panels = [("six test populations pooled", "a   Six test populations pooled")] + [(s, None) for s in TEST]
    fig = plt.figure(figsize=(7.2, 6.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.5, left=0.17, right=0.985, top=0.86, bottom=0.085)
    ax = fig.add_subplot(gs[0])
    R = sorted([r for r in rt if r["set"] == "six test populations pooled"], key=lambda r: float(r["mean_rank"]))
    y = np.arange(len(R))[::-1]; cd = float(R[0]["nemenyi_cd"]); a_rank = float(next(r["mean_rank"] for r in R if r["model"] == "ANKYRA"))
    ax.axvspan(a_rank, a_rank + cd, color="#F6E3E5", zorder=0)
    for yy, r in zip(y, R):
        me = r["model"] == "ANKYRA"; sig = me or float(r["wilcoxon_holm_p_vs_ankyra"]) < 0.05
        ax.scatter([float(r["mean_rank"])], [yy], s=22 if me else 14, color=ANKYRA if me else ("#4D4D4D" if sig else "white"), edgecolor=ANKYRA if me else "#4D4D4D", lw=0.8, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([label(r["model_label"]) for r in R], fontsize=6.2)
    for t_, r in zip(ax.get_yticklabels(), R):
        if r["model"] == "ANKYRA":
            t_.set_color(ANKYRA); t_.set_fontweight("bold")
    ax.set_xlabel("Mean per-unit rank among 21 forecasters (lower is better)", fontsize=6.6); ax.tick_params(axis="y", length=0)
    ax.set_title(f"a   Six test populations pooled ({R[0]['units']} units)", fontsize=7.2)
    ax.text(a_rank + cd / 2, y[0] + 0.75, f"Nemenyi CD = {cd:.2f}", fontsize=5.8, color=ANKYRA, ha="center", va="bottom")
    ax.set_ylim(y[-1] - 0.7, y[0] + 1.4); ax.grid(axis="x", color="#EFEFEF", lw=0.4, zorder=0)
    bx = fig.add_subplot(gs[1])
    sets = TEST + PREVIEW; yy = np.arange(len(sets))[::-1]
    for y_, s_ in zip(yy, sets):
        Rs = [r for r in rt if r["set"] == s_]; n = len(Rs) - 1
        better = sum(1 for r in Rs if r["model"] != "ANKYRA" and float(r["wilcoxon_holm_p_vs_ankyra"]) < 0.05 and float(r["mean_rank"]) > float(next(x["mean_rank"] for x in Rs if x["model"] == "ANKYRA")))
        worse = sum(1 for r in Rs if r["model"] != "ANKYRA" and float(r["wilcoxon_holm_p_vs_ankyra"]) < 0.05 and float(r["mean_rank"]) < float(next(x["mean_rank"] for x in Rs if x["model"] == "ANKYRA")))
        bx.barh(y_, better, color="#2166AC", height=0.62); bx.barh(y_, n - better - worse, left=better, color="#D9D9D9", height=0.62); bx.barh(y_, worse, left=n - worse, color=ANKYRA, height=0.62)
        bx.text(better - 0.3, y_, f"{better}", va="center", ha="right", fontsize=6.0, color="white", fontweight="bold")
        if worse:
            bx.text(n + 0.3, y_, next(label(r["model_label"]) for r in Rs if r["model"] != "ANKYRA" and float(r["wilcoxon_holm_p_vs_ankyra"]) < 0.05
                                       and float(r["mean_rank"]) < float(next(x["mean_rank"] for x in Rs if x["model"] == "ANKYRA"))), va="center", ha="left", fontsize=5.6, color=ANKYRA)
    bx.set_yticks(yy); bx.set_yticklabels([SHORT[s_] for s_ in sets], fontsize=6.4)
    for t_, s_ in zip(bx.get_yticklabels(), sets):
        t_.set_fontweight("bold" if s_ in TEST else "normal")
    bx.set_xlim(0, 26); bx.set_xticks([0, 5, 10, 15, 20]); bx.set_xlabel("Number of the 20 baselines (Wilcoxon, Holm, 5%)", fontsize=6.6)
    bx.set_title("b   Per population: ANKYRA against each baseline", fontsize=7.2); bx.tick_params(axis="y", length=0)
    bx.legend(handles=[Patch(fc="#2166AC", label="ANKYRA better"), Patch(fc="#D9D9D9", label="not significant"), Patch(fc=ANKYRA, label="ANKYRA worse")], loc="lower left",
              bbox_to_anchor=(0.0, 1.03), ncol=3, fontsize=5.8, handlelength=1.0, handleheight=0.8, columnspacing=0.7, handletextpad=0.3)
    fig.text(0.01, 0.99, "Rank tests on per-unit RMSE, late windows, 21 forecasters. a: mean ranks over the 1,762 units of the six test populations (Friedman test p < 1e-300); the shaded band is",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.967, "the Nemenyi critical difference from ANKYRA's rank, and filled markers differ from ANKYRA in a Holm-corrected Wilcoxon signed-rank test. b: the same paired test per",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.944, "population (bold: test populations). Rank tests weight every unit equally and ignore the size of the differences; the primary estimand is the log RMS ratio of Figure 3.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig15_rank_tests")


# ============================================================================ Figure 16: interval coverage on ten populations
def fig_intervals_all():
    iv = rows("intervals_by_population.csv")
    sets = TEST + PREVIEW; arms = [("ankyra_2_0", "ANKYRA interval", ANKYRA, "o"), ("chronos_native", "Chronos-2 native", "#807DBA", "s"), ("timesfm_native", "TimesFM native 0.1–0.9", FM, "^")]
    val = {(r["set"], r["arm"]): r for r in iv}
    fig = plt.figure(figsize=(7.2, 3.6)); gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.0, 1.0], wspace=0.42, left=0.115, right=0.985, top=0.80, bottom=0.14)
    ax = fig.add_subplot(gs[0]); y = np.arange(len(sets))[::-1]
    ax.axvline(80, color="#1A1A1A", lw=0.7, ls="--")
    for key, name, col, mk in arms:
        ax.scatter([100 * float(val[(s_, key)]["cov80"]) for s_ in sets], y, s=16, color=col, marker=mk, zorder=3, label=name)
    ax.set_yticks(y); ax.set_yticklabels([SHORT[s_] for s_ in sets], fontsize=6.4)
    for t_, s_ in zip(ax.get_yticklabels(), sets):
        t_.set_fontweight("bold" if s_ in TEST else "normal")
    ax.set_xlim(30, 92); ax.set_xlabel("Coverage of the nominal 80% interval (% of hours)", fontsize=6.6); ax.set_title("a   Coverage, all hours", fontsize=7.2)
    ax.grid(axis="x", color="#EFEFEF", lw=0.4, zorder=0); ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.07), ncol=3, fontsize=5.8, handletextpad=0.2, columnspacing=0.8, frameon=False)
    wk = np.arange(1, 5)
    for j, (key, name, col, mk) in enumerate(arms[:2] + arms[2:]):
        if j == 0:
            bx = fig.add_subplot(gs[1]); bx.set_title("b   ANKYRA: coverage by forecast week", fontsize=7.2)
            for s_ in sets:
                bx.plot(wk, [100 * float(val[(s_, key)][f"cov80_week{w}"]) for w in wk], color=col, lw=0.8, alpha=0.75, marker="o", ms=2.2)
            bx.axhline(80, color="#1A1A1A", lw=0.7, ls="--"); bx.set_ylim(60, 95); bx.set_xticks(wk); bx.set_xticklabels([f"W{i}" for i in wk]); bx.set_ylabel("Coverage (%)", fontsize=6.6)
            bx.set_xlabel("Forecast week", fontsize=6.6)
    cx = fig.add_subplot(gs[2]); cx.set_title("c   Native quantiles by forecast week", fontsize=7.2)
    for key, name, col, mk in arms[1:]:
        for s_ in sets:
            cx.plot(wk, [100 * float(val[(s_, key)][f"cov80_week{w}"]) for w in wk], color=col, lw=0.7, alpha=0.6, marker=mk, ms=2.0)
    cx.axhline(80, color="#1A1A1A", lw=0.7, ls="--"); cx.set_ylim(10, 95); cx.set_xticks(wk); cx.set_xticklabels([f"W{i}" for i in wk]); cx.set_xlabel("Forecast week", fontsize=6.6)
    fig.text(0.01, 0.985, "Prediction intervals on the ten scored populations (all windows; bold: test populations). The ANKYRA interval adds pooled residual quantiles of the unit's pseudo-forecasts",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.945, "to the ANKYRA trajectory. Each line in b and c is one population; the dashed line is the nominal level. Computed after scoring, as a description.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig16_intervals_ten_populations")


# ============================================================================ Figure 17: two checks with the forecaster frozen
def fig_frozen_checks():
    cs = [r for r in rows("carrier_swap.csv") if r["subset"] == "full" and r["error"] == "hourly"]
    hk = rows("hkust_first_read.csv")
    pops = ["GoiEner non-household", "GoiEner households", "EWELD", "BDG2 2017", "Cambridge", "Arizona (HEEW)", "Oslo", "Drammen", "CINELDI", "Suzhou park"]
    CHR = "#1D91C0"
    fig = plt.figure(figsize=(7.2, 3.75))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.2, 0.58, 1.0, 1.0], wspace=0.1, left=0.095, right=0.985, top=0.80, bottom=0.215)
    ax = fig.add_subplot(gs[0]); y = np.arange(len(pops))[::-1].astype(float); lo_x, hi_x = -12, 30
    ax.axvspan(0, hi_x, color="#F3F6FA", zorder=0); ax.axvline(0, color="#7F7F7F", lw=0.6, zorder=1)
    for key, col, dy in (("ANKYRA-C vs Chronos-2", CHR, 0.16), ("ANKYRA vs TimesFM", FM, -0.16)):
        for yy, p_ in zip(y, pops):
            r = next(rr for rr in cs if rr["population"] == p_ and rr["contrast"] == key)
            p, a, b = float(r["improvement_pct"]), pct(float(r["um_high"])), pct(float(r["um_low"]))
            ax.plot([max(a, lo_x), min(b, hi_x)], [yy + dy, yy + dy], color=col, lw=1.1, solid_capstyle="butt", zorder=2)
            if a < lo_x:
                ax.annotate("", xy=(lo_x, yy + dy), xytext=(lo_x + 2.5, yy + dy), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.8, mutation_scale=5))
            ax.scatter([p], [yy + dy], s=15, color=col if float(r["um_high"]) < 0 else "white", edgecolor=col, lw=0.9, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([{"GoiEner non-household": "GoiEner NH", "GoiEner households": "GoiEner HH", "BDG2 2017": "BDG2", "Arizona (HEEW)": "HEEW"}.get(p_, p_) for p_ in pops], fontsize=6.4)
    ax.tick_params(axis="y", length=0); ax.set_xlim(lo_x, hi_x); ax.set_ylim(-0.7, len(pops) - 0.3); ax.grid(axis="x", color="#E5E5E5", lw=0.4, zorder=0)
    ax.set_title("a   Anchoring gain with either foundation model", fontsize=7.2); ax.set_xlabel("Hourly improvement over the\nfoundation model alone (%)", fontsize=6.6)
    ax.legend(handles=[Line2D([], [], marker="o", ls="-", color=CHR, markersize=3.5, lw=1.0, label="Chronos-2 anchored vs Chronos-2"),
                       Line2D([], [], marker="o", ls="-", color=FM, markersize=3.5, lw=1.0, label="TimesFM anchored (ANKYRA) vs TimesFM")],
              loc="upper center", bbox_to_anchor=(0.42, -0.2), fontsize=5.9, ncol=1, handletextpad=0.4)
    comps = ["Chronos-2-X", "TimesFM-X", "TimesFM 2.5", "Chronos-2", "Per-unit ridge", "Previous-month profile", "Four-week profile", "Last-year profile", "Seasonal naive (day)", "Seasonal naive (week)"]
    colour = {"Chronos-2-X": "#253494", "TimesFM-X": "#253494", "TimesFM 2.5": FM, "Chronos-2": CHR, "Per-unit ridge": "#8C6D31"}
    yb = np.arange(len(comps))[::-1].astype(float)
    for k, (kind, title, lim) in enumerate((("hourly", "b   HKUST: hourly error", (-12, 45)), ("energy", "c   HKUST: monthly energy error", (-35, 75)))):
        bx = fig.add_subplot(gs[k + 2]); bx.axvspan(0, lim[1], color="#F3F6FA", zorder=0); bx.axvline(0, color="#7F7F7F", lw=0.6, zorder=1)
        for yy, c_ in zip(yb, comps):
            r = next(rr for rr in hk if rr["error"] == kind and rr["comparator"] == c_)
            p, a, b = float(r["improvement_pct"]), pct(float(r["um_high"])), pct(float(r["um_low"])); col = colour.get(c_, "#9E9E9E")
            edge = kind == "hourly" and c_ in ("TimesFM 2.5", "Chronos-2")          # intervals that end at zero: borderline
            bx.plot([max(a, lim[0]), min(b, lim[1])], [yy, yy], color=col, lw=1.1, solid_capstyle="butt", zorder=2)
            for e_, beyond, d in ((lim[0], a < lim[0], 3.0), (lim[1], b > lim[1], -3.0)):
                if beyond:
                    bx.annotate("", xy=(e_, yy), xytext=(e_ + d, yy), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.8, mutation_scale=5))
            bx.scatter([p], [yy], s=17, marker="D" if edge else "o", color=col if (float(r["um_high"]) < 0 and not edge) else "white", edgecolor=col, lw=0.9, zorder=3)
        bx.set_yticks(yb); bx.set_yticklabels([c_.replace("Previous-month profile", "Prev.-month profile") for c_ in comps] if k == 0 else [], fontsize=6.2)
        bx.tick_params(axis="y", length=0); bx.set_xlim(*lim); bx.set_ylim(-0.7, len(comps) - 0.3); bx.grid(axis="x", color="#E5E5E5", lw=0.4, zorder=0)
        bx.set_title(title, fontsize=7.2); bx.set_xlabel("ANKYRA improvement (%)", fontsize=6.6)
    fig.text(0.01, 0.985, "a: ANKYRA 2.1 with Chronos-2 or TimesFM supplying the foundation forecasts, nothing re-selected; ten populations, all windows (re-evaluation).",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.945, "b, c: HKUST campus incomer meters (134 windows, 30 effective units), ANKYRA 2.1 (first scored with 2.0.1; same readings). 95% unit-and-month intervals; filled = excludes zero;",
             fontsize=6.3, color=GREY, va="top")
    fig.text(0.01, 0.905, "diamonds = borderline (the interval ends at zero and the reading changes with the bootstrap seed). Ridge: 123 windows. The two -X models were added afterwards.",
             fontsize=6.3, color=GREY, va="top")
    save(fig, "fig17_frozen_checks")


if __name__ == "__main__":
    fig_intervals_all()
    fig_rank_tests()
    fig_block_shares()
    fig_operators()
    fig_architecture()
    fig_test_ranks()
    fig_test_forest()
    fig_mechanism()
    fig_peak()
    fig_example()
    fig_loss_metrics()
    fig_lead_days()
    fig_energy_by_day()
    fig_lead_days_relative()
    fig_energy()
    fig_consistency()
    fig_intervals()
    fig_frozen_checks()
    print("figures written to", HERE)
