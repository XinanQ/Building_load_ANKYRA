"""End-to-end ANKYRA forecast on an artificial building; no data or downloads needed.

    python examples/quickstart.py              # foundation-model slot filled by a stand-in (last week repeated)
    python examples/quickstart.py --timesfm    # TimesFM 2.5 (pip install "ankyra[timesfm]"; downloads the checkpoint)
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import torch

import ankyra
from ankyra import readouts
from ankyra.synthetic import synthetic_history, seasonal_naive


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timesfm", action="store_true", help="use TimesFM 2.5 in the foundation-model slot")
    ap.add_argument("--checkpoint", default=None, help="local TimesFM checkpoint directory (optional)")
    args = ap.parse_args()
    torch.set_num_threads(1)

    history = synthetic_history(16000)                      # 16,000 hours before the origin
    foundation = seasonal_naive
    if args.timesfm:
        from ankyra.timesfm_adapter import load_timesfm, timesfm_forecaster
        foundation = timesfm_forecaster(load_timesfm(args.checkpoint))

    f = ankyra.forecast(history, group="Office", temp_sigma_std=0.25, foundation=foundation)

    o = len(history.load_kw)
    types = history.day_types
    context = history.load_kw[o - 1344:o]
    ctx_types = types[o - 1344 + 12 + 24 * np.arange(56)]
    tgt_types = types[o + 12 + 24 * np.arange(31)]
    peak = readouts.peak_readout(f.trajectory_kw, context[None], ctx_types[None], tgt_types[None])[0]

    print(json.dumps({
        "foundation_model": "TimesFM 2.5" if args.timesfm else "stand-in (last week repeated)",
        "off_state": f.off_state,
        "energy_kwh": round(f.energy_kwh, 3),
        "level_kw": round(f.level_kw, 4),
        "peak_kw": round(float(peak), 3),
        "lead_week_weights_on_model": [round(a, 3) for a in f.lead_week_weights],
        "level_weights": {k: round(v, 3) for k, v in f.level_weights.items()},
        "pseudo_origin_pairs": f.pseudo_pairs,
        "trajectory_first_day_kw": np.round(f.trajectory_kw[:24], 2).tolist(),
    }, indent=1))


if __name__ == "__main__":
    main()
