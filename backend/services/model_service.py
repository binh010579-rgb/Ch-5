"""TV4 – Service so sánh mô hình cây m-phân đầy đủ.

Luồng: nhận cây hợp lệ (TV1) -> lấy số liệu thực tế (leaf/internal/height/max_fanout)
-> gọi algorithms.m_ary_tree -> trả bảng/báo cáo cho giao diện.

Quy ước cây dùng chung: tree[node_id] = danh sách id các con (lá có danh sách rỗng),
gốc ở tầng 0.

LƯU Ý TÍCH HỢP: hàm summarize_actual() bên dưới là bản tối thiểu để module TV4 chạy độc lập.
Khi TV2 hoàn thành analyze_structure(), chỉ cần truyền kết quả của TV2 vào
compare_models(actual_summary=...) – các khóa cần có được ghi ở compare_models().
"""

from __future__ import annotations

import csv
from typing import Any, Dict, Iterable, List, Optional

from algorithms.m_ary_tree import (
    compare_actual_model,
    explain_reference_model,
    prove_relation,
    suggest_m_values,
    valid_m_values,
)


# --------------------------------------------------------------------------- #
# Số liệu thực tế (bản tối thiểu, dùng DFS bằng stack để an toàn với cây sâu)
# --------------------------------------------------------------------------- #
def summarize_actual(tree: Dict[str, List[str]], root: str) -> Dict[str, Any]:
    """Tính L, I, V, height, max_fanout của cây thực tế."""
    if root not in tree:
        raise ValueError(f"Gốc '{root}' không có trong cây")

    leaves = internal = 0
    height = 0
    max_fanout = 0
    visited = 0
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        visited += 1
        children = tree.get(node, [])
        height = max(height, depth)
        if children:
            internal += 1
            max_fanout = max(max_fanout, len(children))
            for child in children:
                stack.append((child, depth + 1))
        else:
            leaves += 1

    return {
        "leaf_count": leaves,
        "internal_count": internal,
        "total_nodes": visited,
        "height": height,
        "max_fanout": max_fanout,
        "avg_fanout": (visited - 1) / internal if internal else 0.0,
    }


def load_tree_from_csv(path: str) -> Dict[str, Any]:
    """Đọc CSV (id,name,type,parent_id) thành cây. Chỉ dùng khi chạy độc lập;
    khi tích hợp, cây phải lấy từ tree_service của TV1 (đã được validate)."""
    children: Dict[str, List[str]] = {}
    names: Dict[str, str] = {}
    roots: List[str] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            node_id = row["id"].strip()
            parent = (row.get("parent_id") or "").strip()
            names[node_id] = row.get("name", node_id)
            children.setdefault(node_id, [])
            if parent:
                children.setdefault(parent, []).append(node_id)
            else:
                roots.append(node_id)
    if len(roots) != 1:
        raise ValueError(f"Dữ liệu phải có đúng 1 gốc, tìm thấy {len(roots)}: {roots}")
    return {"tree": children, "root": roots[0], "names": names}


# --------------------------------------------------------------------------- #
# Service chính cho giao diện
# --------------------------------------------------------------------------- #
def compare_models(
    actual_summary: Dict[str, Any], m_values: Optional[Iterable[int]] = None
) -> Dict[str, Any]:
    """So sánh số liệu thực tế với nhiều giá trị m.

    actual_summary cần: leaf_count (bắt buộc); internal_count, height, max_fanout (tùy chọn
    nhưng nên có để có đủ bảng so sánh).
    """
    suggestions = suggest_m_values(actual_summary)
    if m_values is None:
        m_values = [s["m"] for s in suggestions]
    m_list = list(dict.fromkeys(m_values))  # bỏ trùng, giữ thứ tự

    reports = [compare_actual_model(actual_summary, m) for m in m_list]
    reasons = {s["m"]: s["reason"] for s in suggestions}

    rows = []
    for r in reports:
        # Giá trị thiếu để None (giao diện tự hiển thị "—"), tránh cột lẫn số/chuỗi.
        rows.append(
            {
                "m": r["m"],
                "Lý do chọn": reasons.get(r["m"], "Do người dùng chọn."),
                "L": r["L"],
                "I lý thuyết": r["I_theory"],
                "I thực tế": r["I_actual"],
                "Chênh lệch I": r["I_diff"],
                "h tối thiểu": r["h_min"],
                "h thực tế": r["h_actual"],
                "Chênh lệch h": r["h_diff"],
                "Cây thực tế là m-phân?": (
                    None if r["is_m_ary"] is None else ("Có" if r["is_m_ary"] else "Không")
                ),
                "Trạng thái": r["status"],
            }
        )

    return {
        "actual": actual_summary,
        "reports": reports,
        "table": rows,
        "valid_m": valid_m_values(actual_summary["leaf_count"]),
        "proof": prove_relation(),
        "reference_note": explain_reference_model(),
    }


def compare_from_tree(
    tree: Dict[str, List[str]], root: str, m_values: Optional[Iterable[int]] = None
) -> Dict[str, Any]:
    """Tiện ích: từ cây -> số liệu thực tế -> so sánh."""
    return compare_models(summarize_actual(tree, root), m_values)
