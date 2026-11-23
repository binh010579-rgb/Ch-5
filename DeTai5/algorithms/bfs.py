"""TV2 - BFS và tính độ sâu (tầng).

Quy ước chung của nhóm:
- tree là dict: tree[node_id] = [danh sách id các con]. Lá thì có giá trị [].
- Gốc ở tầng 0, con trực tiếp của gốc ở tầng 1.
- Không gọi Streamlit / SQLite trong file này.
"""
from collections import deque


def bfs_with_depths(tree, root):
    """Duyệt BFS 1 lần, trả về (thứ tự thăm, {node: depth}).

    Depth của con = depth của cha + 1, tính ngay khi duyệt.
    Dùng tập visited để mỗi đỉnh chỉ thăm đúng 1 lần.
    """
    if root is None or root not in tree:
        raise ValueError("Gốc không tồn tại trong cây")

    order = []                 # thứ tự thăm
    depths = {root: 0}         # gốc ở tầng 0
    visited = {root}
    queue = deque([root])      # deque: lấy đầu hàng đợi O(1)

    while queue:
        node = queue.popleft()
        order.append(node)
        for child in tree.get(node, []):
            if child in visited:       # phòng dữ liệu sai (chu trình)
                continue
            visited.add(child)
            depths[child] = depths[node] + 1
            queue.append(child)
    return order, depths


def bfs(tree, root):
    """Trả về thứ tự thăm các đỉnh theo BFS."""
    order, _ = bfs_with_depths(tree, root)
    return order


def get_depths(tree, root):
    """Trả về {node_id: depth}, gốc = 0."""
    _, depths = bfs_with_depths(tree, root)
    return depths
