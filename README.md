# Đề tài 5 – Phân tích số lá và cấu trúc phân nhánh của cây quản lý phân cấp bến bãi

Bài tập lớn môn **Cấu trúc rời rạc** (Chương 7: tính chất số đỉnh, số lá của cây).
Công nghệ: **Python · Streamlit · SQLite · pytest · GitHub**.

## 1. Mục tiêu

Mô hình hóa hệ thống quản lý bến xe thành **cây có gốc** T: gốc là trụ sở chính, đỉnh trong là chi nhánh/đơn vị quản lý, lá là bến xe. Chương trình:

1. Dựng và kiểm tra cây từ dữ liệu tổ chức (TV1).
2. Duyệt BFS, tính tầng, đếm lá và đỉnh trong theo tầng, kiểm chứng |V| = I + L (TV2).
3. Tính fan-out trung bình và độ lệch chuẩn theo tầng (TV3).
4. So sánh với cây m-phân đầy đủ: I = (L−1)/(m−1), h ≥ ⌈log_m L⌉ (TV4).
5. Phát hiện nhánh fan-out lệch, mô phỏng tách/gộp, đánh giá trước–sau (TV5).

## 2. Cài đặt và chạy

```bash
pip install -r requirements.txt
streamlit run frontend/app.py     # chạy giao diện (từ thư mục gốc dự án)
pytest                            # chạy toàn bộ test
pytest tests/test_recommendation.py   # chạy test riêng một người
```

Lần đầu mở giao diện, vào trang **1. Data** để nạp dữ liệu (bấm nút nạp dữ liệu mẫu chính thức, hoặc tải file CSV của bạn lên). Các trang còn lại lấy cây từ database nên cần nạp dữ liệu trước.
File `backend/database/bus_management.db` được tạo tự động khi chạy, **không commit** (đã có trong `.gitignore`).

## 3. Cấu trúc thư mục

```
DeTai5/
├── frontend/                  # GIAO DIỆN (Streamlit)
│   ├── app.py                 # trang chủ
│   ├── path_setup.py          # giúp import algorithms / backend (đừng xóa)
│   └── pages/
│       ├── 1_Data.py              # TV1: quản lý đơn vị, nhập/xuất dữ liệu
│       ├── 2_Tree_BFS.py          # TV2: sơ đồ cây, thứ tự BFS, thống kê theo tầng
│       ├── 3_Statistics.py        # TV3: fan-out TB, độ lệch chuẩn, biểu đồ
│       ├── 4_Model.py             # TV4: đối chiếu với cây m-phân đầy đủ
│       └── 5_Recommendation.py    # TV5: nhánh lệch, tách/gộp, so sánh trước–sau
├── backend/
│   ├── database/              # SQLite: connection, repository, schema.sql        (TV1)
│   └── services/              # lớp trung gian: gọi algorithms + database
│       ├── tree_service.py        # TV1: get_valid_tree()
│       ├── analysis_service.py    # TV2
│       ├── statistics_service.py  # TV3
│       ├── model_service.py       # TV4
│       └── recommendation_service.py  # TV5
├── algorithms/                # THUẬT TOÁN thuần Python (không Streamlit, không SQL)
│   ├── tree.py, validation.py     # TV1: dựng cây, kiểm tra hợp lệ
│   ├── bfs.py, leaf_analysis.py   # TV2: BFS, tầng, lá/đỉnh trong
│   ├── fanout.py, statistics.py   # TV3: fan-out, trung bình, độ lệch chuẩn
│   ├── m_ary_tree.py              # TV4: cây m-phân đầy đủ
│   └── rebalance.py               # TV5: phát hiện lệch, tách/gộp, đánh giá
├── data/organization.csv      # dữ liệu mẫu (75 đơn vị, 61 bến xe)
├── tests/                     # mỗi người một file test
├── docs/                      # ghi chú, báo cáo từng thành viên
├── requirements.txt
├── pytest.ini
└── README.md
```

**Luồng gọi:** `frontend/pages` → `backend/services` → `algorithms` và `backend/database`.
Trang không tự tính toán; thuật toán không biết gì về giao diện hay database.

## 4. Phân công và tiến độ

| TV | Phần thuật toán | Algorithms | Service | Page | Test | Trạng thái |
|---|---|---|---|---|---|---|
| TV1 | Dựng cây, kiểm tra hợp lệ, database | `tree.py`, `validation.py` | `tree_service.py` (+ `database/`) | `1_Data.py` | `test_tree.py` | Xong |
| TV2 | BFS, độ sâu, đếm lá/đỉnh trong theo tầng | `bfs.py`, `leaf_analysis.py` | `analysis_service.py` | `2_Tree_BFS.py` | `test_bfs.py` | Xong |
| TV3 | Fan-out, trung bình, độ lệch chuẩn | `fanout.py`, `statistics.py` | `statistics_service.py` | `3_Statistics.py` | `test_statistics.py` | Xong |
| TV4 | Cây m-phân đầy đủ, công thức, so sánh | `m_ary_tree.py` | `model_service.py` | `4_Model.py` | `test_model.py` | Xong |
| TV5 | Nhánh lệch, tách/gộp, trước–sau | `rebalance.py` | `recommendation_service.py` | `5_Recommendation.py` | `test_recommendation.py` | Xong |

## 5. Quy ước chung (mọi người phải theo)

* **Kiểu cây:** `tree[node_id] = [id các con]`, lá có `[]`, **gốc ở tầng 0**, con trực tiếp của gốc ở tầng 1.
* **Dữ liệu tổ chức:** bảng/CSV có 4 cột `id, name, type, parent_id` (`type` là `HEADQUARTERS` / `BRANCH` / `STATION`, gốc để trống `parent_id`).
* Lấy cây hợp lệ **chỉ** qua `backend.services.tree_service.get_valid_tree()` → `(tree, root, info)` với `info[id] = {"name", "type", "parent_id"}`. Dữ liệu sai thì hàm raise `ValueError`.
* Import theo gốc dự án: `from algorithms.bfs import get_depths`.
* Mỗi trang `frontend/pages/*.py` có dòng đầu `import path_setup  # noqa: F401`.
* Không viết SQL ngoài `backend/database/`. Không import `streamlit` trong `algorithms/` và `backend/`.
* Không hard-code kết quả; mọi số liệu phải tính từ dữ liệu hiện tại.
* Mỗi người chỉ sửa file của mình; cần đổi interface của người khác thì báo trước.
* **Git:** mỗi người một nhánh `feature/tv1-tree`, `feature/tv2-bfs`, `feature/tv3-stats`, `feature/tv4-model`, `feature/tv5-rebalance`; mở Pull Request (có mô tả, kết quả chạy, test) và có người review trước khi merge.

## 6. Mô tả từng phần

### TV1 – Dựng cây, kiểm tra dữ liệu, database
* `build_tree(records)`, `validate_tree(records)` kiểm tra: mã trùng, thiếu mã, `parent_id` không tồn tại, nhiều gốc/không có gốc, tự làm cha, bến xe có con, chu trình, đỉnh không nối tới gốc, |V| = |E| + 1.
* `UnitRepository` (SQLite) đọc/ghi/xuất đơn vị; chỉ cây hợp lệ mới được trả cho các module khác.
* Giải thích: kiểm tra |V| = |E| + 1 **chưa đủ**, phải kiểm tra thêm liên thông và không chu trình.

### TV2 – BFS, tầng, đếm lá và đỉnh trong
* `bfs_with_depths`, `bfs`, `get_depths`: BFS bằng `collections.deque`, depth con = depth cha + 1.
* `classify_nodes`, `count_by_level`, `analyze_structure`: đếm lá/đỉnh trong/tổng theo tầng, kiểm chứng |V| = I + L.
* Độ phức tạp: O(V + E) = O(V) với cây; dùng `deque` để lấy đầu hàng đợi O(1).

### TV3 – Fan-out và độ lệch chuẩn
* `get_fanout`, `group_fanout_by_level`, `calculate_stats`, `analyze_fanout`.
* Dùng độ lệch chuẩn **tổng thể** σ = √(Σ(xᵢ − x̄)²/n). Báo cáo trả về các khóa `fanout`, `by_level`, `overall`, `ranking`.
* Không kết luận chi nhánh "quá tải" chỉ từ fan-out.

### TV4 – Cây m-phân đầy đủ
* Công thức L = (m−1)·I + 1, suy ra I = (L−1)/(m−1) (phải nguyên, không tự làm tròn); cận tầng h ≥ ⌈log_m L⌉.
* Chứng minh bằng cách đếm cạnh hai cách: E = V − 1 = I + L − 1 và E = m·I.
* Mô hình m-phân chỉ là mốc **tham chiếu**, không ép tổ chức thực tế phải theo. Xem `docs/TV4_ket_qua_va_nhan_xet.md`.

### TV5 – Nhánh lệch, tách/gộp, trước–sau
* **Tiêu chí (do nhóm chọn, không phải chuẩn ngành):** so sánh các đỉnh trong cùng tầng; đánh dấu *quá rộng* nếu fan-out > μ + k·σ, *quá hẹp* nếu < μ − k·σ. Mặc định k = 1,5.
* **Phương án (heuristic, không chứng minh tối ưu):** *tách* đơn vị quá rộng thành n = ⌈f / limit⌉ đơn vị cùng cấp (không tăng số tầng); *gộp* (tùy chọn, mặc định tắt) đơn vị quá hẹp vào đơn vị cùng cha.
* Mô phỏng trên **bản sao** cây; `validate_reorganization` kiểm tra một gốc, mỗi đỉnh đúng một cha, liên thông, không chu trình, |V| = |E| + 1 và **bảo toàn bến xe** (tập lá mới = tập lá cũ).
* `evaluate_before_after` so sánh σ, hệ số biến thiên, fan-out lớn nhất, số đỉnh trong, số tầng; không kết luận "tốt hơn" nếu chỉ một nhóm chỉ số cải thiện. Mốc đánh giá "sau" dùng (μ, σ) cố định của cây gốc.
* Kết quả mẫu (k = 1,5): tách TP.HCM 15 bến → 8 + 7; fan-out lớn nhất 15 → 12, σ 3,86 → 2,83, số tầng giữ 3, số đỉnh trong 14 → 15. Xem `docs/TV5_ket_qua_va_nhan_xet.md`.

## 7. Dữ liệu và kịch bản thực nghiệm

Bộ dữ liệu chính cần 3–4 tầng, ít nhất 60 bến xe (lá) và phân bổ không đều giữa các chi nhánh.

| Kịch bản | Cách tạo | Mục đích |
|---|---|---|
| A – Phân bổ tương đối đều | Các chi nhánh có số bến gần nhau | Mốc tham chiếu |
| B – Phân bổ không đều | Vài chi nhánh quản lý nhiều bến hơn hẳn | Kiểm tra khả năng phát hiện lệch (`data/organization.csv`) |
| C – Sau đề xuất | Tạo từ B bằng tách/gộp/chuyển có giải thích | Đánh giá trước–sau (trang 5) |

**Nguồn dữ liệu chính thức: `data/organization.csv`** – 75 đơn vị, L = 61 bến xe, I = 14 đỉnh trong, h = 3. Nút "Nạp dữ liệu mẫu chính thức" ở trang 1 đọc thẳng file này nên mọi số liệu trong báo cáo cùng một nguồn.

## 8. Kiểm thử

| File test | Nội dung chính |
|---|---|
| `test_tree.py` | Cây chỉ có gốc, nhiều tầng, mã trùng, thiếu cha, hai gốc, tự làm cha, chu trình, nhánh rời |
| `test_bfs.py` | Thứ tự BFS, mỗi đỉnh thăm một lần, đếm theo tầng, |V| = I + L |
| `test_statistics.py` | Fan-out, tính tay trung bình/σ, tầng không có đỉnh trong, dữ liệu rỗng |
| `test_model.py` | m = 2, 3, 4; L = 1; m ≤ 1; I không nguyên; log và làm tròn lên |
| `test_recommendation.py` | Nhánh lệch, tách/gộp, lỗi tham chiếu, chu trình, mất bến, cha trùng, đánh giá trước–sau, dữ liệu thật |

## 9. Câu hỏi vấn đáp cả nhóm cần nắm

* Chứng minh |V| = |E| + 1 từ định nghĩa cây (liên thông, không chu trình).
* Chứng minh L = (m−1)·I + 1 của cây m-phân đầy đủ bằng đếm cạnh hai cách.
* Cây thực tế không đều có nên ép thành cây m-phân đầy đủ không? (Không mặc định: dùng làm cơ sở tham chiếu để đo mức lệch; ép đều có thể thêm tầng/đơn vị trung gian hoặc gộp những khu vực không nên gộp.)
* Vì sao BFS dùng `deque`, độ phức tạp O(V + E) là gì, bộ nhớ phụ tối đa là bao nhiêu?
* Vì sao so sánh fan-out theo từng tầng và vì sao k là giả định, không phải chuẩn?

## 10. Tiến độ gợi ý

1. Chốt nền: dữ liệu mẫu, kiểu cây, quy ước tầng, tên hàm.
2. Mỗi người code thuật toán + test riêng.
3. Viết service, review chéo.
4. Tích hợp trang Streamlit tương ứng.
5. Chạy kịch bản A/B/C, lưu bảng và biểu đồ.
6. Viết báo cáo (lý thuyết, thuật toán, độ phức tạp, test, kết quả, hạn chế), làm slide, tập thuyết trình chéo.

## 11. Lỗi thường gặp

* `ModuleNotFoundError: algorithms` → thiếu dòng `import path_setup  # noqa: F401` đầu trang, hoặc chạy lệnh sai thư mục (phải chạy từ thư mục gốc).
* Trang báo "Chưa có cây hợp lệ" → chưa nạp dữ liệu ở trang 1 hoặc dữ liệu vi phạm điều kiện cây; đọc danh sách lỗi hiển thị.
* Phương án TV5 báo "KHÔNG hợp lệ" → xem danh sách lỗi (mất bến, hai cha, chu trình, đơn vị bị rỗng); đây là hành vi đúng của bộ kiểm tra.
