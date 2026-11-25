"""TV3 - Trung bình, phương sai, độ lệch chuẩn.

TỰ CÀI công thức, không dùng numpy/statistics để lấy kết quả chính.
Độ lệch chuẩn TỔNG THỂ: sigma = sqrt( sum((x_i - mean)^2) / n ).
Ghi rõ trong báo cáo là dùng tổng thể hay mẫu.
"""
from algorithms.fanout import get_fanout, group_fanout_by_level


def calculate_stats(values):
    """Trả về dict: count, mean, variance, std, min, max.

    - Danh sách rỗng: không chia cho 0 (trả count = 0, các giá trị còn lại là None hoặc 0,
      nhóm tự thống nhất và ghi trong docstring).
    - Một giá trị: std = 0.
    TODO (TV3): cài đặt. Độ phức tạp O(n).
    """
    raise NotImplementedError("TV3 chưa cài đặt calculate_stats")


def analyze_fanout(tree, depths):
    """Báo cáo fan-out cho giao diện và cho TV5.

    GỢI Ý các khóa trả về (TV5 sẽ dùng, đổi thì báo TV5):
      fanout        : {node_id: fan-out}                    (toàn bộ đỉnh trong)
      by_level      : [{"level": 0, "count": 1, "mean": ..., "std": ..., "min": ..., "max": ...}, ...]
      overall       : calculate_stats của mọi đỉnh trong
      ranking       : [(node_id, fan-out, level), ...] sắp giảm dần theo fan-out
    TODO (TV3): cài đặt bằng get_fanout + group_fanout_by_level + calculate_stats.
    """
    raise NotImplementedError("TV3 chưa cài đặt analyze_fanout")
