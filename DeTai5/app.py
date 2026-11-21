"""Trang chủ tạm để chạy được `streamlit run app.py`.
TV1 là người điều phối tích hợp: khi nhóm có app.py chính thức thì thay file này."""
import streamlit as st

st.set_page_config(page_title="Đề tài 5 – Cây quản lý bến bãi", layout="wide")
st.title("Phân tích số lá và cấu trúc phân nhánh của cây quản lý bến bãi")
st.write("Chọn từng trang ở thanh bên. Trang 4 (TV4): đối chiếu thực tế với cây m-phân đầy đủ.")
