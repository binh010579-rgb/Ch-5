from backend.database.repository import UnitRepository
from algorithms.validation import validate_tree
from algorithms.tree import build_tree

class TreeService:
    def __init__(self):
        self.repo = UnitRepository()

    def get_valid_tree(self):
        records = self.repo.load_units()
        is_valid, errors = validate_tree(records)
        if not is_valid:
            return False, errors, None, None, None
        tree, nodes_info, root = build_tree(records)
        return True, [], tree, nodes_info, root

    def import_from_records(self, records: list[dict]):
        is_valid, errors = validate_tree(records)
        if not is_valid:
            return False, errors
        self.repo.save_units(records)
        return True, []

def get_valid_tree():
    """Interface chung cho mọi trang/service khác.

    Trả về (tree, root, info):
      tree[node_id] = [id các con]; info[node_id] = {"name", "type", "parent_id"}.
    Raise ValueError nếu dữ liệu chưa tạo thành cây hợp lệ.
    """
    ok, errors, tree, info, root = TreeService().get_valid_tree()
    if not ok:
        raise ValueError("; ".join(errors))
    return tree, root, info
