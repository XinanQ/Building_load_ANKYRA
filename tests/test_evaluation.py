"""The evaluation module: scoring blocks, late subset, rank tests, scaled errors, windows and baselines."""
import unittest

import numpy as np

from ankyra import metrics
from evaluation import baselines, scoring, windows


def toy(n_units=8, per_unit=3, seed=1):
    rng = np.random.default_rng(seed); n = n_units * per_unit
    y = 10 + rng.random((n, 744)); unit = np.repeat([f"u{i}" for i in range(n_units)], per_unit); month = np.tile(["2020-01", "2020-02", "2020-03"], n_units)
    F = {"ANKYRA": y + 0.1 * rng.standard_normal(y.shape), "A": y + 0.3 * rng.standard_normal(y.shape), "B": y + 0.2 * rng.standard_normal(y.shape)}
    return F, y, unit, month, 10 + rng.random((n, 1344))


class ScoringTests(unittest.TestCase):
    def test_block_matches_the_package_estimand_and_resolves_clear_differences(self):
        F, y, unit, month, _ = toy()
        b = scoring.block(F, y, unit, month, "ANKYRA", n_boot=200)
        r = metrics.log_ratio(scoring.window_mse(F["ANKYRA"], y), scoring.window_mse(F["A"], y), unit)
        self.assertEqual(b["pairwise"]["A"]["log_ratio"], r)
        self.assertEqual(b["pairwise"]["A"]["resolved"], "better")
        self.assertLess(b["pairwise"]["A"]["um_low"], b["pairwise"]["A"]["um_high"])
        self.assertEqual(min(b["mean_unit_rank"], key=b["mean_unit_rank"].get), "ANKYRA")
        self.assertEqual((b["windows"], b["units"], b["months"]), (24, 8, 3))

    def test_intervals_are_reproducible_and_family_is_left_out_of_the_ranking(self):
        F, y, unit, month, _ = toy(); F["reduced"] = F["ANKYRA"] + 0.01
        a = scoring.block(F, y, unit, month, "ANKYRA", family=("reduced",), n_boot=100)
        b = scoring.block(F, y, unit, month, "ANKYRA", family=("reduced",), n_boot=100)
        self.assertEqual(a["pairwise"], b["pairwise"])
        self.assertIn("reduced", a["pairwise"]); self.assertNotIn("reduced", a["mean_unit_rank"])

    def test_late_block_uses_the_windows_every_model_covers(self):
        F, y, unit, month, _ = toy(); F["trained"] = F["B"].copy(); F["trained"][month == "2020-01"] = np.nan
        r = scoring.score_population(F, y, unit, month, n_boot=50)
        self.assertNotIn("trained", r["full"]["pairwise"]); self.assertIn("trained", r["late"]["pairwise"])
        self.assertEqual(r["late"]["windows"], 16)
        with self.assertRaises(ValueError):
            scoring.score_population({**F, "ANKYRA": F["trained"]}, y, unit, month, n_boot=10)

    def test_rank_tests_scaled_errors_energy_and_days(self):
        F, y, unit, month, ctx = toy(n_units=20)
        t = scoring.rank_tests(scoring.unit_rmse(F, y, unit)[1])
        self.assertEqual(t["units"], 20); self.assertEqual(set(t["significantly_better_than"]), {"A", "B"}); self.assertLess(t["friedman_p"], 0.01)
        s = scoring.scaled_errors(F, y, ctx, unit)
        self.assertLess(s["ANKYRA"]["RMSSE_geo_mean"], s["A"]["RMSSE_geo_mean"])
        e = scoring.energy_error(F, y, unit, month, n_boot=50); self.assertEqual(set(e), {"A", "B"})
        d = scoring.by_forecast_day(F, y, unit)
        self.assertEqual(d["gm_cv_rmse_pct"]["ANKYRA"].shape, (31,)); self.assertEqual(d["units_in_set"], 20)


class WindowAndBaselineTests(unittest.TestCase):
    def test_usable_origins_need_complete_context_target_and_history(self):
        load = np.ones(12000); load[9000] = np.nan
        o = windows.usable_origins(load, [3000, 6000, 8500, 9500, 10400, 11500])
        self.assertEqual(list(o), [6000, 10400])                           # dropped: too little history, a gap in the target or the context, no room for the target
        starts = windows.month_starts("2020-01-01T00:00:00+00:00", 2000)
        self.assertEqual(list(starts), [0, 744, 1440])
        ctx, y, month = windows.window_arrays(np.arange(12000.0), [6000], "2020-01-01T00:00:00+00:00")
        self.assertEqual((ctx.shape, y.shape), ((1, 1344), (1, 744))); self.assertEqual(ctx[0, -1], 5999.0); self.assertEqual(y[0, 0], 6000.0)

    def test_baselines_repeat_the_context(self):
        ctx = np.arange(1344.0)[None]
        d = baselines.seasonal_naive(ctx, 24); w = baselines.seasonal_naive(ctx, 168); p = baselines.week_profile(ctx)
        self.assertEqual(d.shape, (1, 744)); np.testing.assert_array_equal(d[0, :24], ctx[0, -24:]); np.testing.assert_array_equal(d[0, 24:48], ctx[0, -24:])
        np.testing.assert_array_equal(w[0, :168], ctx[0, -168:])
        np.testing.assert_allclose(p[0, :168], ctx[0, -672:].reshape(4, 168).mean(0))


if __name__ == "__main__":
    unittest.main()
