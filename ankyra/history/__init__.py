"""Specified historical level and daily-path replacement, reference interface 1.1."""
from .api import History, Estimate, InputError, SignatureDegeneracy, estimate_from_history, frozen_config, score_against_observations
__version__ = '1.1.0'
__all__ = ['History','Estimate','InputError','SignatureDegeneracy','estimate_from_history','frozen_config','score_against_observations']
