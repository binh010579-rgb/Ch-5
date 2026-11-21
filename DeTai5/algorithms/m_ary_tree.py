"""TV4 – Mô hình cây m-phân đầy đủ và so sánh với cây thực tế (Đề tài 5).

Quy ước chung của nhóm:
  * Gốc ở tầng 0; h là SỐ CẠNH từ gốc đến tầng lá sâu nhất.
  * L = số lá, I = số đỉnh trong, V = I + L, E = V - 1.

Module chỉ nhận số liệu và trả kết quả (không gọi Streamlit, không truy vấn SQLite).
Các công thức là O(1); riêng minimum_height là O(h) vì dùng số nguyên để tránh sai số
dấu phẩy động của log.
"""

from __future__ import annotations

from typing import Any, Dict, List


# --------------------------------------------------------------------------- #
# Kiểm tra đầu vào
# --------------------------------------------------------------------------- #
def _check_int(name: str, value: Any, minimum: int) -> None:
    # bool là lớp con của int trong Python nên loại ra rõ ràng
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} phải là số nguyên, nhận được {value!r}")
    if value < minimum:
        raise ValueError(f"{name} phải >= {minimum}, nhận được {value}")


# --------------------------------------------------------------------------- #
# 1. Số đỉnh trong:  L = (m - 1) * I + 1   =>   I = (L - 1) / (m - 1)
# --------------------------------------------------------------------------- #
def calculate_internal_nodes(L: int, m: int) -> Dict[str, Any]:
    """Tính số đỉnh trong I của cây m-phân đầy đủ có đúng L lá.

    Không tự làm tròn: nếu (L - 1) không chia hết cho (m - 1) thì trả về
    status = "not_integer" kèm thông báo, KHÔNG đưa ra I gần đúng.

    Trả về dict:
      status  : "ok" | "not_integer" | "invalid_m"
      L, m    : đầu vào
      I       : số đỉnh trong (int) nếu status == "ok", ngược lại None
      V       : tổng số đỉnh = I + L = m*I + 1 (nếu ok)
      E       : số cạnh = V - 1 (nếu ok)
      message : giải thích bằng tiếng Việt
    """
    _check_int("L", L, 1)
    if isinstance(m, bool) or not isinstance(m, int):
        raise TypeError(f"m phải là số nguyên, nhận được {m!r}")

    result: Dict[str, Any] = {"L": L, "m": m, "I": None, "V": None, "E": None}

    if m <= 1:
        result["status"] = "invalid_m"
        result["message"] = (
            f"m = {m} không hợp lệ: công thức I = (L - 1)/(m - 1) cần m > 1 "
            "(m = 1 là cây dạng dây chuyền, chỉ có 1 lá)."
        )
        return result

    remainder = (L - 1) % (m - 1)
    if remainder != 0:
        result["status"] = "not_integer"
        result["message"] = (
            f"(L - 1)/(m - 1) = {L - 1}/{m - 1} không phải số nguyên (dư {remainder}). "
            f"Vì vậy không tồn tại cây {m}-phân đầy đủ có đúng {L} lá; "
            "không làm tròn để ép thành số nguyên."
        )
        return result

    internal = (L - 1) // (m - 1)
    result.update(
        status="ok",
        I=internal,
        V=internal + L,
        E=internal + L - 1,
        message=f"I = ({L} - 1)/({m} - 1) = {internal}; V = I + L = {internal + L}.",
    )
    return result


# --------------------------------------------------------------------------- #
# 2. Số tầng tối thiểu:  L <= m^h  =>  h >= ceil(log_m L)
# --------------------------------------------------------------------------- #
def minimum_height(L: int, m: int) -> int:
    """Số tầng (số cạnh từ gốc đến tầng lá) tối thiểu h = ceil(log_m L).

    Dùng số nguyên: h là số nhỏ nhất thỏa m**h >= L. Cách này tránh lỗi làm tròn
    của math.log (ví dụ math.log(1000, 10) = 2.9999999999999996).
    """
    _check_int("L", L, 1)
    _check_int("m", m, 2)
    h = 0
    capacity = 1  # m**h
    while capacity < L:
        capacity *= m
        h += 1
    return h


# --------------------------------------------------------------------------- #
# 3. So sánh cây thực tế với mô hình m-phân đầy đủ
# --------------------------------------------------------------------------- #
def compare_actual_model(actual_summary: Dict[str, Any], m: int) -> Dict[str, Any]:
    """So sánh số liệu thực tế với cây m-phân đầy đủ có cùng số lá.

    actual_summary cần có:
      leaf_count      (bắt buộc)  L thực tế
      internal_count  (tùy chọn)  I thực tế
      height          (tùy chọn)  số tầng thực tế = số cạnh gốc -> lá sâu nhất
      max_fanout      (tùy chọn)  fan-out lớn nhất trong cây thực tế
    """
    if "leaf_count" not in actual_summary:
        raise KeyError("actual_summary thiếu khóa 'leaf_count'")
    L = actual_summary["leaf_count"]
    _check_int("leaf_count", L, 1)

    theory = calculate_internal_nodes(L, m)
    report: Dict[str, Any] = {
        "m": m,
        "L": L,
        "status": theory["status"],
        "message": theory["message"],
        "I_theory": theory["I"],
        "V_theory": theory["V"],
        "I_actual": actual_summary.get("internal_count"),
        "I_diff": None,
        "h_min": None,
        "h_actual": actual_summary.get("height"),
        "h_diff": None,
        "max_fanout": actual_summary.get("max_fanout"),
        "is_m_ary": None,
        "notes": [],
    }

    if m > 1:
        report["h_min"] = minimum_height(L, m)

    # Chênh lệch số đỉnh trong (chỉ khi cả hai đều có)
    if theory["I"] is not None and report["I_actual"] is not None:
        report["I_diff"] = report["I_actual"] - theory["I"]
        if report["I_diff"] < 0:
            report["notes"].append(
                "Cây thực tế có ÍT đỉnh trong hơn mô hình: trung bình mỗi đỉnh trong "
                f"quản lý NHIỀU hơn {m} con."
            )
        elif report["I_diff"] > 0:
            report["notes"].append(
                "Cây thực tế có NHIỀU đỉnh trong hơn mô hình: nhiều đơn vị trung gian "
                f"quản lý ít hơn {m} con."
            )
        else:
            report["notes"].append(
                f"Số đỉnh trong thực tế bằng mô hình {m}-phân đầy đủ."
            )

    # Chênh lệch số tầng
    if report["h_min"] is not None and report["h_actual"] is not None:
        report["h_diff"] = report["h_actual"] - report["h_min"]

    # Điều kiện áp dụng của cận dưới tầng
    if report["max_fanout"] is not None:
        report["is_m_ary"] = report["max_fanout"] <= m
        if not report["is_m_ary"]:
            report["notes"].append(
                f"Fan-out lớn nhất thực tế là {report['max_fanout']} > m = {m}: cây thực "
                f"tế KHÔNG phải cây {m}-phân, nên cận dưới L <= m^h không bắt buộc đúng "
                "cho cây này. Số tầng thực tế có thể nhỏ hơn h_min mà không mâu thuẫn."
            )
    if report["h_diff"] is not None and report["h_diff"] > 0:
        report["notes"].append(
            f"Cây thực tế sâu hơn cận dưới lý thuyết {report['h_diff']} tầng: "
            "cận dưới chỉ là giá trị nhỏ nhất có thể, không phải số tầng bắt buộc."
        )

    return report


# --------------------------------------------------------------------------- #
# 4. Gợi ý chọn m
# --------------------------------------------------------------------------- #
def valid_m_values(L: int, m_max: int = 10) -> List[int]:
    """Các m trong [2, m_max] cho I nguyên, tức (m - 1) chia hết (L - 1)."""
    _check_int("L", L, 1)
    _check_int("m_max", m_max, 2)
    return [m for m in range(2, m_max + 1) if (L - 1) % (m - 1) == 0]


def suggest_m_values(actual_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Gợi ý các giá trị m để so sánh, kèm lý do (để ghi vào báo cáo)."""
    suggestions: List[Dict[str, Any]] = [
        {"m": 2, "reason": "Cây nhị phân: mốc cơ bản nhất để đối chiếu."},
        {"m": 3, "reason": "Phân cấp 3 nhánh: mức quản lý vừa phải."},
        {"m": 4, "reason": "Phân cấp 4 nhánh: nhịp độ quản lý rộng hơn."},
    ]
    internal = actual_summary.get("internal_count")
    leaves = actual_summary.get("leaf_count")
    if internal and leaves:
        avg = (internal + leaves - 1) / internal  # fan-out trung bình = E / I
        near = max(2, round(avg))
        if near not in {s["m"] for s in suggestions}:
            suggestions.append(
                {
                    "m": near,
                    "reason": f"Gần fan-out trung bình thực tế ({avg:.2f}): "
                    "mô hình sát thực tế nhất.",
                }
            )
    return suggestions


# --------------------------------------------------------------------------- #
# 5. Chứng minh L = (m - 1) * I + 1 (đếm cạnh theo hai cách) và cận tầng
# --------------------------------------------------------------------------- #
def prove_relation() -> str:
    """Trả về chứng minh dạng văn bản (dùng cho báo cáo và giao diện)."""
    return (
        "CHỨNG MINH L = (m − 1)·I + 1 BẰNG ĐẾM SỐ CẠNH THEO HAI CÁCH\n"
        "\n"
        "Giả thiết: T là cây m-phân đầy đủ (mỗi đỉnh trong có ĐÚNG m con), có I đỉnh "
        "trong, L lá, V = I + L đỉnh, E cạnh.\n"
        "\n"
        "Cách 1 – đếm theo tính chất của cây: mỗi đỉnh khác gốc có đúng một cạnh nối "
        "lên cha của nó, gốc thì không. Nên E = V − 1 = (I + L) − 1.\n"
        "\n"
        "Cách 2 – đếm theo số con: mỗi cạnh nối một đỉnh với một con của nó, nên E bằng "
        "tổng số con của mọi đỉnh. Mỗi đỉnh trong có đúng m con, mỗi lá có 0 con, do đó "
        "E = m·I.\n"
        "\n"
        "Hai cách đếm bằng nhau: m·I = I + L − 1, suy ra L = m·I − I + 1 = (m − 1)·I + 1.\n"
        "Do đó I = (L − 1)/(m − 1) (với m > 1) và V = I + L = m·I + 1. ∎\n"
        "\n"
        "Hệ quả: I phải nguyên nên (m − 1) phải chia hết (L − 1). Nếu không chia hết thì "
        "không tồn tại cây m-phân đầy đủ có đúng L lá.\n"
        "\n"
        "CHỨNG MINH CẬN DƯỚI L ≤ m^h\n"
        "Quy ước h là số cạnh từ gốc đến tầng lá sâu nhất; cây m-phân là cây mà mỗi đỉnh "
        "có tối đa m con. Quy nạp theo h:\n"
        "  • h = 0: cây chỉ có gốc, gốc là lá nên L = 1 = m^0.\n"
        "  • Giả sử đúng với chiều cao h − 1. Với cây chiều cao h ≥ 1, gốc có k con "
        "(1 ≤ k ≤ m); mỗi cây con có chiều cao ≤ h − 1 nên có tối đa m^(h−1) lá. "
        "Số lá của cây không vượt quá k·m^(h−1) ≤ m·m^(h−1) = m^h.\n"
        "Lấy logarit cơ số m: h ≥ log_m L; vì h nguyên nên h ≥ ⌈log_m L⌉. ∎\n"
        "\n"
        "Lưu ý: đây là cận DƯỚI lý thuyết cho cây m-phân (mỗi đỉnh tối đa m con); nó "
        "không phải số tầng bắt buộc của tổ chức thực tế."
    )


def explain_reference_model() -> str:
    """Ý nghĩa của mô hình m-phân đầy đủ: tham chiếu, không phải khuôn bắt buộc."""
    return (
        "Cây m-phân đầy đủ là MÔ HÌNH THAM CHIẾU: mỗi đơn vị quản lý đúng m đơn vị cấp "
        "dưới. Nó cho biết số đơn vị trung gian và số tầng 'lý tưởng' nếu mọi chi nhánh "
        "có cùng mức phân bổ. Tổ chức thực tế không nhất thiết phải ép theo mô hình này "
        "vì số bến ở mỗi khu vực khác nhau (diện tích, dân cư, lưu lượng), nên fan-out "
        "không đồng đều có thể hợp lý. Mô hình dùng để đánh giá mức lệch so với chuẩn và "
        "làm căn cứ cho đề xuất điều chỉnh (TV5), chứ không dùng để bắt buộc tổ chức."
    )
