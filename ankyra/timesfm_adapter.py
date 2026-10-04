"""TimesFM 2.5 (200M) point forecasts configured as in the study.

The study loaded the official PyTorch checkpoint (Apache-2.0, Hugging Face revision
1d952420fba87f3c6dee4f240de0f1a0fbc790e3), compiled it with ForecastConfig(max_context=1344, max_horizon=744) and all
other options at their defaults (so the model's own batch, ``per_core_batch_size``, was 1), passed load only (no
covariates) and used the point forecast.

Requires the optional dependency ``timesfm`` (``pip install -e ".[timesfm]"`` from the repository root); the installed
package must provide TimesFM 2.5 (``timesfm.TimesFM_2p5_200M_torch``).  Loading from the Hugging Face id downloads the
checkpoint; a local directory containing ``model.safetensors`` is loaded offline.
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np

from .blocks import CONTEXT, HORIZON

HF_REPO = "google/timesfm-2.5-200m-pytorch"
HF_REVISION = "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"


def load_timesfm(checkpoint: Optional[str] = None, device: Optional[str] = None, per_core_batch_size: int = 1):
    """Return a compiled TimesFM 2.5 model.

    checkpoint           a local directory containing ``model.safetensors``, or that file itself; None downloads
                         ``google/timesfm-2.5-200m-pytorch`` at the pinned revision
    device               e.g. "cpu" or "cuda"; None keeps the device TimesFM chooses
    per_core_batch_size  the model's own batch (1 in the study; 64 gives the same forecasts to within 3e-5 kW and is
                         faster)
    """
    try:
        import timesfm
    except ImportError as exc:
        raise ImportError('TimesFM could not be imported (it is an optional dependency). '
                          'From the repository root run: pip install -e ".[timesfm]"') from exc
    if not hasattr(timesfm, "TimesFM_2p5_200M_torch"):
        raise ImportError("the installed timesfm package does not provide TimesFM 2.5 (timesfm.TimesFM_2p5_200M_torch); "
                          "install TimesFM 2.5 from https://github.com/google-research/timesfm")
    if checkpoint is not None and checkpoint != HF_REPO and not os.path.exists(checkpoint):
        raise FileNotFoundError(f"TimesFM checkpoint not found: {checkpoint!r}; pass a directory containing model.safetensors, "
                                f"the file itself, or None for {HF_REPO} at the pinned revision")
    import torch
    if checkpoint is not None and os.path.exists(checkpoint):
        model = timesfm.TimesFM_2p5_200M_torch(torch_compile=False)
        if device is not None:
            model.model.device = torch.device(device)
            model.model.device_count = 1
        model.load_checkpoint(checkpoint, torch_compile=False)
    else:
        model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(checkpoint or HF_REPO, revision=HF_REVISION, torch_compile=False)
        if device is not None:
            model.model.device = torch.device(device)
            model.model.device_count = 1
            model.model.to(model.model.device)
    model.compile(timesfm.ForecastConfig(max_context=CONTEXT, max_horizon=HORIZON, per_core_batch_size=per_core_batch_size))
    return model


def timesfm_forecaster(model, batch_size: int = 64):
    """Callable (N, 1344) contexts -> (N, 744) point forecasts, for ``ankyra.forecast(..., foundation=...)``.

    ``batch_size`` is the number of contexts handed to ``model.forecast`` per call.  It does not change the model's own
    batch, which is set by ``per_core_batch_size`` in ``load_timesfm``."""
    def run(contexts):
        ctx = np.asarray(contexts, dtype=np.float64)
        if ctx.ndim != 2 or ctx.shape[1] != CONTEXT or not np.isfinite(ctx).all():
            raise ValueError(f"contexts must be finite (N, {CONTEXT})")
        out = []
        for s in range(0, len(ctx), batch_size):
            point, _ = model.forecast(horizon=HORIZON, inputs=[row.astype(np.float32) for row in ctx[s:s + batch_size]])
            out.append(np.asarray(point, dtype=np.float64)[:, :HORIZON])
        return np.concatenate(out)
    return run
