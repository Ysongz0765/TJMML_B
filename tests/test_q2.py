from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.q2.ces import ces_utility
from src.q2.config import ABILITY_COLUMNS, SCENES, equal_reference
from src.q2.data_adapter import load_q1_input
from src.q2.imbalance_penalty import imbalance_penalty
from src.q2.kl_weights import solve_scene_weights
from src.q2.linear_baseline import linear_utility
from src.q2.marginal_analysis import ces_marginal_utility, numerical_marginal_utility
from src.q2.missing_policy import apply_missing_policy, utility_intervals
from src.q2.normalize import normalise_abilities
from src.q2.pairwise_analysis import analyze_target_model, compare_models
from src.q2.pipeline import build_q2_pipeline, write_pipeline_tables
from src.q2.plotting import plot_rank_migration, plot_rank_surface
from src.q2.sensitivity import (
    compare_prior_robustness,
    detect_rank_jump_thresholds,
    rank_surface,
    run_sensitivity_grid,
    summarise_rank_robustness,
)


REPO = Path(__file__).resolve().parents[1]
MOCK_CSV = REPO / "data" / "q2" / "mock_q1_input.csv"
MOCK_METADATA = REPO / "data" / "q2" / "mock_q1_metadata.json"
FINAL_METADATA_TEMPLATE = REPO / "data" / "q2" / "q1_final_metadata_template.json"
FINAL_CSV_TEMPLATE = REPO / "data" / "q2" / "q1_final_input_template.csv"


class DataAdapterTests(unittest.TestCase):
    def test_mock_load_and_normalise_preserve_missing(self):
        bundle = load_q1_input(MOCK_CSV, MOCK_METADATA, "DEVELOPMENT")
        frame = normalise_abilities(bundle.frame, bundle.metadata["ability_scale"])
        model_f = frame.loc[frame["model"] == "Model_F"].iloc[0]
        self.assertTrue(np.isnan(model_f["C5"]))
        self.assertFalse(bool(model_f["C5_available"]))
        self.assertAlmostEqual(float(frame.loc[0, "C1"]), 0.84)

    def test_development_rejects_unmarked_data(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "input.csv"
            metadata_path = Path(directory) / "metadata.json"
            pd.read_csv(MOCK_CSV).drop(columns=["MOCK_DATA_ONLY"]).to_csv(csv_path, index=False)
            metadata = json.loads(MOCK_METADATA.read_text(encoding="utf-8"))
            metadata["mock_data_only"] = False
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaises(PermissionError):
                load_q1_input(csv_path, metadata_path, "DEVELOPMENT")

    def test_final_mode_is_blocked_by_template_metadata(self):
        with self.assertRaises(PermissionError):
            load_q1_input(FINAL_CSV_TEMPLATE, FINAL_METADATA_TEMPLATE, "FINAL")


class KLWeightTests(unittest.TestCase):
    def test_all_scene_projections_are_feasible(self):
        prior = {"C1": 0.22, "C2": 0.20, "C3": 0.18, "C4": 0.25, "C5": 0.15}
        for scene in SCENES.values():
            with self.subTest(scene=scene.key):
                result = solve_scene_weights(prior, scene, ABILITY_COLUMNS)
                values = np.asarray(list(result.weights.values()))
                self.assertTrue(result.success)
                self.assertTrue(bool(result.diagnostics["feasible"]))
                self.assertGreaterEqual(values.min(), -1e-10)
                self.assertAlmostEqual(values.sum(), 1.0, places=9)
                self.assertGreaterEqual(
                    float(result.diagnostics["core_mass"]),
                    scene.alpha_development_default - 1e-8,
                )

    def test_equal_prior_interface(self):
        result = solve_scene_weights(equal_reference(), SCENES["coding"], ABILITY_COLUMNS)
        self.assertAlmostEqual(sum(result.weights.values()), 1.0, places=9)


class CESAndInterpretationTests(unittest.TestCase):
    def setUp(self):
        self.values = np.asarray([0.82, 0.71, 0.90, 0.63, 0.77])
        self.weights = np.asarray([0.22, 0.20, 0.18, 0.25, 0.15])

    def test_rho_one_equals_linear_when_eps_zero(self):
        ces = float(ces_utility(self.values, self.weights, rho=1.0, eps=0.0))
        linear = float(linear_utility(self.values, self.weights))
        self.assertAlmostEqual(ces, linear, places=12)

    def test_rho_zero_equals_weighted_geometric_mean(self):
        ces = float(ces_utility(self.values, self.weights, rho=0.0, eps=0.0))
        expected = float(np.exp(np.sum(self.weights * np.log(self.values))))
        self.assertAlmostEqual(ces, expected, places=12)

    def test_imbalance_penalty_is_positive_for_unbalanced_vector(self):
        values = np.asarray([0.95, 0.90, 0.85, 0.15, 0.80])
        linear = np.asarray([linear_utility(values, self.weights)])
        ces = np.asarray([ces_utility(values, self.weights, rho=-0.4, eps=0.0)])
        penalty, pri = imbalance_penalty(linear, ces)
        self.assertGreater(float(penalty[0]), 0.0)
        self.assertGreater(float(pri[0]), 0.0)
        self.assertLess(float(pri[0]), 1.0)

    def test_analytic_marginal_matches_finite_difference(self):
        for rho in (-0.4, 0.0, 0.55):
            with self.subTest(rho=rho):
                analytic = ces_marginal_utility(self.values, self.weights, rho)
                numeric = numerical_marginal_utility(self.values, self.weights, rho, step=1e-6)
                np.testing.assert_allclose(analytic, numeric, rtol=2e-5, atol=2e-6)

    def test_ces_inner_shares_sum_to_one(self):
        from src.q2.marginal_analysis import ces_inner_shares

        shares = ces_inner_shares(self.values, self.weights, rho=-0.3)
        self.assertAlmostEqual(float(shares.sum()), 1.0, places=12)


class MissingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bundle = load_q1_input(MOCK_CSV, MOCK_METADATA, "DEVELOPMENT")
        cls.frame = normalise_abilities(bundle.frame, bundle.metadata["ability_scale"])

    def test_complete_case_excludes_missing_model(self):
        result = apply_missing_policy(self.frame, "complete_case")
        self.assertEqual(result.excluded_models, ("Model_F",))
        self.assertEqual(len(result.frame), 5)

    def test_common_dimension_drops_c5_not_models(self):
        result = apply_missing_policy(self.frame, "common_dimension")
        self.assertEqual(result.dimensions, ("C1", "C2", "C3", "C4"))
        self.assertEqual(len(result.frame), 6)
        self.assertEqual(result.label, "COMMON_DIMENSION_RESULT")

    def test_interval_propagation_bounds_rank(self):
        prior = {"C1": 0.22, "C2": 0.20, "C3": 0.18, "C4": 0.25, "C5": 0.15}
        weights = solve_scene_weights(prior, SCENES["research"], ABILITY_COLUMNS).weights
        intervals = utility_intervals(self.frame, ABILITY_COLUMNS, weights, rho=-0.2)
        self.assertEqual(len(intervals), 6)
        self.assertTrue((intervals["utility_lower"] <= intervals["utility_upper"]).all())
        self.assertTrue((intervals["best_possible_rank"] <= intervals["worst_possible_rank"]).all())


class IntegrationAndSensitivityTests(unittest.TestCase):
    def test_mock_pipeline_complete_case(self):
        result = build_q2_pipeline(MOCK_CSV, MOCK_METADATA, missing_mode="complete_case")
        self.assertEqual(result.mode, "DEVELOPMENT")
        self.assertEqual(set(result.scene_results), set(SCENES))
        self.assertIsNotNone(result.rank_migration)
        for table in result.scene_results.values():
            self.assertEqual(len(table), 5)
            self.assertTrue({"utility", "linear_utility", "pri", "rank"}.issubset(table.columns))
            self.assertFalse(table["model"].str.contains("Kimi|GPT|Claude", case=False).any())

    def test_mock_pipeline_common_dimension_resolves_weights(self):
        result = build_q2_pipeline(MOCK_CSV, MOCK_METADATA, missing_mode="common_dimension")
        for scene in SCENES:
            self.assertEqual(result.scene_dimensions[scene], ("C1", "C2", "C3", "C4"))
            self.assertEqual(len(result.scene_results[scene]), 6)
            self.assertTrue((result.scene_results[scene]["result_label"] == "COMMON_DIMENSION_RESULT").all())

    def test_sensitivity_summary_and_plots(self):
        pipeline = build_q2_pipeline(MOCK_CSV, MOCK_METADATA, missing_mode="complete_case")
        scene = SCENES["research"]
        grid = run_sensitivity_grid(
            pipeline.ability_frame,
            scene,
            ABILITY_COLUMNS,
            {"C1": 0.22, "C2": 0.20, "C3": 0.18, "C4": 0.25, "C5": 0.15},
            alpha_values=np.asarray([0.58, 0.66, 0.72]),
            rho_values=np.asarray([-0.4, 0.0, 0.2]),
        )
        summary = summarise_rank_robustness(grid)
        jumps = detect_rank_jump_thresholds(grid)
        self.assertEqual(len(grid), 5 * 3 * 3)
        self.assertEqual(len(summary), 5)
        self.assertEqual(
            list(jumps.columns),
            ["model", "scene", "rho", "alpha_from", "alpha_to", "rank_from", "rank_to", "rank_jump"],
        )
        self.assertTrue({"mean_rank", "best_rank", "worst_rank", "top3_share", "rank_std"}.issubset(summary.columns))
        surface = rank_surface(grid, "Model_A")
        with tempfile.TemporaryDirectory() as directory:
            heatmap_path = Path(directory) / "surface.png"
            migration_path = Path(directory) / "migration.png"
            fig1, _ = plot_rank_surface(surface, "Model_A", "research", heatmap_path)
            fig2, _ = plot_rank_migration(pipeline.rank_migration, migration_path)
            self.assertTrue(heatmap_path.exists())
            self.assertTrue(migration_path.exists())
            plt.close(fig1)
            plt.close(fig2)

    def test_prior_comparison_and_target_analysis(self):
        pipeline = build_q2_pipeline(MOCK_CSV, MOCK_METADATA, missing_mode="complete_case")
        q1_grid = run_sensitivity_grid(
            pipeline.ability_frame,
            SCENES["coding"],
            ABILITY_COLUMNS,
            {"C1": 0.22, "C2": 0.20, "C3": 0.18, "C4": 0.25, "C5": 0.15},
            alpha_values=np.asarray([0.60, 0.70]),
            rho_values=np.asarray([-0.3, 0.1]),
        )
        equal_grid = run_sensitivity_grid(
            pipeline.ability_frame,
            SCENES["coding"],
            ABILITY_COLUMNS,
            equal_reference(),
            alpha_values=np.asarray([0.60, 0.70]),
            rho_values=np.asarray([-0.3, 0.1]),
        )
        prior_comparison = compare_prior_robustness(q1_grid, equal_grid)
        self.assertEqual(len(prior_comparison), 5)
        weights = {scene: result.weights for scene, result in pipeline.weight_results.items()}
        target = analyze_target_model(
            pipeline.ability_frame,
            pipeline.scene_results,
            weights,
            pipeline.scene_rho,
            pipeline.scene_dimensions,
            model_name="Model_A",
            rank_migration=pipeline.rank_migration,
        )
        self.assertEqual(target["model"], "Model_A")
        self.assertIn("ces_inner_shares", target["scenes"]["research"])
        self.assertIn("marginal_utilities", target["scenes"]["research"])
        competitor = target["scenes"]["research"]["competitors"]["closest_utility"]
        comparison = compare_models(
            pipeline.ability_frame,
            "Model_A",
            competitor,
            "research",
            ABILITY_COLUMNS,
            weights["research"],
            pipeline.scene_rho["research"],
        )
        self.assertIn("ces_curvature_gap_effect", comparison)

    def test_writer_enforces_dev_directory(self):
        result = build_q2_pipeline(MOCK_CSV, MOCK_METADATA, missing_mode="complete_case")
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                write_pipeline_tables(result, Path(directory) / "outputs" / "q2" / "final")


if __name__ == "__main__":
    unittest.main()
