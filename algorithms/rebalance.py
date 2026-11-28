"""TV5 - Phát hiện nhánh fan-out lệch và mô phỏng tách/gộp chi nhánh.

Đây là PHƯƠNG ÁN HEURISTIC theo quy tắc nhóm, KHÔNG gọi là tối ưu toàn cục.
Ngưỡng k (hoặc ngưỡng nghiệp vụ) do nhóm chọn, không phải tiêu chuẩn ngành.
Luôn làm việc trên BẢN SAO (copy.deepcopy), không sửa cây gốc.

Quy ước chung: tree[node_id] = [id các con]; lá có []; gốc ở tầng 0.
Đầu vào từ TV3 là report của backend.services.statistics_service.run_fanout_analysis():
  {"fanout": {id: số con}, "by_level": [{"level", "count", "mean", "std", ...}],
   "overall": {...}, "ranking": [...]}
Nếu report rỗng ({}), các hàm tự tính lại từ cây nên vẫn chạy độc lập (dùng cho test).

Tiêu chí đánh dấu (theo TỪNG TẦNG, vì so sánh các đơn vị cùng cấp mới có nghĩa):
  fan-out > mean + k·σ   -> "high" (quá rộng, ứng viên TÁCH)
  fan-out < mean - k·σ   -> "low"  (quá hẹp, ứng viên GỘP)
σ là độ lệch chuẩn tổng thể (chia n), giống TV3. Tầng có σ = 0 (mọi đơn vị bằng nhau)
hoặc chỉ có 1 đỉnh trong thì không đánh dấu đơn vị nào.

Các hàm chính (theo kế hoạch phân công):
  detect_imbalanced_branches, simulate_reorganization,
  validate_reorganization, evaluate_before_after
Hàm bổ trợ: propose_plan (tự sinh phương án), describe_plan (ghi cha cũ/mới + lý do).
"""
import copy
import math
from collections import deque

from algorithms.bfs import get_depths

_EPS = 1e-9


# --------------------------------------------------------------------------- #
# Tiện ích nội bộ
# --------------------------------------------------------------------------- #
def _infer_root(tree):
    """Gốc = đỉnh không là con của đỉnh nào. Phải có đúng một gốc."""
    child_ids = {c for children in tree.values() for c in children}
    roots = [n for n in tree if n not in child_ids]
    if len(roots) != 1:
        raise ValueError(f"Cây phải có đúng 1 gốc, tìm thấy {len(roots)}")
    return roots[0]


def _parent_map(tree):
    parent = {}
    for p, children in tree.items():
        for c in children:
            parent[c] = p
    return parent


def _level_context(tree, fanout_report, root):
    """Trả về (root, depths, fanout, stats) với stats = {level: (mean, std)}.

    Ưu tiên số liệu của TV3 nếu có; thiếu thì tự tính từ cây.
    """
    if root is None:
        root = _infer_root(tree)
    depths = get_depths(tree, root)
    report = fanout_report or {}

    fanout = report.get("fanout") or {n: len(ch) for n, ch in tree.items() if ch}

    stats = {}
    for item in report.get("by_level") or []:
        stats[item["level"]] = (item["mean"], item["std"])

    if not stats:
        grouped = {}
        for node_id, f in fanout.items():
            if node_id in depths:
                grouped.setdefault(depths[node_id], []).append(f)
        for level, values in grouped.items():
            n = len(values)
            mean = sum(values) / n
            std = (sum((x - mean) ** 2 for x in values) / n) ** 0.5
            stats[level] = (mean, std)
    return root, depths, fanout, stats


# --------------------------------------------------------------------------- #
# 1. Phát hiện nhánh lệch
# --------------------------------------------------------------------------- #
def level_bands(tree, fanout_report=None, root=None):
    """Trả về {tầng: (trung bình, σ)} của fan-out các đỉnh trong, dùng làm MỐC THAM CHIẾU CỐ ĐỊNH.

    Khi đánh giá cây sau điều chỉnh, dùng mốc của cây gốc (reference_stats) để biết
    phương án có thực sự đưa các đơn vị về trong ngưỡng đã chọn hay không; nếu tính lại
    trung bình/σ trên cây mới thì mốc dịch chuyển và luôn xuất hiện nhánh "lệch tương đối".
    """
    return _level_context(tree, fanout_report, root)[3]


def detect_imbalanced_branches(tree, fanout_report, threshold, root=None, reference_stats=None):
    """Trả về danh sách đơn vị có fan-out lệch so với mức chung CỦA TẦNG đó.

    threshold = k. reference_stats (tùy chọn) = level_bands() của cây khác, dùng làm mốc cố định.
    Mỗi phần tử:
      {"id", "level", "fanout", "mean", "std", "z_score", "upper", "lower",
       "direction": "high"|"low", "reason"}
    Sắp theo |z_score| giảm dần. Không có nhánh nào vượt ngưỡng -> [].
    """
    if threshold is None or threshold < 0:
        raise ValueError("Ngưỡng k phải >= 0")

    root, depths, fanout, stats = _level_context(tree, fanout_report, root)
    if reference_stats is not None:
        stats = reference_stats

    flagged = []
    for node_id, f in fanout.items():
        level = depths.get(node_id)
        if level is None or level not in stats:
            continue
        mean, std = stats[level]
        if not std:                      # σ = 0 hoặc None: các đơn vị cùng tầng đều nhau
            continue
        upper = mean + threshold * std
        lower = mean - threshold * std
        z = (f - mean) / std
        if f > upper + _EPS:
            direction = "high"
            reason = (f"Fan-out {f} > TB tầng {level} ({mean:.2f}) + {threshold:g}×σ "
                      f"({std:.2f}) = {upper:.2f}")
        elif f < lower - _EPS:
            direction = "low"
            reason = (f"Fan-out {f} < TB tầng {level} ({mean:.2f}) - {threshold:g}×σ "
                      f"({std:.2f}) = {lower:.2f}")
        else:
            continue
        flagged.append({
            "id": node_id, "level": level, "fanout": f,
            "mean": mean, "std": std, "z_score": z,
            "upper": upper, "lower": lower,
            "direction": direction, "reason": reason,
        })
    flagged.sort(key=lambda b: (-abs(b["z_score"]), str(b["id"])))
    return flagged


# --------------------------------------------------------------------------- #
# 2. Mô phỏng tách / gộp / chuyển (trên BẢN SAO)
# --------------------------------------------------------------------------- #
def _apply_plan(tree, plan):
    """Áp dụng plan lên bản sao; trả về (new_tree, log). Cây gốc không bị sửa."""
    work = copy.deepcopy(tree)
    log = []

    def require(node, label):
        if node is None or node not in work:
            raise ValueError(f"{label} '{node}' không tồn tại trong cây")

    def parent_of(node):
        for p, children in work.items():
            if node in children:
                return p
        return None

    def add_log(step_no, op, unit, old_parent, new_parent, reason):
        log.append({"step": step_no, "op": op, "unit": unit,
                    "old_parent": old_parent, "new_parent": new_parent,
                    "reason": reason})

    for step_no, step in enumerate(plan or [], start=1):
        op = step.get("op")
        reason = step.get("reason", "")

        if op == "move":
            node, new_parent = step.get("node"), step.get("new_parent")
            require(node, "Đơn vị cần chuyển")
            require(new_parent, "Cha mới")
            old = parent_of(node)
            if old is None:
                raise ValueError("Không thể chuyển đơn vị gốc")
            work[old].remove(node)
            work[new_parent].append(node)
            add_log(step_no, "move", node, old, new_parent, reason)

        elif op == "split":
            node, new_node = step.get("node"), step.get("new_node")
            moved = list(step.get("move_children", []))
            require(node, "Đơn vị cần tách")
            if not new_node:
                raise ValueError("Thao tác split thiếu 'new_node'")
            if new_node in work:
                raise ValueError(f"Mã đơn vị mới '{new_node}' đã tồn tại")
            if len(set(moved)) != len(moved):
                raise ValueError("move_children có đơn vị bị lặp")
            for c in moved:
                if c not in work[node]:
                    raise ValueError(f"'{c}' không phải con trực tiếp của '{node}'")
            new_parent = step.get("new_parent") or parent_of(node)
            if new_parent is None:
                raise ValueError("Đơn vị gốc không có cha, cần chỉ định 'new_parent'")
            require(new_parent, "Cha của đơn vị mới")

            work[new_node] = []
            work[new_parent].append(new_node)
            add_log(step_no, "create", new_node, None, new_parent, reason)
            for c in moved:
                work[node].remove(c)
                work[new_node].append(c)
                add_log(step_no, "move", c, node, new_node, reason)

        elif op == "merge":
            node, into = step.get("node"), step.get("into")
            require(node, "Đơn vị cần gộp")
            require(into, "Đơn vị nhận")
            if node == into:
                raise ValueError("Không thể gộp một đơn vị vào chính nó")
            old = parent_of(node)
            if old is None:
                raise ValueError("Không thể gộp đơn vị gốc")
            for c in list(work[node]):
                add_log(step_no, "move", c, node, into, reason)
            work[into].extend(work[node])
            work[old].remove(node)
            del work[node]
            add_log(step_no, "delete", node, old, None, reason)

        else:
            raise ValueError(f"Thao tác không hợp lệ ở bước {step_no}: {op!r}")

    return work, log


def simulate_reorganization(tree, plan):
    """Áp dụng phương án lên BẢN SAO của tree và trả về new_tree.

    plan là danh sách thao tác (mỗi thao tác có thể kèm "reason"):
      {"op": "move",  "node": "BX_10", "new_parent": "CN_X"}
      {"op": "split", "node": "CN_A", "new_node": "CN_A2", "move_children": ["BX_1", "BX_2"],
                      "new_parent": <tùy chọn, mặc định là cha của CN_A>}
      {"op": "merge", "node": "CN_B", "into": "CN_C"}   # con của CN_B chuyển sang CN_C, xóa CN_B

    Hàm chỉ báo ValueError khi tham chiếu sai (mã không tồn tại, mã mới trùng, ...).
    Các lỗi về cấu trúc (chu trình, mất bến, ...) KHÔNG bị chặn ở đây mà do
    validate_reorganization phát hiện, để phương án sai vẫn được mô phỏng và chỉ rõ lỗi.
    """
    new_tree, _ = _apply_plan(tree, plan)
    return new_tree


def describe_plan(tree, plan):
    """Bảng ghi rõ từng thay đổi: đơn vị nào chuyển, cha cũ -> cha mới, lý do.

    Mỗi dòng: {"step", "op": "create"|"move"|"delete", "unit", "old_parent", "new_parent", "reason"}.
    """
    _, log = _apply_plan(tree, plan)
    return log


# --------------------------------------------------------------------------- #
# 3. Kiểm tra phương án
# --------------------------------------------------------------------------- #
def validate_reorganization(old_tree, new_tree):
    """Kiểm tra phương án hợp lệ, trả về {"ok": bool, "errors": [...], ...}.

    Kiểm: đúng một gốc (và là gốc cũ), mỗi đỉnh (trừ gốc) đúng một cha, không tự làm cha,
    liên thông + không chu trình (mọi đỉnh đi tới được từ gốc), |V| = |E| + 1,
    và BẢO TOÀN số bến xe: tập lá mới == tập lá cũ (không mất, không nhân đôi,
    không có bến xe bị biến thành đơn vị quản lý, không có đơn vị quản lý bị rỗng thành lá).
    """
    errors = []
    if not new_tree:
        return {"ok": False, "errors": ["Cây mới rỗng"], "stations_before": 0, "stations_after": 0}

    parents = {}
    for p, children in new_tree.items():
        for c in children:
            if c == p:
                errors.append(f"Đơn vị '{c}' tự làm cha của chính nó")
            if c not in new_tree:
                errors.append(f"Đơn vị '{c}' (con của '{p}') không có trong cây")
            parents.setdefault(c, []).append(p)

    for c, ps in parents.items():
        if len(ps) > 1:
            errors.append(f"Đơn vị '{c}' có {len(ps)} cha: {', '.join(map(str, ps))}")

    roots = [n for n in new_tree if n not in parents]
    if not roots:
        errors.append("Không có gốc (cây bị khép kín thành chu trình)")
    elif len(roots) > 1:
        errors.append(f"Có {len(roots)} gốc: {', '.join(map(str, roots))}")
    else:
        old_roots = [n for n in old_tree if n not in {c for ch in old_tree.values() for c in ch}]
        if len(old_roots) == 1 and old_roots[0] != roots[0]:
            errors.append(f"Gốc bị thay đổi: '{old_roots[0]}' -> '{roots[0]}'")

        visited = {roots[0]}
        queue = deque([roots[0]])
        while queue:
            node = queue.popleft()
            for c in new_tree.get(node, []):
                if c in new_tree and c not in visited:
                    visited.add(c)
                    queue.append(c)
        unreachable = [n for n in new_tree if n not in visited]
        if unreachable:
            errors.append("Không liên thông hoặc có chu trình, các đơn vị không đi tới được từ gốc: "
                          + ", ".join(map(str, unreachable)))

    edges = sum(len(ch) for ch in new_tree.values())
    if len(new_tree) != edges + 1:
        errors.append(f"Vi phạm |V| = |E| + 1 (|V|={len(new_tree)}, |E|={edges})")

    old_leaves = {n for n, ch in old_tree.items() if not ch}
    new_leaves = {n for n, ch in new_tree.items() if not ch}
    lost = sorted(old_leaves - set(new_tree), key=str)
    if lost:
        errors.append("Mất bến xe: " + ", ".join(map(str, lost)))
    demoted = sorted((old_leaves & set(new_tree)) - new_leaves, key=str)
    if demoted:
        errors.append("Bến xe đang quản lý đơn vị con (phải là lá): " + ", ".join(map(str, demoted)))
    emptied = sorted(new_leaves - old_leaves, key=str)
    if emptied:
        errors.append("Đơn vị quản lý không còn đơn vị cấp dưới (thành lá, làm sai số bến xe): "
                      + ", ".join(map(str, emptied)))

    return {"ok": not errors, "errors": errors,
            "stations_before": len(old_leaves), "stations_after": len(new_leaves)}


# --------------------------------------------------------------------------- #
# 4. Tự sinh phương án (heuristic) từ các nhánh bị đánh dấu
# --------------------------------------------------------------------------- #
def _unique_id(base, used):
    candidate, i = base, 2
    while candidate in used:
        candidate = f"{base}_{i}"
        i += 1
    used.add(candidate)
    return candidate


def propose_plan(tree, imbalanced, fanout_report, threshold, names=None,
                 allow_merge=False, root=None):
    """Sinh phương án theo quy tắc cố định (heuristic, không chứng minh tối ưu).

    TÁCH (direction = "high"): đơn vị có fan-out f > mean + k·σ được chia thành
      n = ceil(f / limit) đơn vị CÙNG CẤP (đơn vị mới là anh em của đơn vị cũ, nên không tăng số tầng),
      với limit = max(floor(mean + k·σ), 2); các con chia đều (chênh nhau tối đa 1).
      Ưu tiên chuyển bến xe (lá) trước đơn vị con.
    GỘP (direction = "low", chỉ khi allow_merge=True): gộp vào một đơn vị anh em có fan-out nhỏ nhất
      sao cho sau gộp vẫn không vượt mean + k·σ của tầng đó.
    Dữ liệu không có thông tin địa lý nên việc chọn con nào chuyển chỉ dựa trên số liệu;
    nhóm phải rà soát lại theo khu vực thực tế trước khi kết luận.
    """
    names = names or {}
    root, depths, _, stats = _level_context(tree, fanout_report, root)
    parent = _parent_map(tree)
    used = set(tree)
    touched = set()
    plan = []

    for b in imbalanced:
        if b["direction"] != "high":
            continue
        node, f = b["id"], b["fanout"]
        if parent.get(node) is None:
            continue
        limit = max(int(math.floor(b["upper"] + _EPS)), 2)
        if f <= limit:
            continue
        pieces = math.ceil(f / limit)
        base, extra = divmod(f, pieces)
        sizes = [base + (1 if i < extra else 0) for i in range(pieces)]

        children = tree[node]
        movable = [c for c in children if not tree.get(c)] + [c for c in children if tree.get(c)]
        moved_all = movable[:f - sizes[0]]

        pos = 0
        for part, size in enumerate(sizes[1:], start=2):
            chunk = moved_all[pos:pos + size]
            pos += size
            new_id = _unique_id(f"{node}_T{part}", used)
            label = names.get(node, node)
            plan.append({
                "op": "split",
                "node": node,
                "new_node": new_id,
                "new_name": f"{label} (tách {part})",
                "move_children": chunk,
                "reason": (f"{b['reason']}; tách thành {pieces} đơn vị cùng cấp "
                           f"({' + '.join(map(str, sizes))}) để đưa fan-out về ≤ {limit}"),
            })
        touched.add(node)

    if allow_merge:
        for b in imbalanced:
            if b["direction"] != "low":
                continue
            node = b["id"]
            p = parent.get(node)
            if p is None or node in touched:
                continue
            mean, std = stats[depths[node]]
            upper = mean + threshold * std
            f = b["fanout"]
            candidates = [s for s in tree[p]
                          if s != node and s not in touched and tree.get(s)
                          and len(tree[s]) + f <= upper + _EPS]
            if not candidates:
                continue
            target = min(candidates, key=lambda s: (len(tree[s]), str(s)))
            plan.append({
                "op": "merge",
                "node": node,
                "into": target,
                "reason": (f"{b['reason']}; gộp vào đơn vị cùng cha '{target}' "
                           f"(fan-out sau gộp {len(tree[target]) + f} ≤ {upper:.2f})"),
            })
            touched.update({node, target})
    return plan


# --------------------------------------------------------------------------- #
# 5. Đánh giá trước - sau
# --------------------------------------------------------------------------- #
def _metrics(report):
    structure = report.get("structure") or {}
    fanout = report.get("fanout") or {}
    overall = fanout.get("overall") or {}
    mean, std = overall.get("mean"), overall.get("std")
    return {
        "leaves": structure.get("total_leaves"),
        "internal": structure.get("total_internal"),
        "total": structure.get("total_nodes"),
        "height": structure.get("height"),
        "mean": mean,
        "std": std,
        "cv": (std / mean) if (mean and std is not None) else None,
        "max_fanout": overall.get("max"),
        "imbalanced": report.get("imbalanced_count"),
    }


# (khóa, nhãn, nhóm, chiều tốt hơn)
_METRIC_DEFS = [
    ("leaves", "Số bến xe L (phải không đổi)", "invariant", None),
    ("total", "Tổng số đơn vị |V|", "cost", None),
    ("internal", "Số đỉnh trong I (đơn vị quản lý)", "cost", "lower"),
    ("height", "Số tầng h (tầng sâu nhất)", "cost", "lower"),
    ("mean", "Fan-out trung bình (toàn cây)", "info", None),
    ("std", "Độ lệch chuẩn fan-out (toàn cây)", "balance", "lower"),
    ("cv", "Hệ số biến thiên σ/TB", "balance", "lower"),
    ("max_fanout", "Fan-out lớn nhất", "balance", "lower"),
    ("imbalanced", "Số nhánh ngoài ngưỡng (mốc cây gốc)", "balance", "lower"),
]


def evaluate_before_after(old_report, new_report):
    """Bảng so sánh trước-sau + nhận xét đánh đổi.

    Mỗi report là dict: {"structure": <run_analysis>, "fanout": <run_fanout_analysis>,
                         "imbalanced_count": <số nhánh ngoài ngưỡng, tùy chọn>,
                         "imbalanced_recomputed_count": <đếm lại theo mốc mới, tùy chọn>}.

    Trả về {"table", "tradeoffs", "verdict", "improved_balance", "cost_increase", "conserved"}.
    Không kết luận "tốt hơn" nếu chỉ một nhóm chỉ số cải thiện còn nhóm kia xấu đi.
    """
    old_m, new_m = _metrics(old_report), _metrics(new_report)

    table = []
    trend_of = {}
    for key, label, group, better in _METRIC_DEFS:
        b, a = old_m[key], new_m[key]
        delta = None if (b is None or a is None) else round(a - b, 4)
        if delta is None or better is None:
            trend = "info"
        elif delta < -_EPS:
            trend = "improved"
        elif delta > _EPS:
            trend = "worse"
        else:
            trend = "same"
        trend_of[key] = trend
        table.append({"metric": label, "key": key, "group": group,
                      "before": b, "after": a, "delta": delta, "trend": trend})

    conserved = old_m["leaves"] == new_m["leaves"]
    if not conserved:
        return {"table": table, "tradeoffs": ["Số bến xe thay đổi: phương án làm mất/nhân đôi bến xe."],
                "verdict": "Phương án không hợp lệ: số bến xe không được bảo toàn.",
                "improved_balance": False, "cost_increase": False, "conserved": False}

    balance_keys = [k for k in ("cv", "max_fanout", "imbalanced") if old_m[k] is not None and new_m[k] is not None]
    no_worse = all(trend_of[k] != "worse" for k in balance_keys)
    some_better = any(trend_of[k] == "improved" for k in balance_keys)
    improved_balance = bool(balance_keys) and no_worse and some_better
    balance_worse = any(trend_of[k] == "worse" for k in balance_keys)

    height_up = trend_of["height"] == "worse"
    internal_up = trend_of["internal"] == "worse"
    cost_increase = height_up or internal_up

    tradeoffs = []
    if internal_up:
        tradeoffs.append(f"Số đỉnh trong tăng {int(new_m['internal'] - old_m['internal'])}: "
                         "thêm đơn vị quản lý, kéo theo chi phí vận hành/nhân sự.")
    if trend_of["internal"] == "improved":
        tradeoffs.append(f"Số đỉnh trong giảm {int(old_m['internal'] - new_m['internal'])}: "
                         "bộ máy gọn hơn nhưng fan-out của đơn vị nhận có thể tăng.")
    if height_up:
        tradeoffs.append(f"Số tầng tăng {int(new_m['height'] - old_m['height'])}: "
                         "đường báo cáo dài hơn.")
    if trend_of["max_fanout"] == "improved":
        tradeoffs.append(f"Fan-out lớn nhất giảm {old_m['max_fanout']} -> {new_m['max_fanout']}: "
                         "giảm tải cho đơn vị quản lý nhiều bến nhất.")
    if trend_of["std"] == "worse" or trend_of["cv"] == "worse":
        tradeoffs.append("Độ phân tán fan-out tăng: phương án làm phân bổ kém đều hơn.")
    recomputed = new_report.get("imbalanced_recomputed_count")
    if recomputed is not None and new_m["imbalanced"] is not None and recomputed > new_m["imbalanced"]:
        tradeoffs.append(f"Nếu tính lại trung bình/σ trên cây mới thì còn {recomputed} nhánh vượt ngưỡng "
                         "(mốc của tầng dịch chuyển sau khi tách/gộp); không nên chạy lặp vô hạn vì "
                         "luôn có nhánh lệch tương đối.")
    if not tradeoffs:
        tradeoffs.append("Các chỉ số không thay đổi đáng kể.")

    if improved_balance and not cost_increase:
        verdict = "Cải thiện độ cân bằng mà không tăng số tầng hay số đơn vị quản lý."
    elif improved_balance and cost_increase:
        verdict = ("Có đánh đổi: phân bổ cân bằng hơn nhưng chi phí cơ cấu tăng "
                   "(thêm đơn vị quản lý hoặc thêm tầng). Chưa thể kết luận 'tốt hơn' nếu chưa có tiêu chí chi phí.")
    elif balance_worse:
        verdict = "Phương án làm độ cân bằng xấu đi, không nên áp dụng."
    elif cost_increase:
        verdict = "Phương án không cải thiện cân bằng nhưng tăng chi phí cơ cấu."
    else:
        verdict = "Phương án không tạo thay đổi đáng kể."

    return {"table": table, "tradeoffs": tradeoffs, "verdict": verdict,
            "improved_balance": improved_balance, "cost_increase": cost_increase,
            "conserved": True}
