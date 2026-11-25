"""TV2 - Phân loại lá / đỉnh trong và đếm theo tầng."""
from algorithms.bfs import bfs_with_depths


def classify_nodes(tree, nodes=None):
    """Trả về (leaves, internal_nodes).

    Lá: không có con. Đỉnh trong: có ít nhất 1 con.
    `nodes`: tập đỉnh cần xét (mặc định: mọi đỉnh trong tree).
    """
    if nodes is None:
        nodes = tree.keys()
    leaves, internal = [], []
    for n in nodes:
        if len(tree.get(n, [])) == 0:
            leaves.append(n)
        else:
            internal.append(n)
    return leaves, internal


def count_by_level(tree, depths):
    """Đếm internal / leaf / total theo từng tầng.

    Trả về list dict, sắp theo tầng tăng dần:
    [{"level": 0, "internal": 1, "leaves": 0, "total": 1}, ...]
    """
    stats = {}
    for node, d in depths.items():
        row = stats.setdefault(d, {"level": d, "internal": 0, "leaves": 0, "total": 0})
        if len(tree.get(node, [])) == 0:
            row["leaves"] += 1
        else:
            row["internal"] += 1
        row["total"] += 1
    return [stats[k] for k in sorted(stats)]


def analyze_structure(tree, root):
    """Báo cáo tổng hợp cho giao diện và các TV khác.

    Các khóa trả về:
      order, depths, leaves, internal_nodes, by_level,
      total_nodes (V), total_internal (I), total_leaves (L),
      height (tầng sâu nhất), widest_level,
      check_V_equals_I_plus_L, check_levels_sum
    """
    order, depths = bfs_with_depths(tree, root)
    # chỉ xét các đỉnh đi tới được từ gốc
    leaves, internal = classify_nodes(tree, order)
    by_level = count_by_level(tree, depths)

    V, I, L = len(order), len(internal), len(leaves)
    widest = max(by_level, key=lambda r: r["total"])["level"]

    return {
        "order": order,
        "depths": depths,
        "leaves": leaves,
        "internal_nodes": internal,
        "by_level": by_level,
        "total_nodes": V,
        "total_internal": I,
        "total_leaves": L,
        "height": max(depths.values()),
        "widest_level": widest,
        "check_V_equals_I_plus_L": V == I + L,
        "check_levels_sum": (
            sum(r["total"] for r in by_level) == V
            and sum(r["internal"] for r in by_level) == I
            and sum(r["leaves"] for r in by_level) == L
        ),
    }
