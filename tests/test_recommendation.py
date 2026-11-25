"""Kiểm thử TV5. Chạy: pytest tests/test_recommendation.py
Khi cài đặt xong, XÓA dòng @xfail để test chạy thật."""
import copy

import pytest

from algorithms.rebalance import (
    detect_imbalanced_branches,
    simulate_reorganization,
    validate_reorganization,
)

XF = pytest.mark.xfail(raises=NotImplementedError, reason="TV5 chưa làm")

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


@XF
def test_no_branch_exceeds_threshold():
    balanced = {"ROOT": ["A", "B"], "A": ["S1", "S2"], "B": ["S3", "S4"],
                **{f"S{i}": [] for i in range(1, 5)}}
    assert detect_imbalanced_branches(balanced, {}, 1.5) == []


@XF
def test_only_one_branch_flagged():
    flagged = detect_imbalanced_branches(LOPSIDED, {}, 1.0)
    assert [b["id"] for b in flagged] == ["CN_A"]


@XF
def test_simulate_keeps_original_unchanged_and_keeps_stations():
    original = copy.deepcopy(LOPSIDED)
    plan = [{"op": "move", "node": "S6", "new_parent": "CN_B"}]
    new_tree = simulate_reorganization(LOPSIDED, plan)
    assert LOPSIDED == original
    assert _stations(new_tree) == _stations(LOPSIDED)


@XF
def test_validate_detects_lost_station():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_A"].remove("S6")
    del bad["S6"]
    assert validate_reorganization(LOPSIDED, bad)["ok"] is False


@XF
def test_validate_detects_duplicate_parent():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_B"].append("S1")          # S1 có hai cha
    assert validate_reorganization(LOPSIDED, bad)["ok"] is False


@XF
def test_validate_detects_cycle():
    bad = copy.deepcopy(LOPSIDED)
    bad["CN_B"].append("CN_A")
    bad["ROOT"].remove("CN_A")
    bad["CN_A"].append("CN_B")        # CN_A <-> CN_B
    assert validate_reorganization(LOPSIDED, bad)["ok"] is False
