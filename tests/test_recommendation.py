"""Kiểm thử TV5. Chạy: pytest tests/test_recommendation.py"""
import copy

import pytest

from algorithms.rebalance import (
    describe_plan,
    detect_imbalanced_branches,
    evaluate_before_after,
    level_bands,
    propose_plan,
    simulate_reorganization,
    validate_reorganization,
)
from backend.services.model_service import load_tree_from_csv
from backend.services.recommendation_service import run_recommendation

# CN_A có 6 bến, CN_B và CN_C chỉ có 1 bến -> CN_A lệch
LOPSIDED = {
    "ROOT": ["CN_A", "CN_B", "CN_C"],
    "CN_A": ["S1", "S2", "S3", "S4", "S5", "S6"],
    "CN_B": ["S7"],
    "CN_C": ["S8"],
    **{f"S{i}": [] for i in range(1, 9)},
}


def _stations(tree):
    return sorted(n for n, ch in tree.items() if not ch)


def test_no_branch_exceeds_threshold():
    balanced = {"ROOT": ["A", "B"], "A": ["S1", "S2"], "B": ["S3", "S4"],
                **{f"S{i}": [] for i in range(1, 5)}}
    assert detect_imbalanced_branches(balanced, {}, 1.5) == []


def test_only_one_branch_flagged():
    flagged = detect_imbalanced_branches(LOPSIDED, {}, 1.0)
    assert [b["id"] for b in flagged] == ["CN_A"]


def test_simulate_keeps_original_unchanged_and_keeps_stations():
    original = copy.deepcopy(LOPSIDED)
    plan = [{"op": "move", "node": "S6", "new_parent": "CN_B"}]
    new_tree = simulate_reorganization(LOPSIDED, plan)
    assert LOPSIDED == original
    assert _stations(new_tree) == _stations(LOPSIDED)


def test_validate_detects_lost_station():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_A"].remove("S6")
    del bad["S6"]
    assert validate_reorganization(LOPSIDED, bad)["ok"] is False


def test_validate_detects_duplicate_parent():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_B"].append("S1")          # S1 có hai cha
    assert validate_reorganization(LOPSIDED, bad)["ok"] is False


def test_validate_detects_cycle():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_B"].append("CN_A")
    bad["ROOT"].remove("CN_A")
    bad["CN_A"].append("CN_B")        # CN_A <-> CN_B
    assert validate_reorganization(LOPSIDED, bad)["ok"] is False


# ---------------------------------------------------------------------------
# Bổ sung: biên, merge/split, validate, đánh giá, service, dữ liệu thật
# ---------------------------------------------------------------------------
def test_detect_uses_fanout_report_when_given():
    from backend.services.statistics_service import run_fanout_analysis
    report = run_fanout_analysis(LOPSIDED, "ROOT")
    assert [b["id"] for b in detect_imbalanced_branches(LOPSIDED, report, 1.0)] == ["CN_A"]


def test_detect_flagged_fields_and_direction():
    b = detect_imbalanced_branches(LOPSIDED, {}, 1.0)[0]
    assert b["direction"] == "high" and b["level"] == 1 and b["fanout"] == 6
    assert b["z_score"] > 1.0 and "6" in b["reason"]


def test_detect_low_branch():
    tree = {"R": ["A", "B", "C", "D"], "A": ["1", "2", "3", "4", "5", "6"], "B": ["7", "8", "9", "10", "11", "12"],
            "C": ["13", "14", "15", "16", "17", "18"], "D": ["19"], **{str(i): [] for i in range(1, 20)}}
    flagged = detect_imbalanced_branches(tree, {}, 1.0)
    assert [(b["id"], b["direction"]) for b in flagged] == [("D", "low")]


def test_detect_root_only_and_negative_k():
    assert detect_imbalanced_branches({"R": []}, {}, 1.0) == []
    with pytest.raises(ValueError):
        detect_imbalanced_branches(LOPSIDED, {}, -1)


def test_split_creates_sibling_and_keeps_stations():
    plan = [{"op": "split", "node": "CN_A", "new_node": "CN_A2", "move_children": ["S4", "S5", "S6"]}]
    new_tree = simulate_reorganization(LOPSIDED, plan)
    assert new_tree["CN_A"] == ["S1", "S2", "S3"] and new_tree["CN_A2"] == ["S4", "S5", "S6"]
    assert "CN_A2" in new_tree["ROOT"]
    assert validate_reorganization(LOPSIDED, new_tree)["ok"] is True


def test_merge_moves_children_and_removes_node():
    new_tree = simulate_reorganization(LOPSIDED, [{"op": "merge", "node": "CN_B", "into": "CN_C"}])
    assert "CN_B" not in new_tree and new_tree["CN_C"] == ["S8", "S7"]
    assert new_tree["ROOT"] == ["CN_A", "CN_C"]
    assert validate_reorganization(LOPSIDED, new_tree)["ok"] is True


def test_simulate_rejects_bad_references():
    for plan in (
        [{"op": "move", "node": "NOPE", "new_parent": "CN_B"}],
        [{"op": "move", "node": "S1", "new_parent": "NOPE"}],
        [{"op": "move", "node": "ROOT", "new_parent": "CN_B"}],
        [{"op": "split", "node": "CN_A", "new_node": "CN_B", "move_children": ["S1"]}],
        [{"op": "split", "node": "CN_A", "new_node": "X", "move_children": ["S7"]}],
        [{"op": "merge", "node": "CN_B", "into": "CN_B"}],
        [{"op": "explode"}],
    ):
        with pytest.raises(ValueError):
            simulate_reorganization(LOPSIDED, plan)


def test_empty_plan_returns_equal_copy():
    new_tree = simulate_reorganization(LOPSIDED, [])
    assert new_tree == LOPSIDED and new_tree is not LOPSIDED


def test_describe_plan_has_old_and_new_parent():
    rows = describe_plan(LOPSIDED, [{"op": "move", "node": "S6", "new_parent": "CN_B", "reason": "test"}])
    assert rows == [{"step": 1, "op": "move", "unit": "S6", "old_parent": "CN_A",
                     "new_parent": "CN_B", "reason": "test"}]


def test_validate_detects_cycle_made_by_simulation():
    bad = simulate_reorganization(LOPSIDED, [{"op": "move", "node": "CN_A", "new_parent": "S1"}])
    result = validate_reorganization(LOPSIDED, bad)
    assert result["ok"] is False and any("liên thông" in e or "chu trình" in e for e in result["errors"])


def test_validate_detects_two_roots_and_emptied_branch():
    two_roots = copy.deepcopy(LOPSIDED)
    two_roots["ROOT"].remove("CN_C")
    assert validate_reorganization(LOPSIDED, two_roots)["ok"] is False
    emptied = simulate_reorganization(LOPSIDED, [{"op": "move", "node": "S7", "new_parent": "CN_A"}])
    result = validate_reorganization(LOPSIDED, emptied)          # CN_B thành lá
    assert result["ok"] is False and any("CN_B" in e for e in result["errors"])


def test_validate_ok_for_unchanged_tree_and_counts_stations():
    result = validate_reorganization(LOPSIDED, copy.deepcopy(LOPSIDED))
    assert result["ok"] and result["stations_before"] == result["stations_after"] == 8


def test_propose_plan_splits_lopsided_branch():
    flagged = detect_imbalanced_branches(LOPSIDED, {}, 1.0)
    plan = propose_plan(LOPSIDED, flagged, {}, 1.0)
    assert len(plan) == 1 and plan[0]["op"] == "split" and plan[0]["node"] == "CN_A"
    new_tree = simulate_reorganization(LOPSIDED, plan)
    assert validate_reorganization(LOPSIDED, new_tree)["ok"]
    assert max(len(ch) for ch in new_tree.values()) < 6


def test_propose_plan_empty_when_nothing_flagged():
    assert propose_plan(LOPSIDED, [], {}, 1.0) == []


def _report(tree, root, imbalanced=None):
    from backend.services.analysis_service import run_analysis
    from backend.services.statistics_service import run_fanout_analysis
    return {"structure": run_analysis(tree, root), "fanout": run_fanout_analysis(tree, root),
            "imbalanced_count": imbalanced}


def test_evaluate_reports_tradeoff_not_plain_better():
    plan = [{"op": "split", "node": "CN_A", "new_node": "CN_A2", "move_children": ["S4", "S5", "S6"]}]
    new_tree = simulate_reorganization(LOPSIDED, plan)
    out = evaluate_before_after(_report(LOPSIDED, "ROOT", 1), _report(new_tree, "ROOT", 0))
    assert out["conserved"] and out["improved_balance"] and out["cost_increase"]   # thêm 1 đỉnh trong
    assert "đánh đổi" in out["verdict"].lower()


def test_evaluate_detects_station_count_change():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_A"].remove("S6")
    del bad["S6"]
    out = evaluate_before_after(_report(LOPSIDED, "ROOT"), _report(bad, "ROOT"))
    assert out["conserved"] is False


def test_evaluate_no_change():
    out = evaluate_before_after(_report(LOPSIDED, "ROOT", 1), _report(LOPSIDED, "ROOT", 1))
    assert not out["improved_balance"] and not out["cost_increase"]


def test_service_keeps_original_and_returns_all_keys():
    original = copy.deepcopy(LOPSIDED)
    res = run_recommendation(LOPSIDED, "ROOT", threshold=1.0)
    assert LOPSIDED == original
    for key in ("imbalanced", "plan", "plan_rows", "new_tree", "validation", "before", "after", "comparison"):
        assert key in res
    assert res["validation"]["ok"] and res["comparison"]["improved_balance"]


def test_service_no_imbalance_gives_empty_plan():
    balanced = {"ROOT": ["A", "B"], "A": ["S1", "S2"], "B": ["S3", "S4"], **{f"S{i}": [] for i in range(1, 5)}}
    res = run_recommendation(balanced, "ROOT", threshold=1.5)
    assert res["imbalanced"] == [] and res["plan"] == [] and res["new_tree"] == balanced


def test_service_invalid_manual_plan_stops_analysis():
    res = run_recommendation(LOPSIDED, "ROOT", plan=[{"op": "move", "node": "CN_A", "new_parent": "S1"}])
    assert res["validation"]["ok"] is False and res["after"] is None and res["comparison"] is None


def test_service_uses_names_for_new_units():
    info = {k: {"name": f"Đơn vị {k}", "type": "BRANCH", "parent_id": None} for k in LOPSIDED}
    res = run_recommendation(LOPSIDED, "ROOT", threshold=1.0, info=info)
    new_id = res["plan"][0]["new_node"]
    assert res["names"][new_id] == "Đơn vị CN_A (tách 2)"


def test_real_dataset_scenario_before_after():
    data = load_tree_from_csv("data/organization.csv")
    tree, root = data["tree"], data["root"]
    original = copy.deepcopy(tree)
    res = run_recommendation(tree, root, threshold=1.5)
    assert tree == original
    assert "CN_MN_HCM" in [b["id"] for b in res["imbalanced"]]       # chi nhánh 15 bến
    assert res["validation"]["ok"] and res["validation"]["stations_after"] == 61
    cmp_ = res["comparison"]
    assert cmp_["improved_balance"]
    rows = {r["key"]: r for r in cmp_["table"]}
    assert rows["max_fanout"]["before"] == 15 and rows["max_fanout"]["after"] < 15
    assert rows["height"]["after"] == rows["height"]["before"]       # tách cùng cấp, không thêm tầng
    assert rows["std"]["after"] < rows["std"]["before"]


def test_level_bands_matches_report():
    from backend.services.statistics_service import run_fanout_analysis
    bands = level_bands(LOPSIDED, run_fanout_analysis(LOPSIDED, "ROOT"), root="ROOT")
    assert bands[1][0] == pytest.approx(8 / 3)
    assert bands == level_bands(LOPSIDED, {})
