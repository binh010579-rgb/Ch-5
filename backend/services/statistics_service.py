"""TV3 - Service thống kê fan-out (gọi thuật toán, trả kết quả cho giao diện và TV5)."""
from algorithms.bfs import get_depths
from algorithms.statistics import analyze_fanout


def run_fanout_analysis(tree, root):
    """Từ cây hợp lệ -> báo cáo fan-out (xem algorithms.statistics.analyze_fanout)."""
    depths = get_depths(tree, root)
    return analyze_fanout(tree, depths)


def fanout_level_rows(report):
    """Chuyển report["by_level"] thành list dict tiêu đề tiếng Việt để hiển thị bảng.

    TODO (TV3): cài đặt, ví dụ cột: Tầng, Số đỉnh trong, Fan-out TB, Độ lệch chuẩn, Min, Max.
    """
    raise NotImplementedError("TV3 chưa cài đặt fanout_level_rows")


def fanout_ranking_rows(report, tree_info=None):
    """Bảng xếp hạng fan-out theo đơn vị (kèm tên đơn vị nếu có tree_info).

    TODO (TV3): cài đặt.
    """
    raise NotImplementedError("TV3 chưa cài đặt fanout_ranking_rows")
