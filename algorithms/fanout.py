def get_fanout(tree):
    fanout = {}

    for node_id, children in tree.items():
        if len(children) > 0:
            fanout[node_id] = len(children)

    return fanout


def group_fanout_by_level(fanout, depths):
    grouped = {}

    for node_id, child_count in fanout.items():

        if node_id not in depths:
            raise ValueError(f"Không tìm thấy tầng của đỉnh: {node_id}")

        level = depths[node_id]

        if level not in grouped:
            grouped[level] = []

        grouped[level].append(child_count)

    return dict(sorted(grouped.items()))
