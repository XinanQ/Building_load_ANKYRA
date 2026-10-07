"""ANKYRA: anchoring a time-series foundation model to each unit's own history for month-ahead load forecasting.

2.0 anchors all three blocks: level, daily path (1.x) and, with ``ankyra.analog``, the within-day shape.
2.0.1 hands a context whose 1,344 hours all stay within 1e-3 kW of zero to the foundation model (micro-load rule).
Package 2.0.2 masks hours marked unobserved once for every branch; 2.0.3 changes documentation only (model 2.0.1).
2.1 estimates the within-day trust as one value per window instead of one per lead block (``single_trust=False``
reproduces 2.0.1)."""
from .history import History, InputError, SignatureDegeneracy
from .core import AnkyraForecast, forecast, pseudo_origin_contexts, fill_short_gaps, lead_week_weights, lead_week_transition
from . import blocks, readouts, metrics, analog

__version__ = "2.2.0"
__all__ = ["History", "InputError", "SignatureDegeneracy", "AnkyraForecast", "forecast", "pseudo_origin_contexts", "fill_short_gaps", "lead_week_weights",
           "lead_week_transition", "blocks", "readouts", "metrics", "analog"]
