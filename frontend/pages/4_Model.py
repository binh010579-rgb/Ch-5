"""Trang TV4 – Đối chiếu thực tế với mô hình cây m-phân đầy đủ."""

import os

import path_setup  # noqa: F401
import pandas as pd
import streamlit as st

from path_setup import ROOT_DIR

from backend.services.model_service import compare_models, load_tree_from_csv, summarize_actual

SAMPLE_CSV = os.path.join(str(ROOT_DIR), "data", "organization.csv")


def get_tree():
    """Lấy cây hợp lệ.

    Lấy từ backend.services.tree_service.get_valid_tree() của TV1 -> (tree, root, info).
    Nếu database chưa có dữ liệu hợp lệ thì đọc data/organization.csv để trang vẫn chạy.
    """
    try:
        from backend.services.tree_service import get_valid_tree  # type: ignore

        tree, root, _info = get_valid_tree()
        return tree, root, "tree_service (TV1)"
    except (ImportError, ValueError):
        data = load_tree_from_csv(SAMPLE_CSV)
        return data["tree"], data["root"], "data/organization.csv (chạy độc lập)"


st.set_page_config(page_title="Mô hình m-phân", layout="wide")
st.title("Đối chiếu thực tế – mô hình cây m-phân đầy đủ")
st.caption(
    "Mô hình m-phân đầy đủ chỉ là mốc THAM CHIẾU: mỗi đơn vị quản lý đúng m đơn vị cấp dưới."
)

try:
    tree, root, source = get_tree()
    actual = summarize_actual(tree, root)
except Exception as exc:  # dữ liệu sai/thiếu: báo rõ thay vì làm sập trang
    st.error(f"Không đọc được cây tổ chức: {exc}")
    st.stop()

st.caption(f"Nguồn dữ liệu: {source}")

# --- Số liệu thực tế --------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Số lá L (bến xe)", actual["leaf_count"])
c2.metric("Đỉnh trong I", actual["internal_count"])
c3.metric("Tổng đỉnh V", actual["total_nodes"])
c4.metric("Số tầng h (số cạnh)", actual["height"])
c5.metric("Fan-out lớn nhất", actual["max_fanout"])
if actual["total_nodes"] != actual["internal_count"] + actual["leaf_count"]:
    st.error("Sai lệch: |V| ≠ I + L. Kiểm tra lại dữ liệu đầu vào.")
else:
    st.success(
        f"Kiểm chứng |V| = I + L: {actual['total_nodes']} = "
        f"{actual['internal_count']} + {actual['leaf_count']}"
    )

# --- Chọn m ------------------------------------------------------------------
st.sidebar.header("Chọn giá trị m")
m_values = st.sidebar.multiselect(
    "Các giá trị m để so sánh", options=list(range(2, 11)), default=[2, 3, 4]
)
if not m_values:
    st.info("Hãy chọn ít nhất một giá trị m ở thanh bên.")
    st.stop()

result = compare_models(actual, sorted(m_values))

st.subheader("Bảng so sánh thực tế – lý thuyết")
# Chuyển sang chuỗi để mọi cột cùng kiểu (tránh lỗi Arrow khi cột lẫn số và "—")
display_rows = [
    {k: ("—" if v is None else str(v)) for k, v in row.items()} for row in result["table"]
]
st.dataframe(pd.DataFrame(display_rows), hide_index=True)
st.caption(
    f"Với L = {actual['leaf_count']}, các m ∈ [2, 10] cho I nguyên: "
    f"{', '.join(map(str, result['valid_m'])) or 'không có'}."
)

# --- Cảnh báo / nhận xét theo từng m ------------------------------------------
for rep in result["reports"]:
    if rep["status"] != "ok":
        st.warning(f"m = {rep['m']}: {rep['message']}")
    for note in rep["notes"]:
        st.write(f"• **m = {rep['m']}**: {note}")

# --- Biểu đồ ---------------------------------------------------------------------
chart_rows = [
    {"m": r["m"], "I lý thuyết": r["I_theory"], "I thực tế": r["I_actual"]}
    for r in result["reports"]
    if r["I_theory"] is not None and r["I_actual"] is not None
]
if chart_rows:
    st.subheader("Số đỉnh trong: thực tế và mô hình")
    st.bar_chart(pd.DataFrame(chart_rows).set_index("m"))

# --- Lý thuyết ---------------------------------------------------------------------
with st.expander("Chứng minh L = (m − 1)·I + 1 và cận h ≥ ⌈log_m L⌉"):
    st.text(result["proof"])
with st.expander("Vì sao không ép cây thực tế thành cây m-phân đầy đủ?"):
    st.write(result["reference_note"])
