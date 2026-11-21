# TV4 – Kết quả so sánh và nhận xét (dữ liệu mẫu)

Dữ liệu mẫu `data/organization.csv`: 75 đơn vị, **L = 61 bến xe**, **I = 14 đỉnh trong**, |V| = 14 + 61 = 75,
số tầng thực tế **h = 3**, fan-out trung bình = 74/14 ≈ 5,29, fan-out lớn nhất = 15 (không đều).
*Thay bằng số liệu của bộ dữ liệu chính thức khi nhóm chốt dữ liệu.*

| m | I lý thuyết = (L−1)/(m−1) | I thực tế | Chênh lệch I | h tối thiểu = ⌈log_m L⌉ | h thực tế | Chênh lệch h |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 60 | 14 | −46 | 6 | 3 | −3 |
| 3 | 30 | 14 | −16 | 4 | 3 | −1 |
| 4 | 20 | 14 | −6 | 3 | 3 | 0 |
| 5 | 15 | 14 | −1 | 3 | 3 | 0 |
| 7 | 10 | 14 | +4 | 3 | 3 | 0 |

## Nhận xét
1. Với m = 2, 3, 4, cây thực tế có ít đỉnh trong hơn mô hình: trung bình mỗi đơn vị quản lý khoảng 5,29 đơn vị cấp dưới, nhiều hơn m. Mô hình sát thực tế nhất là m = 5 (I lý thuyết 15, thực tế 14).
2. Với m = 2 và 3, số tầng thực tế (3) **nhỏ hơn** cận h tối thiểu (6 và 4). Điều này không mâu thuẫn: cận L ≤ m^h chỉ áp dụng cho cây mà mỗi đỉnh có **tối đa m con**, còn cây thực tế có đơn vị quản lý tới 15 con nên không phải cây nhị phân hay tam phân.
3. Cận dưới h là số tầng nhỏ nhất có thể, không phải số tầng bắt buộc của tổ chức.
4. Fan-out lớn nhất (15) gấp gần ba lần trung bình (5,29): phân bổ không đều. Đây là số liệu đầu vào để TV5 xét tách/gộp chi nhánh, nhưng riêng mô hình m-phân chưa đủ để kết luận chi nhánh nào quá tải.

## Gợi ý trả lời vấn đáp (câu 3: có nên ép cây thực tế thành cây m-phân đầy đủ?)
Không nên mặc định ép. Mô hình m-phân đầy đủ là mốc tham chiếu để đo mức lệch. Số bến mỗi khu vực khác nhau theo dân cư, diện tích, lưu lượng; ép đồng đều có thể buộc tạo thêm đơn vị trung gian (tăng số tầng, tăng chi phí quản lý) hoặc gộp những khu vực không nên gộp. Ngoài ra không phải L nào cũng có cây m-phân đầy đủ: cần (m − 1) chia hết (L − 1), ví dụ L = 60, m = 4 cho I = 59/3, không nguyên.

## Chứng minh
Xem `prove_relation()` trong `algorithms/m_ary_tree.py` (hoặc mục chứng minh trên trang 4_Model): đếm cạnh theo hai cách, E = V − 1 = I + L − 1 và E = m·I, suy ra L = (m − 1)·I + 1; cận L ≤ m^h chứng minh bằng quy nạp theo h.
