"""Kiểm thử TV3. Chạy: pytest tests/test_statistics.py

Cây nhỏ (tính tay):
    A -> B, C ; B -> D, E ; C -> F
    Đỉnh trong: A(2) ở tầng 0; B(2), C(1) ở tầng 1
    Tầng 1: mean = 1.5, variance = 0.25, std = 0.5 (tổng thể)
Khi cài đặt xong, XÓA dòng @xfail để test chạy thật.
"""
import math

import pytest

from algorithms.bfs import get_depths
from algorithms.fanout import get_fanout, group_fanout_by_level
from algorithms.statistics import analyze_fanout, calculate_stats

SMALL = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": [], "F": []}
XF = pytest.mark.xfail(raises=NotImplementedError, reason="TV3 chưa làm")


@XF
def test_get_fanout_only_internal_nodes():
    assert get_fanout(SMALL) == {"A": 2, "B": 2, "C": 1}


@XF
def test_group_by_level():
    grouped = group_fanout_by_level(get_fanout(SMALL), get_depths(SMALL, "A"))
    assert {k: sorted(v) for k, v in grouped.items()} == {0: [2], 1: [1, 2]}


@XF
def test_stats_hand_computed():
    s = calculate_stats([1, 2])
    assert s["mean"] == 1.5 and s["variance"] == 0.25 and math.isclose(s["std"], 0.5)
    assert s["count"] == 2 and s["min"] == 1 and s["max"] == 2


@XF
def test_stats_equal_values_std_zero():
    assert calculate_stats([3, 3, 3, 3])["std"] == 0


@XF
def test_stats_single_value_std_zero():
    assert calculate_stats([5])["std"] == 0


@XF
def test_stats_one_outlier():
    s = calculate_stats([2, 2, 2, 20])
    assert s["std"] > 7


@XF
def test_stats_empty_no_division_by_zero():
    assert calculate_stats([])["count"] == 0


@XF
def test_analyze_fanout_small_tree():
    report = analyze_fanout(SMALL, get_depths(SMALL, "A"))
    lvl1 = next(r for r in report["by_level"] if r["level"] == 1)
    assert lvl1["mean"] == 1.5 and math.isclose(lvl1["std"], 0.5)


@XF
def test_tree_only_root_has_no_internal_below():
    # cây chỉ có gốc: gốc là lá, không có đỉnh trong -> không được chia cho 0
    analyze_fanout({"A": []}, {"A": 0})
