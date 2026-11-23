import pytest
from algorithms.bfs import bfs, get_depths
from algorithms.leaf_analysis import classify_nodes, count_by_level, analyze_structure
from services.analysis_service import run_analysis, extract_subtree

# A
# ├─ B ─ D, E
# └─ C ─ F
SMALL = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": [], "F": []}


def test_only_root():
    t = {"R": []}
    r = analyze_structure(t, "R")
    assert r["leaves"] == ["R"] and r["internal_nodes"] == []
    assert r["total_nodes"] == 1 and r["height"] == 0


def test_chain():
    t = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    assert bfs(t, "A") == ["A", "B", "C", "D"]
    assert get_depths(t, "A") == {"A": 0, "B": 1, "C": 2, "D": 3}
    r = analyze_structure(t, "A")
    assert r["total_internal"] == 3 and r["total_leaves"] == 1


def test_bfs_order_by_hand():
    assert bfs(SMALL, "A") == ["A", "B", "C", "D", "E", "F"]


def test_depths():
    assert get_depths(SMALL, "A") == {"A": 0, "B": 1, "C": 1, "D": 2, "E": 2, "F": 2}


def test_each_node_visited_once():
    order = bfs(SMALL, "A")
    assert len(order) == len(set(order)) == len(SMALL)


def test_count_by_level():
    rows = count_by_level(SMALL, get_depths(SMALL, "A"))
    assert rows == [
        {"level": 0, "internal": 1, "leaves": 0, "total": 1},
        {"level": 1, "internal": 2, "leaves": 0, "total": 2},
        {"level": 2, "internal": 0, "leaves": 3, "total": 3},
    ]


def test_leaves_at_different_levels():
    t = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}  # lá C ở tầng 1, D ở tầng 2
    rows = count_by_level(t, get_depths(t, "A"))
    assert rows[1] == {"level": 1, "internal": 1, "leaves": 1, "total": 2}


def test_v_equals_i_plus_l_and_sums():
    r = analyze_structure(SMALL, "A")
    assert r["total_nodes"] == r["total_internal"] + r["total_leaves"] == 6
    assert r["check_V_equals_I_plus_L"] and r["check_levels_sum"]


def test_classify():
    leaves, internal = classify_nodes(SMALL)
    assert sorted(leaves) == ["D", "E", "F"]
    assert sorted(internal) == ["A", "B", "C"]


def test_subtree():
    sub = extract_subtree(SMALL, "B")
    assert set(sub) == {"B", "D", "E"}
    r = run_analysis(SMALL, "A", subtree_root="B")
    assert r["height"] == 1 and r["total_leaves"] == 2


def test_bad_root():
    with pytest.raises(ValueError):
        bfs(SMALL, "X")


def test_big_tree_60_leaves():
    # gốc -> 4 chi nhánh -> mỗi chi nhánh 15 bến
    t = {"HQ": [f"CN{i}" for i in range(4)]}
    for i in range(4):
        t[f"CN{i}"] = [f"B{i}_{j}" for j in range(15)]
        for j in range(15):
            t[f"B{i}_{j}"] = []
    r = analyze_structure(t, "HQ")
    assert r["total_leaves"] == 60 and r["total_internal"] == 5
    assert r["check_V_equals_I_plus_L"]
