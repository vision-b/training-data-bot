from typing import Union
import sqlite3
from pathlib import Path

class DatabaseManager:
    """Small SQLite store for dataset snapshots (assistant-designed)."""

    def __init__(self, database_path: Union[str, Path] = "data/training_data_bot.db"):
        self.database_path = str(database_path)
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS datasets (id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        self.connection.commit()

    def save_dataset(self, dataset):
        self.connection.execute(
            "INSERT OR REPLACE INTO datasets (id, payload) VALUES (?, ?)",
            (str(dataset.id), dataset.model_dump_json()),
        )
        self.connection.commit()

    def load_dataset_json(self, dataset_id: str):
        row = self.connection.execute(
            "SELECT payload FROM datasets WHERE id = ?", (dataset_id,)
        ).fetchone()
        return row[0] if row else None

    async def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
