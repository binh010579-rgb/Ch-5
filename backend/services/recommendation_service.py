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
"""TV5 - Service đề xuất điều chỉnh cấu trúc (gọi TV1-TV4, giữ cây gốc nguyên vẹn).

Luồng: phát hiện nhánh lệch -> (sinh hoặc nhận) phương án -> mô phỏng trên BẢN SAO
-> kiểm tra hợp lệ + bảo toàn bến xe -> chạy lại TV2/TV3 trên cây mới -> so sánh trước/sau.
"""
from algorithms.rebalance import (
    describe_plan,
    detect_imbalanced_branches,
    evaluate_before_after,
    level_bands,
    propose_plan,
    simulate_reorganization,
    validate_reorganization,
)
from backend.services.analysis_service import run_analysis      # TV2
from backend.services.statistics_service import run_fanout_analysis  # TV3


def _names(info):
    return {k: v.get("name", k) for k, v in (info or {}).items()}


def run_recommendation(tree, root, threshold=1.5, plan=None, info=None, allow_merge=False):
    """Chạy toàn bộ luồng và trả về dict các khóa:

      imbalanced   : nhánh bị đánh dấu trên cây gốc
      plan         : phương án (tự sinh nếu plan=None)
      plan_rows    : từng thay đổi (đơn vị, cha cũ -> cha mới, lý do)
      new_tree     : cây sau điều chỉnh (bản sao; cây gốc không đổi)
      validation   : {"ok", "errors", "stations_before", "stations_after"}
      before/after : {"structure", "fanout", "imbalanced_count"} (after = None nếu phương án sai)
      imbalanced_after : nhánh còn nằm NGOÀI ngưỡng trên cây mới, theo mốc (TB, σ) cố định của cây gốc
      imbalanced_recomputed : nhánh bị đánh dấu nếu tính lại TB/σ trên cây mới (mốc dịch chuyển)
      comparison   : kết quả evaluate_before_after (None nếu phương án sai)
      names        : {id: tên} gồm cả đơn vị mới tạo
    `info` (tùy chọn) là info của get_valid_tree() để hiển thị tên đơn vị.
    """
    names = _names(info)

    old_fanout = run_fanout_analysis(tree, root)
    old_structure = run_analysis(tree, root)
    imbalanced = detect_imbalanced_branches(tree, old_fanout, threshold, root=root)

    if plan is None:
        plan = propose_plan(tree, imbalanced, old_fanout, threshold, names=names,
                            allow_merge=allow_merge, root=root)
    for step in plan:
        if step.get("op") == "split" and step.get("new_name"):
            names[step["new_node"]] = step["new_name"]

    before = {"structure": old_structure, "fanout": old_fanout, "imbalanced_count": len(imbalanced)}
    result = {
        "imbalanced": imbalanced,
        "plan": plan,
        "plan_rows": [],
        "new_tree": None,
        "validation": None,
        "before": before,
        "after": None,
        "imbalanced_after": [],
        "imbalanced_recomputed": [],
        "comparison": None,
        "names": names,
    }

    new_tree = simulate_reorganization(tree, plan)       # bản sao, cây gốc giữ nguyên
    result["new_tree"] = new_tree
    result["plan_rows"] = describe_plan(tree, plan)
    result["validation"] = validate_reorganization(tree, new_tree)

    if not result["validation"]["ok"]:
        return result                                    # không phân tích cây sai

    new_fanout = run_fanout_analysis(new_tree, root)
    new_structure = run_analysis(new_tree, root)
    bands = level_bands(tree, old_fanout, root=root)     # mốc cố định của cây gốc
    imbalanced_after = detect_imbalanced_branches(new_tree, new_fanout, threshold, root=root,
                                                  reference_stats=bands)
    recomputed = detect_imbalanced_branches(new_tree, new_fanout, threshold, root=root)
    after = {"structure": new_structure, "fanout": new_fanout,
             "imbalanced_count": len(imbalanced_after),
             "imbalanced_recomputed_count": len(recomputed)}

    result["after"] = after
    result["imbalanced_after"] = imbalanced_after
    result["imbalanced_recomputed"] = recomputed
    result["comparison"] = evaluate_before_after(before, after)
    return result
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
