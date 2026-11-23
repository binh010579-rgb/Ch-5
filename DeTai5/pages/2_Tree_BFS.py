"""TV2 - Trang Streamlit: sơ đồ cây, thứ tự BFS, thống kê theo tầng.

GIẢ ĐỊNH: TV1 cung cấp services/tree_service.py với hàm
    get_valid_tree() -> (tree, root, info)
trong đó info[node_id] = {"name": ..., "type": ...}.
Nếu TV1 đặt tên khác, chỉ cần sửa dòng import/gọi bên dưới.
"""
import pandas as pd
import streamlit as st

from services.analysis_service import run_analysis, level_table_rows
from services.tree_service import get_valid_tree  # TV1

st.title("Cây phân cấp và duyệt BFS")

try:
    tree, root, info = get_valid_tree()
except Exception as e:
    st.error(f"Chưa có cây hợp lệ: {e}")
    st.stop()


def label(n):
    return info.get(n, {}).get("name", n)


# --- chọn toàn cây hoặc một chi nhánh ---
internal_ids = [n for n, ch in tree.items() if ch]
choice = st.selectbox(
    "Phạm vi phân tích",
    options=[root] + [n for n in internal_ids if n != root],
    format_func=lambda n: "Toàn cây" if n == root else f"Cây con: {label(n)}",
)
report = run_analysis(tree, root, subtree_root=choice)

# --- số liệu tổng ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Tổng đỉnh |V|", report["total_nodes"])
c2.metric("Đỉnh trong I", report["total_internal"])
c3.metric("Lá L", report["total_leaves"])
c4.metric("Chiều cao", report["height"])

if report["check_V_equals_I_plus_L"] and report["check_levels_sum"]:
    st.success(f"Kiểm chứng đúng: |V| = I + L = {report['total_internal']} + "
               f"{report['total_leaves']} = {report['total_nodes']}")
else:
    st.error("Kiểm chứng |V| = I + L thất bại, cần kiểm tra lại dữ liệu")

# --- bảng theo tầng ---
st.subheader("Thống kê theo tầng")
level_df = pd.DataFrame(level_table_rows(report))
st.dataframe(level_df, hide_index=True)
st.bar_chart(level_df.set_index("Tầng")[["Đỉnh trong", "Lá"]])

# --- thứ tự BFS ---
st.subheader("Thứ tự duyệt BFS")
leaf_set = set(report["leaves"])
bfs_rows = [
    {"Thứ tự": i + 1, "Mã": n, "Tên": label(n), "Tầng": report["depths"][n],
     "Loại": "Lá" if n in leaf_set else "Đỉnh trong"}
    for i, n in enumerate(report["order"])
]
st.dataframe(pd.DataFrame(bfs_rows), hide_index=True)

# --- sơ đồ cây (Graphviz: lá màu xanh, đỉnh trong màu cam) ---
st.subheader("Sơ đồ cây")
if report["total_nodes"] > 120:
    st.info("Cây lớn, hãy chọn một chi nhánh để sơ đồ dễ nhìn hơn.")
dot = ["digraph G { rankdir=TB; node [shape=box, style=filled, fontsize=10];"]
for n in report["order"]:
    color = "#a5d6a7" if n in leaf_set else "#ffcc80"
    dot.append(f'"{n}" [label="{label(n)}", fillcolor="{color}"];')
for n in report["order"]:
    for ch in tree.get(n, []):
        dot.append(f'"{n}" -> "{ch}";')
dot.append("}")
st.graphviz_chart("\n".join(dot))
st.caption("Xanh: lá (bến xe). Cam: đỉnh trong (trụ sở / chi nhánh).")
