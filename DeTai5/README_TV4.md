# TV4 – Mô hình cây m-phân đầy đủ và so sánh

## File của TV4
| File | Vai trò |
| --- | --- |
| `algorithms/m_ary_tree.py` | Thuật toán: `calculate_internal_nodes`, `minimum_height`, `compare_actual_model`, `prove_relation` |
| `services/model_service.py` | Service cho giao diện: `compare_models`, `compare_from_tree`, `summarize_actual` |
| `pages/4_Model.py` | Trang Streamlit đối chiếu thực tế – lý thuyết |
| `tests/test_model.py` | 28 test (m=2,3,4; L=1; m<=1; I không nguyên; log/ceil; đếm cạnh hai cách) |

## Chạy
```
pip install -r requirements.txt
python -m unittest tests.test_model -v      # chạy test
streamlit run app.py                         # chạy giao diện, mở trang 4_Model
```

## Quy ước và interface cần thống nhất với nhóm
* Cây: `tree[node_id] = [id các con]`, lá có danh sách rỗng; gốc ở tầng 0; `h` là số cạnh từ gốc đến lá sâu nhất.
* TV2 truyền vào `compare_models(actual_summary, m_values)` một dict có khóa:
  `leaf_count` (bắt buộc), `internal_count`, `height`, `max_fanout` (tùy chọn nhưng nên có).
* `summarize_actual()` trong service chỉ là bản tối thiểu để TV4 chạy độc lập; khi TV2 xong
  `analyze_structure()` thì dùng kết quả của TV2.
* `pages/4_Model.py` gọi thử `services.tree_service.get_valid_tree()` (giả định về TV1, cần sửa cho
  đúng tên hàm nhóm chốt); nếu chưa có thì đọc `data/organization.csv`.
* `data/organization.csv` là dữ liệu mẫu do TV4 tạo để chạy thử (61 bến, 4 tầng, phân bổ không đều);
  dữ liệu chính thức do nhóm/TV1 chốt.
