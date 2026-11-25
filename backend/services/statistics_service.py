from algorithms.bfs import get_depths
from algorithms.statistics import analyze_fanout

def run_fanout_analysis(tree, root):
    depths = get_depths(tree, root)
    return analyze_fanout(tree, depths)

def fanout_level_rows(report):
    rows = []

    for item in report["by_level"]:
        rows.append({"Tầng": item["level"], "Số đỉnh trong": item["count"], "Fan-out TB": item["mean"], "Độ lệch chuẩn": item["std"], "Min": item["min"], "Max": item["max"]})

    return rows

def fanout_ranking_rows(report, tree_info=None):
    rows = []

    for rank, (node_id, fanout, level) in enumerate(report["ranking"], start=1):
        name = node_id

        if tree_info and node_id in tree_info:
            name = tree_info[node_id].get("name", node_id)

        rows.append({"Xếp hạng": rank, "Mã đơn vị": node_id, "Tên đơn vị": name, "Tầng": level, "Fan-out": fanout})

    return rows
