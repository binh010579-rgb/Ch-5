from algorithms.fanout import (get_fanout, group_fanout_by_level)


def calculate_stats(values):
    values = list(values)
    n = len(values)

    if n == 0:
        return {"count": 0, "mean": None, "variance": None, "std": None, "min": None, "max": None}

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std = variance ** 0.5

    return {"count": n, "mean": mean, "variance": variance, "std": std, "min": min(values), "max": max(values)}


def analyze_fanout(tree, depths):
    fanout = get_fanout(tree)

    grouped = group_fanout_by_level(fanout, depths)

    by_level = []

    for level, values in grouped.items():

        stats = calculate_stats(values)

        by_level.append({"level": level, "count": stats["count"], "mean": stats["mean"], "std": stats["std"], "min": stats["min"], "max": stats["max"]})

    overall = calculate_stats(fanout.values())

    ranking = []

    for node_id, child_count in fanout.items():
        level = depths[node_id]
        ranking.append((node_id, child_count, level))

    ranking.sort(key=lambda item: item[1], reverse=True)

    return {"fanout": fanout, "by_level": by_level, "overall": overall, "ranking": ranking}
