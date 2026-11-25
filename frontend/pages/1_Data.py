import path_setup  # noqa: F401  (thêm thư mục gốc vào sys.path)
import streamlit as st
import pandas as pd
from backend.services.tree_service import TreeService
from backend.database.repository import UnitRepository

st.set_page_config(page_title="Quản lý Dữ liệu Cây Bến Bãi", layout="wide")
st.title("1. Quản lý Dữ liệu & Kiểm tra Cấu trúc Cây (TV1)")

repo = UnitRepository()
service = TreeService()

def generate_sample_data():
    data = [{"id": "TRU_SO", "name": "Trụ sở Tổng công ty", "type": "HEADQUARTERS", "parent_id": ""}]
    branches_t1 = [
        ("CN_BAC", "Chi nhánh Miền Bắc", 2),
        ("CN_TRUNG", "Chi nhánh Miền Trung", 2),
        ("CN_NAM", "Chi nhánh Miền Nam", 3),
        ("CN_TAY", "Chi nhánh Miền Tây", 1),
    ]
    station_counts = [6, 5, 4, 3, 22, 12, 8, 5]
    sub_idx = 0
    bx_counter = 1

    for b1_id, b1_name, num_sub in branches_t1:
        data.append({"id": b1_id, "name": b1_name, "type": "BRANCH", "parent_id": "TRU_SO"})
        for s in range(1, num_sub + 1):
            b2_id = f"{b1_id}_KV{s}"
            data.append({"id": b2_id, "name": f"Khu vực {s} - {b1_name}", "type": "BRANCH", "parent_id": b1_id})
            count = station_counts[sub_idx]
            sub_idx += 1
            for _ in range(count):
                bx_id = f"BX_{bx_counter:02d}"
                data.append({"id": bx_id, "name": f"Bến xe số {bx_counter:02d}", "type": "STATION", "parent_id": b2_id})
                bx_counter += 1
    return data

col1, col2 = st.columns(2)
with col1:
    if st.button("Tạo dữ liệu mẫu chuẩn (4 tầng, 65 bến xe)", type="primary"):
        sample = generate_sample_data()
        ok, errs = service.import_from_records(sample)
        if ok:
            st.success("Đã khởi tạo dữ liệu mẫu thành công!")
            st.rerun()

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
        new_id = c1.text_input("Mã đơn vị (VD: BX_66)")
        new_name = c2.text_input("Tên đơn vị")
        new_type = c3.selectbox("Loại", ["HEADQUARTERS", "BRANCH", "STATION"])
        new_parent = c4.text_input("Mã đơn vị cha (để trống nếu là gốc)")
        if st.form_submit_button("Thêm"):
            try:
                repo.add_unit({"id": new_id, "name": new_name, "type": new_type, "parent_id": new_parent})
                st.rerun()
            except Exception as ex:
                st.error(f"Lỗi thêm dữ liệu: {ex}")