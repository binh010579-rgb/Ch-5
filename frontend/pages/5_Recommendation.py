"""TV5 - Trang Streamlit: phát hiện nhánh lệch và đề xuất tách/gộp, so sánh trước-sau."""
import path_setup  # noqa: F401
import pandas as pd
import streamlit as st

from backend.services.tree_service import get_valid_tree
from backend.services.recommendation_service import run_recommendation

st.set_page_config(page_title="Đề xuất điều chỉnh", layout="wide")
st.title("5. Đề xuất điều chỉnh cấu trúc chi nhánh (TV5)")

try:
    tree, root, info = get_valid_tree()
except Exception as e:
    st.error(f"Chưa có cây hợp lệ: {e}")
    st.stop()

k = st.slider("Ngưỡng k (đánh dấu nhánh có fan-out > trung bình + k × độ lệch chuẩn)", 0.5, 3.0, 1.5, 0.1)
st.caption("k là giả định do nhóm chọn, không phải tiêu chuẩn ngành. Đây là phương án mô phỏng heuristic.")

try:
    result = run_recommendation(tree, root, threshold=k)
except NotImplementedError as e:
    st.warning(f"TV5 chưa hoàn thành: {e}")
    st.stop()

# TODO (TV5): hiển thị
#   - danh sách nhánh bị đánh dấu và lý do
#   - phương án tách/gộp (đơn vị nào chuyển, cha cũ/mới)
#   - kết quả kiểm tra hợp lệ + bảo toàn số bến xe
#   - bảng so sánh trước/sau + nhận xét đánh đổi
