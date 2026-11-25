"""TV5 - Phát hiện nhánh fan-out lệch và mô phỏng tách/gộp chi nhánh.

Đây là PHƯƠNG ÁN HEURISTIC theo quy tắc nhóm, không gọi là tối ưu toàn cục.
Ghi rõ trong báo cáo: k hoặc ngưỡng do nhóm chọn, không phải tiêu chuẩn ngành.
Luôn làm việc trên BẢN SAO (copy.deepcopy), không sửa cây gốc.

Quy ước: tree[node_id] = [id các con]; lá có []; gốc ở tầng 0.
Đầu vào từ TV3 là report của backend.services.statistics_service.run_fanout_analysis().
"""


def detect_imbalanced_branches(tree, fanout_report, threshold):
    """Trả về danh sách đơn vị có fan-out lệch.

    Ví dụ tiêu chí: fan-out > mean + k * std (k = threshold), tính theo từng tầng hoặc toàn cây.
    Mỗi phần tử gợi ý: {"id", "level", "fanout", "mean", "std", "z_score", "reason"}.
    TODO (TV5): cài đặt.
    """
    raise NotImplementedError("TV5 chưa cài đặt detect_imbalanced_branches")


def simulate_reorganization(tree, plan):
    """Áp dụng phương án lên BẢN SAO của tree và trả về new_tree.

    plan gợi ý: danh sách thao tác, ví dụ
      {"op": "move", "node": "BX_10", "new_parent": "CN_X"}
      {"op": "split", "node": "CN_A", "new_node": "CN_A2", "move_children": ["BX_1", "BX_2"]}
      {"op": "merge", "node": "CN_B", "into": "CN_C"}
    Phải ghi rõ đơn vị nào chuyển, cha cũ/mới và lý do.
    TODO (TV5): cài đặt.
    """
    raise NotImplementedError("TV5 chưa cài đặt simulate_reorganization")


def validate_reorganization(old_tree, new_tree):
    """Kiểm tra phương án hợp lệ, trả về {"ok": bool, "errors": [...]}.

    Cần kiểm: một gốc, liên thông, không chu trình, mỗi đỉnh (trừ gốc) đúng một cha,
    và BẢO TOÀN số bến xe (không mất, không nhân đôi).
    TODO (TV5): cài đặt.
    """
    raise NotImplementedError("TV5 chưa cài đặt validate_reorganization")


def evaluate_before_after(old_report, new_report):
    """Bảng so sánh trước-sau (std fan-out, số tầng, số đỉnh trong, ...) + nhận xét đánh đổi.

    Không tuyên bố "tốt hơn" nếu chỉ một chỉ số cải thiện (std giảm có thể làm tăng số tầng).
    TODO (TV5): cài đặt.
    """
    raise NotImplementedError("TV5 chưa cài đặt evaluate_before_after")
