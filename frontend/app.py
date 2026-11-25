"""Trang chủ. Chạy từ thư mục gốc:  streamlit run frontend/app.py"""
import path_setup  # noqa: F401
import streamlit as st

st.set_page_config(page_title="Đề tài 5 – Cây quản lý bến bãi", layout="wide")
st.title("Phân tích số lá và cấu trúc phân nhánh của cây quản lý bến bãi")
st.write("Chọn từng trang ở thanh bên trái:")
st.markdown(
    """
| Trang | Thành viên | Nội dung |
|---|---|---|
| 1_Data | TV1 | Nhập dữ liệu, kiểm tra cây hợp lệ |
| 2_Tree_BFS | TV2 | BFS, độ sâu, đếm lá / đỉnh trong theo tầng |
| 3_Statistics | TV3 | Fan-out trung bình, độ lệch chuẩn theo tầng |
| 4_Model | TV4 | So sánh với cây m-phân đầy đủ |
| 5_Recommendation | TV5 | Đề xuất tách/gộp chi nhánh, so sánh trước-sau |
"""
)
st.info("Bắt đầu ở trang 1_Data: bấm tạo dữ liệu mẫu hoặc tải CSV, các trang sau dùng chung dữ liệu này.")
