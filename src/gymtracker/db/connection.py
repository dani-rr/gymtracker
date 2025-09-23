"""Database connection utilities."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extensions import cursor as PgCursor

from ..config.settings import Settings, settings


class Database:
    """Lightweight connection manager for the application's database."""

    def __init__(self, cfg: Settings | None = None) -> None:
        self._cfg = cfg or settings
        self._connection: PgConnection | None = None

    def connect(self) -> PgConnection:
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(
                database=self._cfg.database,
                user=self._cfg.user,
                password=self._cfg.password,
                host=self._cfg.host,
                port=self._cfg.port,
            )
            self._connection.autocommit = True
        return self._connection

    def cursor(self) -> PgCursor:
        return self.connect().cursor()

    def close(self) -> None:
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    @contextmanager
    def cursor_context(self) -> Iterator[PgCursor]:
        cur = self.cursor()
        try:
            yield cur
        finally:
            cur.close()


default_db = Database()
