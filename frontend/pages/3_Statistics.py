"""TV3 - Trang Streamlit: bảng + biểu đồ fan-out trung bình và độ lệch chuẩn theo tầng."""
import path_setup  # noqa: F401
import pandas as pd
import streamlit as st

from backend.services.tree_service import get_valid_tree
from backend.services.statistics_service import (
    fanout_level_rows,
    fanout_ranking_rows,
    run_fanout_analysis,
)

st.set_page_config(page_title="Thống kê fan-out", layout="wide")
st.title("3. Fan-out trung bình và độ lệch chuẩn theo tầng (TV3)")

try:
    tree, root, info = get_valid_tree()
except Exception as e:
    st.error(f"Chưa có cây hợp lệ: {e}")
    st.stop()

try:
    report = run_fanout_analysis(tree, root)
except NotImplementedError as e:
    st.warning(f"TV3 chưa hoàn thành: {e}")
    st.stop()

# TODO (TV3): hiển thị
#   - metric tổng hợp (fan-out TB toàn cây, độ lệch chuẩn)
#   - bảng theo tầng:   st.dataframe(pd.DataFrame(fanout_level_rows(report)))
#   - biểu đồ fan-out TB / std theo tầng (st.bar_chart)
#   - bảng xếp hạng đơn vị: fanout_ranking_rows(report, info)
#   - đoạn nhận xét: tầng/chi nhánh nào cao/thấp so với mức chung (không kết luận "quá tải" chỉ từ fan-out)
