"""TV2 - Service phân tích cấu trúc (gọi thuật toán, trả kết quả cho giao diện)."""
from algorithms.bfs import bfs, bfs_trace, bfs_operation_count
from algorithms.leaf_analysis import analyze_structure


def extract_subtree(tree, node):
    """Lấy cây con có gốc là `node` (dùng BFS để gom các đỉnh)."""
    if node not in tree:
        raise ValueError(f"Đơn vị '{node}' không tồn tại")
    nodes = bfs(tree, node)
    return {n: list(tree.get(n, [])) for n in nodes}


def run_analysis(tree, root, subtree_root=None):
    """Phân tích toàn cây hoặc cây con của một chi nhánh.

    Với cây con, tầng tính lại từ 0 tại chi nhánh được chọn.
    """
    if not tree:
        raise ValueError("Cây rỗng")
    if subtree_root and subtree_root != root:
        tree = extract_subtree(tree, subtree_root)
        root = subtree_root
    return analyze_structure(tree, root)


def level_table_rows(report):
    """Chuyển by_level thành bảng (list dict, tiêu đề tiếng Việt) để hiển thị."""
    return [
        {
            "Tầng": r["level"],
            "Đỉnh trong": r["internal"],
            "Lá": r["leaves"],
            "Tổng": r["total"],
        }
        for r in report["by_level"]
    ]


# Cây mẫu nhỏ để minh họa BFS từng bước (độc lập với dữ liệu thật)
SAMPLE_TREE = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": [], "F": []}


def sample_trace():
    """Các bước BFS trên cây mẫu A, B, C, D, E, F."""
    return bfs_trace(SAMPLE_TREE, "A")


def complexity_report(tree, root):
    """Số thao tác thực tế của BFS trên cây đang xét, để đối chiếu với V + E."""
    pops, edges = bfs_operation_count(tree, root)
    return {"V": pops, "E": edges, "pops": pops, "edges_examined": edges,
            "total_ops": pops + edges, "check": edges == pops - 1}
