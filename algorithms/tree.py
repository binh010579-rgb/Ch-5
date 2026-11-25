def build_tree(records: list[dict]) -> tuple[dict[str, list[str]], dict[str, dict], str]:
    tree = {}
    nodes_info = {}
    root = None

    for r in records:
        uid = r["id"]
        tree[uid] = []
        nodes_info[uid] = {
            "name": r["name"],
            "type": r["type"],
            "parent_id": r["parent_id"]
        }
        if not r["parent_id"]:
            root = uid

    for r in records:
        uid = r["id"]
        pid = r["parent_id"]
        if pid and pid in tree:
            tree[pid].append(uid)

    return tree, nodes_info, root