"""Gap tolerance (2.2): short gaps interpolated and partially observed pseudo targets accepted, for the pseudo-origin bookkeeping only."""
import unittest

import numpy as np
import torch

import ankyra
from ankyra.core import CONTEXT, HORIZON, STEP, GAP_MAX_H, TARGET_MIN_OBS, fill_short_gaps, pseudo_origin_contexts
from ankyra.history import History, InputError
from ankyra.synthetic import synthetic_history

torch.set_num_threads(1)


def fm_for(load):
    """A foundation forecast at every pseudo-origin whose (raw or filled) context exists: the seasonal-naive week."""
    return {k: np.tile(ctx[-168:], 5)[:HORIZON] for k, ctx in pseudo_origin_contexts(load, gap_tolerance=True).items()}


def run(h, **kw):
    kw.setdefault("group", "Office"); kw.setdefault("temp_sigma_std", 0.25)
    kw.setdefault("foundation", fm_for(np.asarray(h.load_kw, float)))
    return ankyra.forecast(h, **kw)


class FillTests(unittest.TestCase):
    def test_short_gap_inside_a_block_is_interpolated(self):
        x = np.arange(3000, dtype=float); x[100:104] = np.nan                        # 4 hours, far from any block boundary
        f = fill_short_gaps(x)
        self.assertTrue(np.allclose(f[100:104], np.arange(100, 104, dtype=float)))
        self.assertTrue(np.array_equal(np.isnan(f), np.zeros(3000, bool)))

    def test_long_gap_and_boundary_gap_stay_missing(self):
        o = 3000; x = np.arange(o, dtype=float)
        x[200:200 + GAP_MAX_H + 1] = np.nan                                           # one hour too long
        q = o - STEP; x[q - 2:q + 2] = np.nan                                         # straddles the pseudo-origin o - 744
        f = fill_short_gaps(x)
        self.assertTrue(np.isnan(f[200:200 + GAP_MAX_H + 1]).all()); self.assertTrue(np.isnan(f[q - 2:q + 2]).all())

    def test_no_value_after_a_pseudo_origin_enters_the_fill(self):
        o = 3000; x = np.arange(o, dtype=float); q = o - STEP
        x[q - 5:q - 2] = np.nan                                                       # gap inside the block ending at q
        f1 = fill_short_gaps(x); y = x.copy(); y[q:] = 999.0; f2 = fill_short_gaps(y)
        self.assertTrue(np.array_equal(f1[:q], f2[:q]))

    def test_complete_record_unchanged_and_untouched_at_the_origin(self):
        x = np.arange(3000, dtype=float); self.assertTrue(np.array_equal(fill_short_gaps(x), x))
        x[-3:] = np.nan; self.assertTrue(np.isnan(fill_short_gaps(x)[-3:]).all())    # a gap touching the origin has no right neighbour

    def test_pseudo_origin_contexts_origin_raw_pseudo_filled(self):
        h = synthetic_history(16000); load = np.array(h.load_kw, float); q = len(load) - 2 * STEP
        load[q - 700:q - 697] = np.nan
        c_old = pseudo_origin_contexts(load, gap_tolerance=False); c_new = pseudo_origin_contexts(load)
        self.assertNotIn(2, c_old); self.assertIn(2, c_new); self.assertTrue(np.array_equal(c_new[0], load[-CONTEXT:]))


class ForecastTests(unittest.TestCase):
    def test_complete_data_bit_identical_to_2_1(self):
        h = synthetic_history(16000)
        a = run(h); b = run(h, gap_tolerance=False)
        self.assertTrue(np.array_equal(a.trajectory_kw, b.trajectory_kw)); self.assertEqual(a.pseudo_pairs, b.pseudo_pairs)
        self.assertEqual(a.level_weights, b.level_weights)

    def test_gaps_in_pseudo_windows_recover_pseudo_pairs(self):
        h = synthetic_history(16000); load = np.array(h.load_kw, float); o = len(load)
        for k in (3, 4, 5):                                                           # a 3-hour gap in each pseudo context (outside the origin context) ...
            q = o - k * STEP; load[q - 500:q - 497] = np.nan
        q = o - 6 * STEP; load[q + 100:q + 160] = np.nan                                # ... and 60 missing target hours (92% observed) at k = 6
        hg = History(load, h.temperature_c, h.day_types, h.start_timestamp)
        a = run(hg); b = run(hg, gap_tolerance=False)
        self.assertGreater(a.pseudo_pairs, b.pseudo_pairs)
        self.assertTrue(np.isfinite(a.trajectory_kw).all()); self.assertGreaterEqual(a.pseudo_pairs, 4)

    def test_target_below_the_observed_share_is_not_used(self):
        h = synthetic_history(16000); load = np.array(h.load_kw, float); o = len(load)
        q = o - 4 * STEP; load[q + 100:q + 100 + int(HORIZON * (1 - TARGET_MIN_OBS)) + 24] = np.nan     # below 90 % observed
        hg = History(load, h.temperature_c, h.day_types, h.start_timestamp)
        a = run(hg); b = run(hg, gap_tolerance=False)
        self.assertEqual(a.pseudo_pairs, b.pseudo_pairs)

    def test_anchoring_record_is_reported_and_unused(self):
        h = synthetic_history(16000); a = run(h)
        rec = a.anchoring_record
        self.assertEqual(set(rec), {"carrier_level_weight", "history_vs_carrier_log_ratio", "pseudo_origins"})
        self.assertEqual(rec["carrier_level_weight"], a.level_weights["fm"]); self.assertTrue(np.isfinite(rec["history_vs_carrier_log_ratio"]))
        self.assertEqual(rec["pseudo_origins"], a.pseudo_pairs)
        off = run(History(np.r_[np.asarray(h.load_kw)[:-168], np.zeros(168)], h.temperature_c, h.day_types, h.start_timestamp), foundation={0: np.zeros(HORIZON)})
        self.assertTrue(off.off_state); self.assertEqual(off.anchoring_record, {})

    def test_origin_context_gap_still_refused(self):
        h = synthetic_history(16000); load = np.array(h.load_kw, float); load[-10:-7] = np.nan
        hg = History(load, h.temperature_c, h.day_types, h.start_timestamp)
        with self.assertRaises(InputError):
            run(hg, foundation={0: np.full(HORIZON, 1.0)})


if __name__ == "__main__":
    unittest.main()
