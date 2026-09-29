"""Figures of the ANKYRA repository, generated from ../results only.

    python figures/make_figures.py            # writes figures/*.pdf (vector) and figures/*.png (300 dpi)
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
RESERVED = ["LCL households"]
SHORT = {"BDG2 2017": "BDG2", "Cambridge": "Cambridge", "HEEW Arizona": "HEEW", "EWELD": "EWELD",
         "GoiEner non-household": "GoiEner NH", "GoiEner households": "GoiEner HH", "Oslo": "Oslo", "Drammen": "Drammen",
         "CINELDI": "CINELDI", "Suzhou park": "Suzhou park", "LCL households": "LCL"}
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
    box(24, 2, 37.5, 14.5, r"Within-day shape  $w$", "#F2F0F8", "#B4ADD6", tc=FM)
    txt(25.1, 12.3, "day-demeaned TimesFM trajectory\nthe foundation model's most reliable block", fs=5.9)
    tt = np.linspace(0, 3, 160)
    spark(49.5, 3.4, 11.0, 4.2, np.sin(2 * np.pi * tt - 1.6) + 0.35 * np.sin(4 * np.pi * tt), FM, lw=0.8)

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
    ax.add_patch(FancyBboxPatch((86.3, 20.0), 12.2, 7.6, boxstyle="round,pad=0.15,rounding_size=0.8", fc="#FBEDEE", ec="#E3A0A6", lw=0.6, zorder=2))
    txt(86.9, 27.0, "off-state switch", color=ANKYRA, fs=5.8, fontweight="bold")
    txt(86.9, 24.6, r"last 168 h $\leq 10^{-6}$ kW" + "\n→ TimesFM unchanged", fs=5.5)
    box(85.4, 2, 14.0, 14.5, "Readouts", "#FFFFFF", "#9E9E9E")
    txt(86.5, 12.4, r"energy  $744\,\ell$", color=ink, fs=5.9)
    txt(86.5, 9.4, r"peak  $\mathrm{max}_d\,(\hat L_d+A_{\tau_d})$", color=ink, fs=5.9)
    txt(86.5, 6.4, "interval  pseudo-origin\nresidual quantiles", color=ink, fs=5.9)

    # ---- arrows (horizontal or right-angled, no crossings)
    g = "#8C8C8C"
    arrow([(20.5, 43.0), (23.7, 43.0)], HIST)
    arrow([(20.5, 25.9), (23.7, 25.9)], HIST)
    arrow([(20.5, 9.2), (23.7, 9.2)], FM)
    arrow([(61.8, 43.0), (64.9, 43.0)], HIST)
    arrow([(61.8, 25.9), (64.9, 25.9)], HIST)
    arrow([(82.9, 34.4), (85.1, 34.4)], ANKYRA, lw=1.1)
    arrow([(61.8, 5.4), (83.6, 5.4), (83.6, 29.1), (85.1, 29.1)], FM)
    arrow([(92.4, 18.2), (92.4, 16.8)], g)

    ax.text(50, -0.4, r"Exact identity:  $\mathrm{MSE}=\ell(e)^2+\langle b_d(e)^2\rangle_d+\langle w_{d,h}(e)^2\rangle_{d,h}$"
            "  — the blocks are orthogonal, so each source can be scored and replaced block by block.",
            ha="center", va="top", fontsize=6.4, color=GREY)
    ax.legend(handles=[Patch(fc=HIST, label="from the unit's own history"), Patch(fc=FM, label="from TimesFM 2.5"),
                       Patch(fc=ANKYRA, label="ANKYRA's handover")], loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
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
    fig.text(0.01, 0.955, "the six test sets were scored once, after the model had been fixed. NH: non-household; HH: households. "
             "b: 95% unit-and-month bootstrap interval of the unit-equal log RMS ratio.", fontsize=6.3, color=GREY, va="top")
    save(fig, "fig2_test_ranks")


# ============================================================================ Figure 3: pairwise improvements with intervals
def fig_test_forest():
    pw = [r for r in rows("benchmark_pairwise.csv") if r["subset"] == "late" and r["tier"] == "test"]
    models = ["TiDE", "iTransformer-X", "GBT-T", "Chronos-2-X", "TimesFM-X", "TimesFM", "Chronos-2", "Holt-Winters", "MSTL"]
    cls = {r["model"]: r["model_class"] for r in pw}
    lo_x, hi_x = -30, 45
    fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.35), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.125, right=0.99, top=0.86, bottom=0.155, hspace=0.34, wspace=0.08)
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
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=6.1, bbox_to_anchor=(0.55, 0.035), handletextpad=0.2, columnspacing=1.0)
    fig.text(0.125, 0.004, "† The BDG2 unit mean is pulled by three meters reading ≈0.0002 kW (above the off-state threshold). Against all nine models the median unit "
             "favours ANKYRA (59–92% of units).", fontsize=5.8, color="#7F7F7F")
    save(fig, "fig3_test_pairwise")


# ============================================================================ Figure 4: what the handover does
def fig_mechanism():
    ab = rows("ablation.csv"); lw_ = rows("lead_weeks_first_read.csv")
    order = TEST + PREVIEW + RESERVED
    fig = plt.figure(figsize=(7.2, 2.85))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1, 0.8], wspace=0.42, left=0.105, right=0.99, top=0.83, bottom=0.17)
    ax = fig.add_subplot(gs[0])
    y = np.arange(len(order))[::-1]
    ax.axhspan(y[len(TEST) - 1] - 0.5, y[0] + 0.5, color="#F3F6FA", zorder=0)
    ax.axvline(0, color="#7F7F7F", lw=0.6)
    for yy, s in zip(y, order):
        for key, mk, col, dy in (("fixed division", "o", ANKYRA, 0.17), ("without off-state", "D", "#4D4D4D", -0.17)):
            r = next(rr for rr in ab if rr["set"] == s and rr["ablation"].startswith(key))
            p, a, b = float(r["improvement_pct"]), pct(float(r["um_high"])), pct(float(r["um_low"]))
            sig = float(r["um_high"]) < 0 or float(r["um_low"]) > 0
            ax.plot([a, b], [yy + dy, yy + dy], color=col, lw=0.9)
            ax.scatter([p], [yy + dy], marker=mk, s=15 if mk == "o" else 11, color=col if sig else "white", edgecolor=col, lw=0.8, zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([SHORT[s] for s in order], fontsize=6.4)
    for t_, s in zip(ax.get_yticklabels(), order):
        if s in TEST:
            t_.set_fontweight("bold")
    ax.tick_params(axis="y", length=0)
    ax.text(40, y[0] + 0.25, "test sets", fontsize=6, color="#4A6FA5", fontstyle="italic", ha="right", va="center")
    ax.set_xlabel("ANKYRA improvement (%)", fontsize=6.8)
    ax.set_title("a   Ablation", fontsize=7.6)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=ANKYRA, markersize=3.8, label="vs fixed division (F0)"),
                       Line2D([], [], marker="D", ls="", color="#4D4D4D", markersize=3.2, label="vs no off-state rule (F1)")],
              loc="lower right", fontsize=5.9, handletextpad=0.2, borderaxespad=0.1)
    bx = fig.add_subplot(gs[1]); cx = fig.add_subplot(gs[2])
    marks = {"Cambridge": "o", "CINELDI": "s", "HEEW Arizona": "^"}
    wk = np.arange(1, 5)
    bx.axhline(0, color="#7F7F7F", lw=0.6)
    for s, mk in marks.items():
        rr = [r for r in lw_ if r["set"] == s]
        bx.plot(wk, [pct(float(r["fixed_division_vs_timesfm_log_ratio"])) for r in rr], color="#9E9E9E", ls=(0, (3, 2)), marker=mk, ms=3.2, mfc="white", lw=0.9)
        bx.plot(wk, [pct(float(r["ankyra_vs_timesfm_log_ratio"])) for r in rr], color=ANKYRA, marker=mk, ms=3.4, lw=1.1)
        cx.plot(wk, [float(r["mean_weight_on_model"]) for r in rr], color=FM, marker=mk, ms=3.4, lw=1.0, label=SHORT[s])
    bx.set_xticks(wk); bx.set_xticklabels([f"W{i}" for i in wk]); bx.set_xlabel("Forecast week", fontsize=6.8)
    bx.set_ylabel("Improvement over TimesFM (%)", fontsize=6.8)
    bx.set_title("b   Lead-week profile vs TimesFM", fontsize=7.6)
    bx.legend(handles=[Line2D([], [], color=ANKYRA, lw=1.1, label="ANKYRA"), Line2D([], [], color="#9E9E9E", ls=(0, (3, 2)), lw=0.9, label="fixed division (F0)")],
              loc="lower right", fontsize=5.9, handlelength=1.8)
    cx.axhline(0.5, color="#BDBDBD", lw=0.6, ls=(0, (2, 2)))
    cx.text(4.15, 0.5, "prior", fontsize=5.5, color="#9E9E9E", va="center")
    cx.set_ylim(0.25, 0.75); cx.set_xticks(wk); cx.set_xticklabels([f"W{i}" for i in wk]); cx.set_xlabel("Forecast week", fontsize=6.8)
    cx.set_ylabel(r"Mean weight on the model  $\alpha_w$", fontsize=6.8)
    cx.set_title("c   Estimated handover", fontsize=7.6)
    cx.legend(fontsize=5.9, loc="upper right", handlelength=1.4)
    fig.text(0.105, 0.985, "b–c: Cambridge, CINELDI and HEEW, scored for the first time after the handover had been fixed. Shaded in a: the six test sets.",
             fontsize=6.2, color=GREY, va="top")
    save(fig, "fig4_handover_and_ablation")


# ============================================================================ Figure 5: peak operator
def fig_peak():
    pk = rows("peak_readout.csv"); order = TEST + PREVIEW + RESERVED
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
    from ankyra import blocks, operators as op, readouts
    from ankyra.history import estimate_from_history
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
             "b–d: exact properties. P-numbers: docs/THEORY.md.",
             fontsize=6.0, color=GREY, va="top")
    save(fig, "fig7_operators")


if __name__ == "__main__":
    fig_operators()
    fig_architecture()
    fig_test_ranks()
    fig_test_forest()
    fig_mechanism()
    fig_peak()
    fig_example()
    print("figures written to", HERE)
