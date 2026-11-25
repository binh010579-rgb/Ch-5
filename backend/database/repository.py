import pandas as pd
from backend.database.connection import get_connection, init_db

class UnitRepository:
    def __init__(self):
        init_db()

    def load_units(self) -> list[dict]:
        conn = get_connection()
        rows = conn.execute("SELECT id, name, type, parent_id FROM units").fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "type": r["type"],
                "parent_id": r["parent_id"] if r["parent_id"] not in ("", None) else None
            }
            for r in rows
        ]

    def save_units(self, records: list[dict]):
        conn = get_connection()
        conn.execute("DELETE FROM units")
        for r in records:
            pid = r.get("parent_id")
            if pd.isna(pid) or pid == "":
                pid = None
            conn.execute(
                "INSERT INTO units (id, name, type, parent_id) VALUES (?, ?, ?, ?)",
                (str(r["id"]).strip(), str(r["name"]).strip(), str(r["type"]).strip(), str(pid).strip() if pid else None)
            )
        conn.commit()
        conn.close()

    def add_unit(self, data: dict):
        conn = get_connection()
        pid = data.get("parent_id") or None
        conn.execute(
            "INSERT INTO units (id, name, type, parent_id) VALUES (?, ?, ?, ?)",
            (data["id"].strip(), data["name"].strip(), data["type"].strip(), pid.strip() if pid else None)
        )
        conn.commit()
        conn.close()

    def update_unit(self, unit_id: str, data: dict):
        conn = get_connection()
        pid = data.get("parent_id") or None
        conn.execute(
            "UPDATE units SET name = ?, type = ?, parent_id = ? WHERE id = ?",
            (data["name"].strip(), data["type"].strip(), pid.strip() if pid else None, unit_id)
        )
        conn.commit()
        conn.close()

    def delete_unit(self, unit_id: str):
        conn = get_connection()
        conn.execute("DELETE FROM units WHERE id = ?", (unit_id,))
        conn.commit()
        conn.close()

    def export_units(self) -> str:
        records = self.load_units()
        df = pd.DataFrame(records)
        return df.to_csv(index=False)