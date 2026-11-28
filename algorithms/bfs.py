"""TV2 - BFS và tính độ sâu (tầng).

Quy ước chung của nhóm:
- tree là dict: tree[node_id] = [danh sách id các con]. Lá thì có giá trị [].
- Gốc ở tầng 0, con trực tiếp của gốc ở tầng 1.
- Không gọi Streamlit / SQLite trong file này.

Vì sao gốc ở tầng 0?
    Tầng (độ sâu) của một đỉnh v là số CẠNH trên đường đi duy nhất từ gốc đến v,
    kí hiệu depth(v). Đường đi từ gốc đến chính nó có 0 cạnh nên depth(gốc) = 0.
    Cách đặt này cho ba điều nhất quán:
      * depth(con) = depth(cha) + 1 (công thức truy hồi dùng trong BFS bên dưới);
      * chiều cao h của cây = tầng lớn nhất = số cạnh của đường đi dài nhất từ gốc,
        khớp với định nghĩa chiều cao ở Chương 7 và với công thức h >= ceil(log_m L)
        mà TV4 dùng (cây chỉ có gốc thì h = 0);
      * một cây có n tầng (0..h) có h + 1 "hàng" đỉnh, không bị lệch 1 khi đếm.
    Nếu đánh số gốc ở tầng 1 thì "tầng" = số đỉnh trên đường đi chứ không còn là
    số cạnh, và mọi công thức theo h phải trừ/cộng 1 cho khớp.

Độ phức tạp: O(V + E) thời gian, O(V) bộ nhớ (chứng minh ở cuối file).
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


def bfs_trace(tree, root):
    """Ghi lại từng bước BFS để minh họa trên giao diện / trong báo cáo.

    Trả về list dict, mỗi phần tử là trạng thái SAU một lần lấy đỉnh khỏi hàng đợi:
        {"step": số bước (từ 1),
         "current": đỉnh vừa lấy ra khỏi hàng đợi,
         "depth": tầng của đỉnh đó,
         "added": [các con được thêm vào cuối hàng đợi ở bước này],
         "queue": [nội dung hàng đợi sau bước này, đầu hàng ở bên trái],
         "visited_order": [các đỉnh đã thăm đến hết bước này]}
    Bước 0 (trạng thái ban đầu) không nằm trong list: hàng đợi = [gốc], tầng gốc = 0.
    Hàm này cùng thuật toán với bfs_with_depths nên cho cùng thứ tự thăm.
    """
    if root is None or root not in tree:
        raise ValueError("Gốc không tồn tại trong cây")

    depths = {root: 0}
    visited = {root}
    queue = deque([root])
    order, steps = [], []

    while queue:
        node = queue.popleft()
        order.append(node)
        added = []
        for child in tree.get(node, []):
            if child in visited:
                continue
            visited.add(child)
            depths[child] = depths[node] + 1
            queue.append(child)
            added.append(child)
        steps.append({
            "step": len(order),
            "current": node,
            "depth": depths[node],
            "added": added,
            "queue": list(queue),
            "visited_order": list(order),
        })
    return steps


def bfs_operation_count(tree, root):
    """Đếm số thao tác cơ bản của BFS: (số lần popleft, số cạnh được xét).

    Dùng để kiểm chứng bằng thực nghiệm rằng tổng thao tác = V + E (xem chứng minh).
    """
    order, _ = bfs_with_depths(tree, root)
    pops = len(order)
    edges_examined = sum(len(tree.get(n, [])) for n in order)
    return pops, edges_examined


# ---------------------------------------------------------------------------
# CHỨNG MINH ĐỘ PHỨC TẠP O(V + E)
# ---------------------------------------------------------------------------
# Kí hiệu V = số đỉnh đi tới được từ gốc, E = số cạnh giữa các đỉnh đó.
# Với cây có gốc: E = V - 1 (mỗi đỉnh trừ gốc có đúng 1 cạnh nối tới cha).
#
# 1) Mỗi đỉnh vào hàng đợi đúng 1 lần.
#    Một đỉnh chỉ được append khi chưa thuộc `visited`, và ngay lúc append thì được
#    thêm vào `visited` (không bao giờ bị xóa). Gốc được đưa vào từ đầu.
#    => tổng số lần append <= V, và vì vòng lặp chỉ dừng khi hàng đợi rỗng nên
#       mọi đỉnh đi tới được đều được lấy ra: số lần popleft = V.
#
# 2) Mỗi đỉnh được lấy ra khỏi hàng đợi đúng 1 lần, nên vòng `for child in ...`
#    của nó chạy đúng 1 lần. Tổng số lần lặp của vòng for trong cả thuật toán là
#        sum over v of deg_out(v) = E
#    (mỗi cạnh cha->con được xét đúng 1 lần, từ phía cha).
#
# 3) Chi phí từng thao tác:
#      popleft / append của collections.deque : O(1)   (list.pop(0) là O(n), nên
#                                                        không dùng list)
#      kiểm tra `in visited`, `visited.add`   : O(1) trung bình (hash set)
#      ghi depths[child]                      : O(1)
#
# 4) Cộng lại:  T(V, E) = V * O(1)   (V lần popleft + ghi order)
#                       + E * O(1)   (E lần xét cạnh)
#                       + O(1)       (khởi tạo)
#                       = O(V + E).
#    Với cây E = V - 1 nên T = O(V).
#
# 5) Bộ nhớ: visited, depths, order mỗi cái <= V phần tử; hàng đợi chứa tối đa
#    một tầng (không quá V) => O(V).
#
# Vì sao hiệu quả hơn "tính độ sâu bằng cách đi ngược lên gốc cho từng đỉnh"?
#    Cách đó tốn O(V * h), tệ nhất O(V^2) với cây dạng chuỗi. BFS tính depth(con) =
#    depth(cha) + 1 ngay khi duyệt nên chỉ tốn O(V + E).
