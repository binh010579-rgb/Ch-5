import os

import path_setup  # noqa: F401  (thêm thư mục gốc vào sys.path)
import streamlit as st
import pandas as pd
from path_setup import ROOT_DIR
from backend.services.tree_service import TreeService
from backend.database.repository import UnitRepository

st.set_page_config(page_title="Quản lý Dữ liệu Cây Bến Bãi", layout="wide")
st.title("1. Quản lý Dữ liệu & Kiểm tra Cấu trúc Cây (TV1)")

repo = UnitRepository()
service = TreeService()

SAMPLE_CSV = os.path.join(str(ROOT_DIR), "data", "organization.csv")


def load_sample_data():
    """Đọc dữ liệu mẫu chính thức của nhóm: data/organization.csv (61 bến xe)."""
    return pd.read_csv(SAMPLE_CSV, dtype=str).fillna("").to_dict(orient="records")


col1, col2 = st.columns(2)
with col1:
    if st.button("Nạp dữ liệu mẫu chính thức (data/organization.csv, 61 bến xe)", type="primary"):
        try:
            sample = load_sample_data()
        except OSError as ex:
            st.error(f"Không đọc được {SAMPLE_CSV}: {ex}")
        else:
            ok, errs = service.import_from_records(sample)
            if ok:
                st.success("Đã nạp dữ liệu mẫu thành công!")
                st.rerun()
            else:
                for e in errs:
                    st.error(e)

with col2:
    uploaded = st.file_uploader("Hoặc tải lên file CSV (id, name, type, parent_id)", type=["csv"])
    if uploaded:
        df_up = pd.read_csv(uploaded).fillna("")
        records = df_up.to_dict(orient="records")
        ok, errs = service.import_from_records(records)
        if ok:
            st.success("Nạp file CSV hợp lệ!")
            st.rerun()
        else:
            for e in errs:
                st.error(e)

st.divider()
is_valid, errors, tree, nodes_info, root = service.get_valid_tree()
if is_valid:
    V = len(tree)
    E = sum(len(children) for children in tree.values())
    leaves = sum(1 for uid, children in tree.items() if len(children) == 0)
    st.success(f"CÂY HỢP LỆ! Gốc: `{root}` | Tổng đỉnh |V| = {V} | Tổng cạnh |E| = {E} (Thỏa |V| = |E| + 1) | Số bến xe (lá) = {leaves}")
else:
    st.warning("Dữ liệu hiện tại chưa tạo thành cây hợp lệ:")
    for e in errors:
        st.error(e)

st.subheader("Danh sách đơn vị trong hệ thống")
current_data = repo.load_units()
if current_data:
    st.dataframe(pd.DataFrame(current_data), use_container_width=True)
    st.download_button("Xuất dữ liệu ra CSV", data=repo.export_units(), file_name="organization.csv", mime="text/csv")

with st.expander("Thêm đơn vị mới"):
    with st.form("add_form"):
        c1, c2, c3, c4 = st.columns(4)
        new_id = c1.text_input("Mã đơn vị (VD: BX_MN_HCM_16)")
        new_name = c2.text_input("Tên đơn vị")
        new_type = c3.selectbox("Loại", ["HEADQUARTERS", "BRANCH", "STATION"])
        new_parent = c4.text_input("Mã đơn vị cha (để trống nếu là gốc)")
        if st.form_submit_button("Thêm"):
            try:
                repo.add_unit({"id": new_id, "name": new_name, "type": new_type, "parent_id": new_parent})
                st.rerun()
            except Exception as ex:
                st.error(f"Lỗi thêm dữ liệu: {ex}")
