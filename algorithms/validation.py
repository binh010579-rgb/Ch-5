from collections import deque

def validate_tree(records: list[dict]) -> tuple[bool, list[str]]:
    errors = []
    if not records:
        return False, ["Dữ liệu trống, chưa có đơn vị nào."]

    seen_ids = set()
    roots = []
    adj = {}

    for r in records:
        uid = r.get("id")
        pid = r.get("parent_id")
        if not uid:
            errors.append("Tồn tại bản ghi bị thiếu mã đơn vị (id).")
            continue
        if uid in seen_ids:
            errors.append(f"Trùng mã đơn vị: '{uid}'.")
        seen_ids.add(uid)
        adj[uid] = []

        if not pid:
            roots.append(uid)

    if len(roots) == 0:
        errors.append("Không tìm thấy trụ sở gốc (cần đúng 1 đơn vị có parent_id để trống).")
    elif len(roots) > 1:
        errors.append(f"Có {len(roots)} gốc ({', '.join(roots)}). Cây chỉ được phép có 1 gốc duy nhất.")

    edges_count = 0
    for r in records:
        uid = r.get("id")
        pid = r.get("parent_id")
        if not uid or not pid:
            continue
        if uid == pid:
            errors.append(f"Đơn vị '{uid}' tự làm cha của chính mình.")
        elif pid not in seen_ids:
            errors.append(f"Đơn vị '{uid}' có parent_id='{pid}' không tồn tại.")
        else:
            adj[pid].append(uid)
            edges_count += 1

    for r in records:
        uid = r.get("id")
        if r.get("type") == "STATION" and len(adj.get(uid, [])) > 0:
            errors.append(f"Bến xe '{uid}' đang quản lý đơn vị con ({adj[uid]}). Bến xe bắt buộc phải là đỉnh lá.")

    if errors:
        return False, errors

    root = roots[0]
    visited = set()
    queue = deque([root])
    visited.add(root)

    while queue:
        curr = queue.popleft()
        for child in adj[curr]:
            if child in visited:
                errors.append(f"Phát hiện chu trình tại đơn vị '{child}'.")
            else:
                visited.add(child)
                queue.append(child)

    if len(visited) != len(seen_ids):
        unreached = seen_ids - visited
        errors.append(f"Cây không liên thông! Các đơn vị bị rời rạc khỏi gốc: {', '.join(unreached)}.")

    if not errors and len(seen_ids) != edges_count + 1:
        errors.append(f"Vi phạm tính chất cây |V| = |E| + 1 (|V|={len(seen_ids)}, |E|={edges_count}).")

    return len(errors) == 0, errors