import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.validation import validate_tree
from algorithms.tree import build_tree

def test_valid_tree():
    records = [
        {"id": "ROOT", "name": "Trụ sở", "type": "HEADQUARTERS", "parent_id": None},
        {"id": "CN1", "name": "Chi nhánh 1", "type": "BRANCH", "parent_id": "ROOT"},
        {"id": "BX1", "name": "Bến xe 1", "type": "STATION", "parent_id": "CN1"},
    ]
    ok, errs = validate_tree(records)
    assert ok is True
    assert errs == []
    tree, _, root = build_tree(records)
    assert root == "ROOT"
    assert tree["CN1"] == ["BX1"]

def test_multiple_roots():
    records = [
        {"id": "R1", "name": "Gốc 1", "type": "HEADQUARTERS", "parent_id": None},
        {"id": "R2", "name": "Gốc 2", "type": "HEADQUARTERS", "parent_id": None},
    ]
    ok, errs = validate_tree(records)
    assert ok is False

def test_cycle_and_disconnected():
    records = [
        {"id": "ROOT", "name": "Gốc", "type": "HEADQUARTERS", "parent_id": None},
        {"id": "A", "name": "A", "type": "BRANCH", "parent_id": "B"},
        {"id": "B", "name": "B", "type": "BRANCH", "parent_id": "A"},
    ]
    ok, errs = validate_tree(records)
    assert ok is False

def test_station_has_children():
    records = [
        {"id": "ROOT", "name": "Gốc", "type": "HEADQUARTERS", "parent_id": None},
        {"id": "BX1", "name": "Bến xe", "type": "STATION", "parent_id": "ROOT"},
        {"id": "BX2", "name": "Bến con", "type": "STATION", "parent_id": "BX1"},
    ]
    ok, errs = validate_tree(records)
    assert ok is False