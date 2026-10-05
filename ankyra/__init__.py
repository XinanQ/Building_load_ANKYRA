"""ANKYRA: anchoring a time-series foundation model to each unit's own history for month-ahead load forecasting.

2.0 anchors all three blocks: level, daily path (1.x) and, with ``ankyra.analog``, the within-day shape.
2.0.1 hands a context whose 1,344 hours all stay within 1e-3 kW of zero to the foundation model (micro-load rule)."""
from .history import History, InputError, SignatureDegeneracy
from .core import AnkyraForecast, forecast, pseudo_origin_contexts, lead_week_weights, lead_week_transition
from . import blocks, readouts, metrics, analog

__version__ = "2.0.2"
__all__ = ["History", "InputError", "SignatureDegeneracy", "AnkyraForecast", "forecast", "pseudo_origin_contexts", "lead_week_weights",
           "lead_week_transition", "blocks", "readouts", "metrics", "analog"]
