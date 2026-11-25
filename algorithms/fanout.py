"""TV3 - Fan-out của đỉnh trong và thống kê theo tầng.

Quy ước chung: tree[node_id] = [id các con]; lá có []; gốc ở tầng 0.
Không gọi Streamlit / SQLite trong file này.

Đầu vào lấy từ TV1/TV2:
    tree   : dict từ backend.services.tree_service.get_valid_tree()
    depths : dict {node_id: tầng} từ algorithms.bfs.get_depths(tree, root)
"""


def get_fanout(tree):
    """Trả về {node_id: số con trực tiếp} CHỈ cho đỉnh trong (đỉnh có >= 1 con).

    TODO (TV3): cài đặt. Độ phức tạp O(V).
    """
    raise NotImplementedError("TV3 chưa cài đặt get_fanout")


def group_fanout_by_level(fanout, depths):
    """Nhóm fan-out theo tầng của đỉnh cha.

    Trả về {level: [fan-out của các đỉnh trong ở tầng đó]}.
    TODO (TV3): cài đặt.
    """
    raise NotImplementedError("TV3 chưa cài đặt group_fanout_by_level")
