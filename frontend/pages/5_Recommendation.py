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

OP_LABEL = {"create": "Tạo đơn vị mới", "move": "Chuyển", "delete": "Xóa (sau khi gộp)"}


def name_of(uid, names):
    if uid is None:
        return "—"
    return f"{names.get(uid, uid)} ({uid})"


# --- Tham số -----------------------------------------------------------------
c1, c2 = st.columns([3, 2])
with c1:
    k = st.slider("Ngưỡng k (đánh dấu fan-out > TB tầng + k × σ, hoặc < TB tầng − k × σ)",
                  0.5, 3.0, 1.5, 0.1)
with c2:
    allow_merge = st.checkbox("Cho phép đề xuất GỘP đơn vị fan-out thấp vào đơn vị cùng cha", value=False)
st.caption("k là giả định do nhóm chọn, không phải tiêu chuẩn ngành. Tiêu chí so sánh các đơn vị CÙNG TẦNG. "
           "Phương án là heuristic mô phỏng theo quy tắc nhóm, không phải nghiệm tối ưu toàn cục. "
           "Dữ liệu không có thông tin địa lý nên việc chọn bến nào chuyển chỉ dựa trên số liệu, "
           "cần rà soát lại theo thực tế.")

try:
    result = run_recommendation(tree, root, threshold=k, info=info, allow_merge=allow_merge)
except Exception as e:
    st.error(f"Không chạy được phân tích: {e}")
    st.stop()

names = result["names"]

# --- 1. Nhánh bị đánh dấu ----------------------------------------------------
st.header("1. Nhánh có fan-out lệch (cây hiện tại)")
imb = result["imbalanced"]
if not imb:
    st.success("Không có nhánh nào vượt ngưỡng ở k hiện tại. Thử giảm k để xem các nhánh lệch nhẹ hơn.")
else:
    df_imb = pd.DataFrame([{
        "Mã đơn vị": b["id"],
        "Tên đơn vị": names.get(b["id"], b["id"]),
        "Tầng": b["level"],
        "Fan-out": b["fanout"],
        "TB tầng": round(b["mean"], 2),
        "σ tầng": round(b["std"], 2),
        "z-score": round(b["z_score"], 2),
        "Hướng": "Quá rộng (ứng viên tách)" if b["direction"] == "high" else "Quá hẹp (ứng viên gộp)",
        "Lý do": b["reason"],
    } for b in imb])
    st.dataframe(df_imb, use_container_width=True, hide_index=True)
    st.caption("Fan-out lệch chưa đủ để kết luận đơn vị quá tải: cần thêm dữ liệu về lưu lượng, diện tích, nhân sự.")

# --- 2. Phương án ------------------------------------------------------------
st.header("2. Phương án mô phỏng (trên bản sao, cây gốc giữ nguyên)")
plan_rows = result["plan_rows"]
if not result["plan"]:
    st.info("Chưa có thao tác nào cần thực hiện (không có nhánh quá rộng"
            + ("" if allow_merge else ", hoặc chưa bật gộp") + ").")
else:
    df_plan = pd.DataFrame([{
        "Bước": r["step"],
        "Thao tác": OP_LABEL.get(r["op"], r["op"]),
        "Đơn vị": name_of(r["unit"], names),
        "Cha cũ": name_of(r["old_parent"], names),
        "Cha mới": name_of(r["new_parent"], names),
        "Lý do": r["reason"],
    } for r in plan_rows])
    st.dataframe(df_plan, use_container_width=True, hide_index=True)

# --- 3. Kiểm tra hợp lệ ------------------------------------------------------
st.header("3. Kiểm tra hợp lệ và bảo toàn bến xe")
val = result["validation"]
m1, m2 = st.columns(2)
m1.metric("Số bến xe trước", val["stations_before"])
m2.metric("Số bến xe sau", val["stations_after"])
if val["ok"]:
    st.success("Cây mới hợp lệ: một gốc, liên thông, không chu trình, mỗi đơn vị (trừ gốc) đúng một cha, "
               "bảo toàn toàn bộ bến xe.")
else:
    st.error("Phương án KHÔNG hợp lệ, không phân tích tiếp:")
    for err in val["errors"]:
        st.write(f"- {err}")
    st.stop()

# --- 4. So sánh trước / sau --------------------------------------------------
st.header("4. So sánh trước - sau")
cmp_ = result["comparison"]
TREND = {"improved": "✅ tốt hơn", "worse": "⚠️ xấu hơn", "same": "= không đổi", "info": ""}


def fmt(v):
    if v is None:
        return "—"
    return round(v, 3) if isinstance(v, float) else v


df_cmp = pd.DataFrame([{
    "Chỉ số": r["metric"],
    "Trước": fmt(r["before"]),
    "Sau": fmt(r["after"]),
    "Thay đổi": fmt(r["delta"]),
    "Đánh giá": TREND[r["trend"]],
} for r in cmp_["table"]]).astype(str)
st.dataframe(df_cmp, use_container_width=True, hide_index=True)

if cmp_["improved_balance"] and not cmp_["cost_increase"]:
    st.success(cmp_["verdict"])
elif cmp_["improved_balance"]:
    st.warning(cmp_["verdict"])
else:
    st.info(cmp_["verdict"])
st.subheader("Nhận xét đánh đổi")
for line in cmp_["tradeoffs"]:
    st.write(f"- {line}")

# Biểu đồ fan-out từng đơn vị ở tầng bị đánh dấu
levels = sorted({b["level"] for b in imb}) or sorted({r["level"] for r in result["before"]["fanout"]["by_level"]})
rows = []
for scenario, key, tr in (("Trước", "before", tree), ("Sau", "after", result["new_tree"])):
    depths = result[key]["structure"]["depths"]
    for uid, f in result[key]["fanout"]["fanout"].items():
        if depths.get(uid) in levels:
            rows.append({"Đơn vị": names.get(uid, uid), "Kịch bản": scenario, "Fan-out": f})
if rows:
    df_chart = pd.DataFrame(rows).pivot_table(index="Đơn vị", columns="Kịch bản", values="Fan-out", aggfunc="max").fillna(0)
    st.subheader("Fan-out các đơn vị ở tầng liên quan (trước / sau)")
    st.bar_chart(df_chart)

# --- 5. Thử phương án thủ công -----------------------------------------------
with st.expander("Thử phương án thủ công: chuyển một đơn vị sang cha khác (để kiểm tra bộ kiểm tra hợp lệ)"):
    internal_ids = [u for u, ch in tree.items() if ch]
    movable_ids = [u for u in tree if u != root]
    node = st.selectbox("Đơn vị cần chuyển", movable_ids, format_func=lambda u: name_of(u, names))
    new_parent = st.selectbox("Cha mới", list(tree), format_func=lambda u: name_of(u, names), index=list(tree).index(root))
    if st.button("Mô phỏng thao tác này"):
        manual = run_recommendation(tree, root, threshold=k, info=info,
                                    plan=[{"op": "move", "node": node, "new_parent": new_parent,
                                           "reason": "Thao tác thủ công do người dùng chọn"}])
        v = manual["validation"]
        if v["ok"]:
            st.success("Hợp lệ. " + manual["comparison"]["verdict"])
            st.write(f"Fan-out lớn nhất: {manual['before']['fanout']['overall']['max']} → "
                     f"{manual['after']['fanout']['overall']['max']}; σ toàn cây: "
                     f"{manual['before']['fanout']['overall']['std']:.2f} → "
                     f"{manual['after']['fanout']['overall']['std']:.2f}")
        else:
            st.error("Không hợp lệ:")
            for err in v["errors"]:
                st.write(f"- {err}")
