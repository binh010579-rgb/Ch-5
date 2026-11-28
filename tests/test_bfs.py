import pytest
from algorithms.bfs import bfs, get_depths, bfs_trace, bfs_operation_count
from algorithms.leaf_analysis import classify_nodes, count_by_level, analyze_structure
from backend.services.analysis_service import run_analysis, extract_subtree

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


# ---- Minh họa từng bước và kiểm chứng độ phức tạp O(V + E) ----

def test_trace_matches_bfs_order():
    steps = bfs_trace(SMALL, "A")
    assert [s["current"] for s in steps] == bfs(SMALL, "A")
    assert steps[-1]["visited_order"] == bfs(SMALL, "A")
    assert steps[-1]["queue"] == []


def test_trace_by_hand():
    steps = bfs_trace(SMALL, "A")
    # bước 1: lấy A (tầng 0), thêm B, C
    assert steps[0] == {"step": 1, "current": "A", "depth": 0, "added": ["B", "C"],
                        "queue": ["B", "C"], "visited_order": ["A"]}
    # bước 2: lấy B (tầng 1), thêm D, E; hàng đợi còn C, D, E
    assert steps[1]["added"] == ["D", "E"] and steps[1]["queue"] == ["C", "D", "E"]
    # bước 3: lấy C, thêm F
    assert steps[2]["current"] == "C" and steps[2]["queue"] == ["D", "E", "F"]


def test_trace_depth_never_decreases():
    depths = [s["depth"] for s in bfs_trace(SMALL, "A")]
    assert depths == sorted(depths)  # BFS thăm theo tầng tăng dần


def test_root_is_level_zero():
    assert get_depths(SMALL, "A")["A"] == 0
    assert get_depths({"R": []}, "R") == {"R": 0}


def test_operation_count_is_v_plus_e():
    pops, edges = bfs_operation_count(SMALL, "A")
    V = len(SMALL)
    E = sum(len(c) for c in SMALL.values())
    assert pops == V and edges == E == V - 1  # cây: E = V - 1


def test_linear_growth_on_chain():
    # số thao tác tăng tuyến tính theo V (không bình phương)
    for n in (10, 100, 1000):
        t = {i: [i + 1] for i in range(n - 1)}
        t[n - 1] = []
        pops, edges = bfs_operation_count(t, 0)
        assert pops + edges == 2 * n - 1


def test_trace_bad_root():
    with pytest.raises(ValueError):
        bfs_trace(SMALL, "X")


def test_service_sample_and_complexity():
    from backend.services.analysis_service import SAMPLE_TREE, sample_trace, complexity_report
    assert [x["current"] for x in sample_trace()] == ["A", "B", "C", "D", "E", "F"]
    r = complexity_report(SAMPLE_TREE, "A")
    assert r["V"] == 6 and r["E"] == 5 and r["total_ops"] == 11 and r["check"]
