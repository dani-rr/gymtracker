"""Database connection utilities backed by sqlite3."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

SqliteConnection = sqlite3.Connection
SqliteCursor = sqlite3.Cursor

DEFAULT_DB_FILENAME = "trainings.db"


def _default_db_path() -> Path:
    env_path = os.getenv("GYMTRACKER_DB_PATH")
    if env_path:
        return Path(env_path).expanduser()
    return Path(__file__).resolve().with_name(DEFAULT_DB_FILENAME)


@dataclass(slots=True)
class Settings:
    """Container for sqlite connection parameters."""

    database_path: Path
    timeout: float = 5.0
    detect_types: int = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    check_same_thread: bool = False

    @classmethod
    def load(cls) -> "Settings":
        return cls(database_path=_default_db_path())


settings = Settings.load()


class Database:
    """Lightweight connection manager for the application's database."""

    def __init__(self, cfg: Settings | None = None) -> None:
        self._cfg = cfg or settings
        self._connection: SqliteConnection | None = None

    def connect(self) -> SqliteConnection:
        if self._connection is None:
            self._cfg.database_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(
                self._cfg.database_path,
                timeout=self._cfg.timeout,
                detect_types=self._cfg.detect_types,
                check_same_thread=self._cfg.check_same_thread,
            )
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def cursor(self) -> SqliteCursor:
        return self.connect().cursor()

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def cursor_context(self) -> Iterator[SqliteCursor]:
        cursor = self.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


default_db = Database()
