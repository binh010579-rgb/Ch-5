"""TV2 - Trang Streamlit: sơ đồ cây, thứ tự BFS, thống kê theo tầng.

GIẢ ĐỊNH: TV1 cung cấp services/tree_service.py với hàm
    get_valid_tree() -> (tree, root, info)
trong đó info[node_id] = {"name": ..., "type": ...}.
Nếu TV1 đặt tên khác, chỉ cần sửa dòng import/gọi bên dưới.
"""
import path_setup  # noqa: F401
import pandas as pd
import streamlit as st

from algorithms.bfs import bfs_trace
from backend.services.analysis_service import level_table_rows, run_analysis, sample_trace
from backend.services.tree_service import get_valid_tree  # TV1

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

# --- minh họa BFS từng bước ---
st.subheader("Minh họa BFS từng bước")
demo = st.radio("Cây dùng để minh họa", ["Cây mẫu (A–F)", "Dữ liệu đang chọn"], horizontal=True)

if demo.startswith("Cây mẫu"):
    st.code("A\n├─ B ─ D, E\n└─ C ─ F", language=None)
    _steps, _name = sample_trace(), (lambda n: n)
    _scope_ok = True
else:
    _scope = report["order"]
    _scope_ok = len(_scope) > 1
    if _scope_ok:
        _sub = {n: [c for c in tree.get(n, []) if c in report["depths"]] for n in _scope}
        _steps, _name = bfs_trace(_sub, _scope[0]), label
    else:
        st.info("Phạm vi đang chọn chỉ có một đỉnh nên BFS kết thúc ngay ở bước 1.")

if _scope_ok:
    _k = st.slider("Bước", 1, len(_steps), 1, key="bfs_step")
    _s = _steps[_k - 1]
    m1, m2, m3 = st.columns(3)
    m1.metric("Đỉnh vừa lấy ra", _name(_s["current"]))
    m2.metric("Tầng", _s["depth"])
    m3.metric("Độ dài hàng đợi", len(_s["queue"]))
    st.write("**Thêm vào cuối hàng đợi:** "
             + (", ".join(_name(n) for n in _s["added"]) or "không có (đỉnh này là lá)"))
    st.write("**Hàng đợi sau bước này (đầu hàng bên trái):** "
             + (" → ".join(_name(n) for n in _s["queue"]) or "rỗng"))
    st.write("**Đã thăm:** " + " → ".join(_name(n) for n in _s["visited_order"]))
    st.dataframe(pd.DataFrame([
        {"Bước": x["step"], "Lấy ra": _name(x["current"]), "Tầng": x["depth"],
         "Thêm vào hàng đợi": ", ".join(_name(n) for n in x["added"]) or "–",
         "Hàng đợi sau bước": ", ".join(_name(n) for n in x["queue"]) or "rỗng"}
        for x in _steps[:_k]
    ]), hide_index=True)

# --- thứ tự BFS ---
st.subheader("Thứ tự duyệt BFS")
leaf_set = set(report["leaves"])
bfs_rows = [
    {"Thứ tự": i + 1, "Mã": n, "Tên": label(n), "Tầng": report["depths"][n],
     "Loại": "Lá" if n in leaf_set else "Đỉnh trong"}
    for i, n in enumerate(report["order"])
]
st.dataframe(pd.DataFrame(bfs_rows), hide_index=True)

# --- treemap: diện tích ô = số bến xe, màu = so với trung bình cùng tầng ---
st.subheader("Bản đồ phân bổ bến xe (treemap)")


def treemap_data(tree, order, depths, label):
    """Mỗi ĐỈNH TRONG là một ô; giá trị = số bến xe (lá) bên dưới nó.

    ratio = số bến của ô / trung bình số bến của các đỉnh trong cùng tầng.
    ratio > 1: đông hơn mặt bằng chung tầng; ratio < 1: thưa hơn.
    """
    leaves_under = {}
    for n in reversed(order):                       # con xử lý trước cha
        kids = [c for c in tree.get(n, []) if c in depths]
        leaves_under[n] = 1 if not kids else sum(leaves_under[c] for c in kids)

    internal = [n for n in order if any(c in depths for c in tree.get(n, []))]
    by_level = {}
    for n in internal:
        by_level.setdefault(depths[n], []).append(leaves_under[n])
    level_mean = {lv: sum(v) / len(v) for lv, v in by_level.items()}

    parent_of = {c: p for p in internal for c in tree[p] if c in depths}
    rows = []
    for n in internal:
        v = leaves_under[n]
        rows.append({
            "id": n,
            "label": label(n),
            "parent": parent_of.get(n, ""),
            "value": v,
            "level": depths[n],
            "ratio": v / level_mean[depths[n]],
        })
    return rows, level_mean


tm_rows, tm_mean = treemap_data(tree, report["order"], report["depths"], label)
if not tm_rows:
    st.info("Phạm vi đang chọn không có đơn vị quản lý nào để vẽ treemap.")
else:
    try:
        import plotly.graph_objects as go

        fig = go.Figure(go.Treemap(
            ids=[r["id"] for r in tm_rows],
            labels=[r["label"] for r in tm_rows],
            parents=[r["parent"] for r in tm_rows],
            values=[r["value"] for r in tm_rows],
            branchvalues="total",
            text=[f"{r['value']} bến xe" for r in tm_rows],
            textinfo="label+text",
            customdata=[[r["level"], round(r["ratio"], 2), round(tm_mean[r["level"]], 1)]
                        for r in tm_rows],
            hovertemplate=("<b>%{label}</b><br>%{text}"
                           "<br>Tầng %{customdata[0]}"
                           "<br>%{customdata[1]}× trung bình cùng tầng"
                           " (TB = %{customdata[2]} bến)<extra></extra>"),
            marker=dict(
                colors=[min(r["ratio"], 2.5) for r in tm_rows],
                colorscale=[[0, "#cfe8d5"], [0.4, "#f7f1d0"], [1, "#e8715a"]],
                cmin=0, cmax=2.5,
                colorbar=dict(title="× TB tầng"),
                line=dict(width=2),
            ),
            pathbar=dict(visible=True),
        ))
        fig.update_layout(margin=dict(t=10, l=0, r=0, b=0), height=520)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Diện tích ô tỉ lệ với số bến xe bên dưới. Màu đỏ: đông hơn trung bình cùng tầng, "
            "xanh: thưa hơn. Bấm vào một ô để phóng to chi nhánh đó, bấm thanh đường dẫn phía trên để quay lại."
        )
    except ImportError:
        st.warning("Chưa cài plotly. Chạy: pip install plotly")

with st.expander("Xem sơ đồ cây chi tiết"):
    # --- sơ đồ cây (Graphviz: lá màu xanh, đỉnh trong màu cam) ---
    mode = st.radio(
        "Kiểu hiển thị",
        ["Gọn (gộp bến xe theo chi nhánh)", "Chi tiết (từng bến xe)"],
        horizontal=True,
    )


    def wrap(text, width=18):
        """Xuống dòng cho tên dài để ô không bị bè ngang."""
        words, lines, cur = str(text).split(), [], ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > width:
                lines.append(cur)
                cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            lines.append(cur)
        return "\\n".join(lines)


    def build_compact_dot():
        """Mỗi đỉnh trong là một ô; các lá con trực tiếp gộp thành 1 ô '(N) bến xe'."""
        dot = ["digraph G { rankdir=TB; nodesep=0.35; ranksep=0.7;"
               ' node [shape=box, style="filled,rounded", fontsize=13, margin="0.15,0.08"];']
        for n in report["order"]:
            if n in leaf_set:
                continue
            kids = tree.get(n, [])
            leaf_kids = [c for c in kids if c in leaf_set]
            sub_kids = [c for c in kids if c not in leaf_set]
            dot.append(f'"{n}" [label="{wrap(label(n))}", fillcolor="#ffcc80"];')
            for c in sub_kids:
                dot.append(f'"{n}" -> "{c}";')
            if leaf_kids:
                gid = f"{n}__leaves"
                dot.append(f'"{gid}" [label="{len(leaf_kids)} bến xe", fillcolor="#a5d6a7"];')
                dot.append(f'"{n}" -> "{gid}";')
        dot.append("}")
        return "\n".join(dot)


    def build_full_dot():
        """Từng nút một, xoay ngang (LR) để lá xếp thành cột dọc, không bị bè ngang."""
        dot = ["digraph G { rankdir=LR; nodesep=0.06; ranksep=0.8;"
               ' node [shape=box, style="filled", fontsize=11];']
        for n in report["order"]:
            color = "#a5d6a7" if n in leaf_set else "#ffcc80"
            dot.append(f'"{n}" [label="{wrap(label(n), 24)}", fillcolor="{color}"];')
        for n in report["order"]:
            for ch in tree.get(n, []):
                dot.append(f'"{n}" -> "{ch}";')
        dot.append("}")
        return "\n".join(dot)


    if mode.startswith("Gọn"):
        st.graphviz_chart(build_compact_dot())
    else:
        if report["total_nodes"] > 120:
            st.info("Cây lớn, hãy chọn một chi nhánh ở trên để sơ đồ dễ nhìn hơn.")
        st.graphviz_chart(build_full_dot())
    st.caption("Xanh: lá (bến xe). Cam: đỉnh trong (trụ sở / chi nhánh). "
               "Chế độ Gọn: ô xanh ghi số bến xe trực thuộc chi nhánh đó.")
