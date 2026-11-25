"""TV5 - Service đề xuất điều chỉnh cấu trúc (gọi TV1-TV4, giữ cây gốc nguyên vẹn)."""
from algorithms.rebalance import (
    detect_imbalanced_branches,
    evaluate_before_after,
    simulate_reorganization,
    validate_reorganization,
)
from backend.services.analysis_service import run_analysis      # TV2
from backend.services.statistics_service import run_fanout_analysis  # TV3


def run_recommendation(tree, root, threshold=1.5, plan=None):
    """Chạy toàn bộ luồng: phát hiện nhánh lệch -> mô phỏng -> kiểm tra -> so sánh trước/sau.

    Trả về dict gợi ý các khóa:
      imbalanced, plan, new_tree, validation, before, after, comparison
    TODO (TV5): cài đặt; nếu plan=None thì tự sinh phương án từ imbalanced.
    """
    old_fanout = run_fanout_analysis(tree, root)
    old_structure = run_analysis(tree, root)
    imbalanced = detect_imbalanced_branches(tree, old_fanout, threshold)
    # TODO (TV5): sinh plan, simulate_reorganization, validate_reorganization,
    #             chạy lại run_fanout_analysis / run_analysis trên new_tree, evaluate_before_after
    raise NotImplementedError("TV5 chưa hoàn thành run_recommendation")
