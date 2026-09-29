"""The vendored historical estimator (ankyra.history) against the reference package's documented synthetic example."""
import unittest

import numpy as np
import torch

from ankyra.history import estimate_from_history, InputError
from ankyra.synthetic import synthetic_history

torch.set_num_threads(1)


class HistoryReferenceTests(unittest.TestCase):
    def test_documented_synthetic_level(self):
        e = estimate_from_history(synthetic_history(16000), group="Office", temp_sigma_std=0.25)
        self.assertAlmostEqual(e.level_kw, 22.5983831772, places=8)
        self.assertLess(abs(e.daily_path_kw.sum()), 1e-9)
        self.assertAlmostEqual(sum(e.diagnostics["level_weights"].values()), 1.0, places=12)

    def test_annual_candidate_needs_two_error_records(self):
        before = estimate_from_history(synthetic_history(10247), group="Office", temp_sigma_std=0.25)
        at = estimate_from_history(synthetic_history(10248), group="Office", temp_sigma_std=0.25)
        self.assertEqual(before.diagnostics["level_error_counts"]["a_u"], 1)
        self.assertEqual(at.diagnostics["level_error_counts"]["a_u"], 2)

    def test_missing_context_is_rejected(self):
        h = synthetic_history(6000)
        h.load_kw[-10] = np.nan
        with self.assertRaises(InputError):
            estimate_from_history(h, group="Office", temp_sigma_std=0.25)


if __name__ == "__main__":
    unittest.main()
