# Đề tài 5 – Phân tích số lá và cấu trúc phân nhánh của cây quản lý bến bãi

Python · Streamlit · SQLite

## Chạy dự án
```bash
pip install -r requirements.txt
streamlit run frontend/app.py     # chạy giao diện (từ thư mục gốc)
pytest                            # chạy toàn bộ test
```

## Cấu trúc thư mục
```
DeTai5/
├── frontend/                  # GIAO DIỆN (Streamlit)
│   ├── app.py                 # trang chủ
│   ├── path_setup.py          # giúp import algorithms / backend (đừng xóa)
│   └── pages/                 # mỗi người một trang
├── backend/                   # BACKEND
│   ├── database/              # SQLite: connection, repository, schema.sql      (TV1)
│   └── services/              # lớp trung gian: gọi algorithms + database       (mỗi người 1 file)
├── algorithms/                # THUẬT TOÁN thuần Python (không Streamlit, không SQL)
├── data/organization.csv      # dữ liệu mẫu
├── tests/                     # mỗi người một file test
└── docs/                      # ghi chú, báo cáo từng thành viên
```
**Luồng gọi:** `frontend/pages` → `backend/services` → `algorithms` và `backend/database`.
Trang không tự tính toán; thuật toán không biết gì về giao diện hay database.

## Phân công và tiến độ

| TV | Algorithms | Service | Page | Test | Trạng thái |
|---|---|---|---|---|---|
| TV1 | `tree.py`, `validation.py` | `tree_service.py` (+ `database/`) | `1_Data.py` | `test_tree.py` | Xong |
| TV2 | `bfs.py`, `leaf_analysis.py` | `analysis_service.py` | `2_Tree_BFS.py` | `test_bfs.py` | Xong |
| TV3 | `fanout.py`, `statistics.py` | `statistics_service.py` | `3_Statistics.py` | `test_statistics.py` | **Chưa làm (có khung sẵn)** |
| TV4 | `m_ary_tree.py` | `model_service.py` | `4_Model.py` | `test_model.py` | Xong |
| TV5 | `rebalance.py` | `recommendation_service.py` | `5_Recommendation.py` | `test_recommendation.py` | **Chưa làm (có khung sẵn)** |

## Quy ước chung (mọi người phải theo)
* Cây: `tree[node_id] = [id các con]`, lá có `[]`, gốc ở tầng 0.
* Lấy cây hợp lệ **chỉ** qua `backend.services.tree_service.get_valid_tree()` → `(tree, root, info)`,
  với `info[id] = {"name", "type", "parent_id"}`. Dữ liệu sai thì hàm raise `ValueError`.
* Import theo gốc dự án: `from algorithms.bfs import get_depths`, `from backend.services.tree_service import get_valid_tree`.
* Trong mỗi trang `frontend/pages/*.py`, dòng đầu phải có `import path_setup  # noqa: F401`.
* Không viết SQL ngoài `backend/database/`. Không import `streamlit` trong `algorithms/` và `backend/`.
* Mỗi người chỉ sửa file của mình; cần đổi interface của người khác thì báo trước.

## Hướng dẫn cho TV3 (fan-out, thống kê)
File cần làm: `algorithms/fanout.py`, `algorithms/statistics.py`, `backend/services/statistics_service.py`,
`frontend/pages/3_Statistics.py`, `tests/test_statistics.py`. Mỗi hàm còn `raise NotImplementedError` và có `TODO (TV3)`.
1. Cài `get_fanout`, `group_fanout_by_level`, `calculate_stats`, `analyze_fanout` (tự cài công thức, độ lệch chuẩn tổng thể).
2. Hoàn thiện service và trang: bảng theo tầng, bảng xếp hạng, biểu đồ, nhận xét.
3. Trong `tests/test_statistics.py` xóa dòng `@XF` ở từng test khi hàm xong, rồi chạy `pytest tests/test_statistics.py`.
4. **Báo TV5** tên các khóa trong `analyze_fanout` (`fanout`, `by_level`, `overall`, `ranking`), vì TV5 dùng kết quả này.

## Hướng dẫn cho TV5 (phát hiện nhánh lệch, đề xuất)
File cần làm: `algorithms/rebalance.py`, `backend/services/recommendation_service.py`,
`frontend/pages/5_Recommendation.py`, `tests/test_recommendation.py`.
1. Chờ hoặc thống nhất với TV3 về cấu trúc report fan-out (TV5 có thể làm trước với cây mẫu trong test).
2. Cài `detect_imbalanced_branches`, `simulate_reorganization` (trên **bản sao** cây), `validate_reorganization`
   (một gốc, liên thông, không chu trình, đúng một cha, **bảo toàn số bến xe**), `evaluate_before_after`.
3. Ghi rõ ngưỡng k là giả định của nhóm, đây là heuristic, không nói "tối ưu".
4. Bỏ `@XF` trong test khi hàm xong; có ít nhất một kịch bản trước-sau trong trang.

## Việc cả nhóm cần chốt
* Dữ liệu chính thức: `data/organization.csv` (TV4, 61 bến) và nút "dữ liệu mẫu" ở trang 1 (TV1, 65 bến) đang là hai bộ khác nhau.
* `database/bus_management.db` được tạo tự động khi chạy, không commit (đã có trong `.gitignore`).
