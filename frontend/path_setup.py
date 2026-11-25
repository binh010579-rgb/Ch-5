"""Thêm thư mục gốc dự án vào sys.path để import được `algorithms` và `backend`.

Mỗi trang trong frontend/pages chỉ cần: `import path_setup  # noqa: F401`
(Streamlit tự thêm thư mục chứa app.py vào sys.path nên import này luôn chạy được.)
"""
import pathlib
import sys

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
