"""Kiểm thử TV4 – chạy bằng:  python -m unittest tests.test_model -v   (hoặc pytest)."""

import math
import os
import unittest

from algorithms.m_ary_tree import (
    calculate_internal_nodes,
    compare_actual_model,
    minimum_height,
    prove_relation,
    suggest_m_values,
    valid_m_values,
)
from backend.services.model_service import (
    compare_from_tree,
    compare_models,
    load_tree_from_csv,
    summarize_actual,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(ROOT_DIR, "data", "organization.csv")


def build_full_m_ary_tree(m, internal_count):
    """Dựng cây m-phân đầy đủ thật: lần lượt biến một lá thành đỉnh trong có m con."""
    tree = {"n0": []}
    leaves = ["n0"]
    counter = 1
    for _ in range(internal_count):
        node = leaves.pop(0)
        kids = []
        for _ in range(m):
            kid = f"n{counter}"
            counter += 1
            tree[kid] = []
            kids.append(kid)
        tree[node] = kids
        leaves.extend(kids)
    return tree


class TestCalculateInternalNodes(unittest.TestCase):
    def test_m2_m3_m4(self):
        # L = (m-1)I + 1  ->  I = (L-1)/(m-1)
        self.assertEqual(calculate_internal_nodes(61, 2)["I"], 60)
        self.assertEqual(calculate_internal_nodes(61, 3)["I"], 30)
        self.assertEqual(calculate_internal_nodes(61, 4)["I"], 20)

    def test_total_nodes_and_edges(self):
        r = calculate_internal_nodes(61, 4)
        self.assertEqual(r["V"], r["I"] + r["L"])
        self.assertEqual(r["V"], 4 * r["I"] + 1)  # V = m*I + 1
        self.assertEqual(r["E"], r["V"] - 1)
        self.assertEqual(r["E"], 4 * r["I"])      # E = m*I (cách đếm thứ hai)

    def test_single_leaf(self):
        # L = 1: cây chỉ có gốc, I = 0 với mọi m > 1
        for m in (2, 3, 4):
            r = calculate_internal_nodes(1, m)
            self.assertEqual(r["status"], "ok")
            self.assertEqual(r["I"], 0)
            self.assertEqual(r["V"], 1)

    def test_not_integer_is_not_rounded(self):
        r = calculate_internal_nodes(60, 4)  # (60-1)/(4-1) = 59/3
        self.assertEqual(r["status"], "not_integer")
        self.assertIsNone(r["I"])
        self.assertIsNone(r["V"])
        self.assertIn("không", r["message"])

    def test_invalid_m(self):
        for m in (1, 0, -3):
            r = calculate_internal_nodes(61, m)
            self.assertEqual(r["status"], "invalid_m")
            self.assertIsNone(r["I"])

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            calculate_internal_nodes(0, 2)
        with self.assertRaises(ValueError):
            calculate_internal_nodes(-5, 2)
        with self.assertRaises(TypeError):
            calculate_internal_nodes(61.0, 2)
        with self.assertRaises(TypeError):
            calculate_internal_nodes(61, "2")
        with self.assertRaises(TypeError):
            calculate_internal_nodes(True, 2)

    def test_formula_matches_real_trees(self):
        # Đối chiếu công thức bằng cây dựng thật và đếm cạnh hai cách
        for m in (2, 3, 4, 5):
            for internal in (0, 1, 2, 7, 20):
                tree = build_full_m_ary_tree(m, internal)
                s = summarize_actual(tree, "n0")
                edges_by_parent = sum(len(c) for c in tree.values())
                self.assertEqual(edges_by_parent, len(tree) - 1)   # E = V - 1
                self.assertEqual(edges_by_parent, m * s["internal_count"])  # E = mI
                self.assertEqual(s["leaf_count"], (m - 1) * s["internal_count"] + 1)
                r = calculate_internal_nodes(s["leaf_count"], m)
                self.assertEqual(r["I"], s["internal_count"])


class TestMinimumHeight(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(minimum_height(61, 2), 6)   # 2^5=32 < 61 <= 64=2^6
        self.assertEqual(minimum_height(61, 3), 4)   # 3^3=27 < 61 <= 81=3^4
        self.assertEqual(minimum_height(61, 4), 3)   # 4^2=16 < 61 <= 64=4^3

    def test_single_leaf_is_zero(self):
        self.assertEqual(minimum_height(1, 2), 0)

    def test_exact_powers_and_one_over(self):
        for m in (2, 3, 4, 10):
            for h in range(0, 6):
                self.assertEqual(minimum_height(m ** h, m), h)
                self.assertEqual(minimum_height(m ** h + 1, m), h + 1)

    def test_no_floating_point_error(self):
        # math.log(1000, 10) = 2.9999999999999996 -> ceil sẽ cho kết quả sai nếu dùng log
        self.assertEqual(minimum_height(1000, 10), 3)
        self.assertEqual(minimum_height(243, 3), 5)
        self.assertEqual(minimum_height(2 ** 40, 2), 40)

    def test_matches_ceil_log_when_safe(self):
        for m in (2, 3, 4, 5):
            for L in range(1, 300):
                if abs(math.log(L, m) - round(math.log(L, m))) > 1e-9:
                    self.assertEqual(minimum_height(L, m), math.ceil(math.log(L, m)))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            minimum_height(61, 1)
        with self.assertRaises(ValueError):
            minimum_height(0, 2)

    def test_bound_holds_for_real_m_ary_trees(self):
        # Với cây m-phân thật: L <= m^h và h >= h_min
        for m in (2, 3, 4):
            for internal in (1, 3, 10, 25):
                tree = build_full_m_ary_tree(m, internal)
                s = summarize_actual(tree, "n0")
                self.assertLessEqual(s["leaf_count"], m ** s["height"])
                self.assertGreaterEqual(s["height"], minimum_height(s["leaf_count"], m))


class TestCompare(unittest.TestCase):
    def setUp(self):
        self.actual = {
            "leaf_count": 61, "internal_count": 14, "height": 3, "max_fanout": 15,
        }

    def test_report_values(self):
        r = compare_actual_model(self.actual, 4)
        self.assertEqual(r["I_theory"], 20)
        self.assertEqual(r["I_diff"], 14 - 20)
        self.assertEqual(r["h_min"], 3)
        self.assertEqual(r["h_diff"], 0)
        self.assertFalse(r["is_m_ary"])  # fan-out 15 > 4

    def test_warns_when_actual_is_not_m_ary(self):
        r = compare_actual_model(self.actual, 2)
        self.assertTrue(any("KHÔNG phải cây" in n for n in r["notes"]))
        # h thực tế (3) < h_min (6) là hợp lệ vì cây thực tế không phải nhị phân
        self.assertLess(r["h_diff"], 0)

    def test_not_integer_case(self):
        r = compare_actual_model({"leaf_count": 60, "internal_count": 14}, 4)
        self.assertEqual(r["status"], "not_integer")
        self.assertIsNone(r["I_theory"])
        self.assertIsNone(r["I_diff"])
        self.assertEqual(r["h_min"], 3)  # cận tầng vẫn tính được

    def test_missing_optional_fields(self):
        r = compare_actual_model({"leaf_count": 61}, 3)
        self.assertEqual(r["I_theory"], 30)
        self.assertIsNone(r["I_diff"])
        self.assertIsNone(r["h_diff"])
        self.assertIsNone(r["is_m_ary"])

    def test_missing_leaf_count(self):
        with self.assertRaises(KeyError):
            compare_actual_model({"internal_count": 3}, 2)

    def test_invalid_m_in_compare(self):
        r = compare_actual_model(self.actual, 1)
        self.assertEqual(r["status"], "invalid_m")
        self.assertIsNone(r["h_min"])

    def test_actual_equals_model(self):
        tree = build_full_m_ary_tree(3, 10)
        r = compare_from_tree(tree, "n0", [3])["reports"][0]
        self.assertEqual(r["I_diff"], 0)
        self.assertTrue(r["is_m_ary"])

    def test_valid_m_values(self):
        self.assertEqual(valid_m_values(61, 7), [2, 3, 4, 5, 6, 7])
        self.assertEqual(valid_m_values(60, 6), [2])  # L-1 = 59 nguyên tố nên chỉ m=2
        self.assertEqual(valid_m_values(1, 5), [2, 3, 4, 5])

    def test_suggestions_include_defaults(self):
        ms = [s["m"] for s in suggest_m_values(self.actual)]
        self.assertTrue({2, 3, 4}.issubset(ms))
        self.assertTrue(all(s["reason"] for s in suggest_m_values(self.actual)))


class TestProof(unittest.TestCase):
    def test_proof_mentions_both_counts(self):
        text = prove_relation()
        self.assertIn("E = V − 1", text)
        self.assertIn("E = m·I", text)
        self.assertIn("(m − 1)·I + 1", text)
        self.assertIn("⌈log_m L⌉", text)


class TestSampleData(unittest.TestCase):
    def test_sample_dataset_satisfies_requirements(self):
        data = load_tree_from_csv(SAMPLE_CSV)
        s = summarize_actual(data["tree"], data["root"])
        self.assertGreaterEqual(s["leaf_count"], 60)
        self.assertIn(s["height"], (2, 3, 4))
        self.assertEqual(s["total_nodes"], s["internal_count"] + s["leaf_count"])
        self.assertEqual(s["total_nodes"], len(data["tree"]))      # thăm đủ, không sót
        self.assertEqual(s["leaf_count"], 61)
        self.assertEqual(s["internal_count"], 14)
        # phân bổ không đều: fan-out lớn nhất khác xa trung bình
        self.assertGreater(s["max_fanout"], 2 * s["avg_fanout"])

    def test_service_output_shape(self):
        data = load_tree_from_csv(SAMPLE_CSV)
        out = compare_from_tree(data["tree"], data["root"], [2, 3, 4])
        self.assertEqual(len(out["table"]), 3)
        self.assertEqual([r["I lý thuyết"] for r in out["table"]], [60, 30, 20])
        self.assertEqual([r["h tối thiểu"] for r in out["table"]], [6, 4, 3])
        self.assertTrue(out["proof"])

    def test_deep_chain_does_not_hit_recursion_limit(self):
        n = 5000
        tree = {f"n{i}": [f"n{i + 1}"] for i in range(n)}
        tree[f"n{n}"] = []
        s = summarize_actual(tree, "n0")
        self.assertEqual(s["height"], n)
        self.assertEqual(s["leaf_count"], 1)

    def test_duplicate_m_values_removed(self):
        out = compare_models({"leaf_count": 61}, [2, 2, 3])
        self.assertEqual([r["m"] for r in out["table"]], [2, 3])


if __name__ == "__main__":
    unittest.main()
