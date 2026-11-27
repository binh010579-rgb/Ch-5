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

overall = report["overall"]

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Số đỉnh trong",
    overall["count"]
)

col2.metric(
    "Fan-out trung bình toàn cây",
    f'{overall["mean"]:.2f}' if overall["mean"] is not None else "N/A"
)

col3.metric(
    "Độ lệch chuẩn toàn cây",
    f'{overall["std"]:.2f}' if overall["std"] is not None else "N/A"
)

col4.metric(
    "Fan-out lớn nhất",
    overall["max"] if overall["max"] is not None else "N/A"
)

st.divider()

st.subheader("📊 Thống kê fan-out theo tầng")

level_rows = fanout_level_rows(report)
df_level = pd.DataFrame(level_rows)

if df_level.empty:
    st.info("Cây hiện không có đỉnh trong để thống kê fan-out.")
else:
    st.dataframe(
        df_level,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📈 Fan-out trung bình và độ lệch chuẩn theo tầng")

    chart_df = df_level.set_index("Tầng")[
        ["Fan-out TB", "Độ lệch chuẩn"]
    ]

    st.bar_chart(chart_df, use_container_width=True)

st.divider()

st.subheader("🏆 Xếp hạng đơn vị theo fan-out")

ranking_rows = fanout_ranking_rows(report, info)
df_ranking = pd.DataFrame(ranking_rows)

if df_ranking.empty:
    st.info("Không có đơn vị nào có đơn vị con.")
else:
    st.dataframe(
        df_ranking,
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("💡 Nhận xét kết quả")

if overall["count"] == 0:
    st.info(
        "Cây không có đỉnh trong. Vì vậy chưa thể tính "
        "fan-out trung bình và độ lệch chuẩn."
    )
else:
    mean_all = overall["mean"]
    std_all = overall["std"]

    st.write(
        f"- Fan-out trung bình toàn cây là **{mean_all:.2f}**."
    )
    st.write(
        f"- Độ lệch chuẩn toàn cây là **{std_all:.2f}**."
    )

    valid_levels = [
        item for item in report["by_level"]
        if item["mean"] is not None
    ]

    if valid_levels:
        highest = max(valid_levels, key=lambda x: x["mean"])
        lowest = min(valid_levels, key=lambda x: x["mean"])

        st.write(
            f'- Tầng có fan-out trung bình cao nhất là '
            f'**tầng {highest["level"]}** '
            f'({highest["mean"]:.2f}).'
        )

        st.write(
            f'- Tầng có fan-out trung bình thấp nhất là '
            f'**tầng {lowest["level"]}** '
            f'({lowest["mean"]:.2f}).'
        )

        st.markdown("**So sánh fan-out trung bình theo tầng với toàn cây:**")

        for item in valid_levels:
            level = item["level"]
            level_mean = item["mean"]
            difference = level_mean - mean_all

            if difference > 0:
                comment = f"cao hơn mức chung {difference:.2f}"
            elif difference < 0:
                comment = f"thấp hơn mức chung {abs(difference):.2f}"
            else:
                comment = "bằng mức chung"

            st.write(
                f"- Tầng {level}: fan-out trung bình "
                f"**{level_mean:.2f}**, {comment}."
            )

    if report["ranking"]:
        top_node, top_fanout, top_level = report["ranking"][0]

        top_name = top_node
        if info and top_node in info:
            top_name = info[top_node].get("name", top_node)

        st.write(
            f'- Đơn vị có fan-out lớn nhất là **{top_name}** '
            f'(mã: `{top_node}`), có **{top_fanout}** đơn vị con '
            f'ở tầng {top_level}.'
        )

    st.caption(
        "Lưu ý: Fan-out lớn phản ánh số lượng đơn vị con trực tiếp, "
        "không đủ căn cứ để kết luận một đơn vị bị quá tải. "
        "Cần kết hợp thêm dữ liệu về nhân sự, khối lượng công việc "
        "và mức độ phức tạp quản lý."
    )

