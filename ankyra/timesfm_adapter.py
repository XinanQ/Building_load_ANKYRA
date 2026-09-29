"""TimesFM 2.5 (200M) point forecasts configured as in the study.

The study loaded the official PyTorch checkpoint (Apache-2.0, Hugging Face revision
1d952420fba87f3c6dee4f240de0f1a0fbc790e3), compiled it with ForecastConfig(max_context=1344, max_horizon=744) and all
other options at their defaults, passed load only (no covariates) and used the point forecast.

Requires the optional dependency ``timesfm`` (``pip install ankyra[timesfm]``).  Loading from the Hugging Face id
downloads the checkpoint; a local directory containing ``model.safetensors`` is loaded offline.
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np

CONTEXT, HORIZON = 1344, 744
HF_REPO = "google/timesfm-2.5-200m-pytorch"
HF_REVISION = "1d952420fba87f3c6dee4f240de0f1a0fbc790e3"


def load_timesfm(checkpoint: Optional[str] = None, device: Optional[str] = None):
    """Return a compiled TimesFM 2.5 model.  ``checkpoint``: local directory / file, or None for the pinned HF revision."""
    import timesfm
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
    model.compile(timesfm.ForecastConfig(max_context=CONTEXT, max_horizon=HORIZON))
    return model


def timesfm_forecaster(model, batch_size: int = 64):
    """Callable (N, 1344) contexts -> (N, 744) point forecasts, for ``ankyra.forecast(..., foundation=...)``."""
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
