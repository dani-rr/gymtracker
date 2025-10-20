"""Data-access helpers for training information."""
from __future__ import annotations

from collections.abc import Sequence

from pandas import DataFrame

from .connection import Database, default_db

DEFAULT_TRAINING_SEQUENCE = ("Push", "Pull", "Legs")
DEFAULT_SEQUENCE_INDEX = {name: idx for idx, name in enumerate(DEFAULT_TRAINING_SEQUENCE)}


def _training_sort_key(name: str) -> tuple[int, str]:
    sequence_position = DEFAULT_SEQUENCE_INDEX.get(name, len(DEFAULT_SEQUENCE_INDEX))
    return sequence_position, name.lower()


def _sort_trainings(names: list[str]) -> tuple[list[str], dict[str, int]]:
    sorted_names = sorted(names, key=_training_sort_key)
    order_map = {name: idx + 1 for idx, name in enumerate(sorted_names)}
    return sorted_names, order_map


class TrainingRepository:
    """Encapsulates all queries against the training table."""

    def __init__(self, db: Database | None = None) -> None:
        self._db = db or default_db

    def get_user_names(self) -> list[str]:
        with self._db.cursor_context() as cursor:
            cursor.execute("SELECT DISTINCT user FROM training ORDER BY user")
            return [name[0] for name in cursor.fetchall()]

    def get_trainings(self, user: str) -> tuple[list[str], list[str]]:
        with self._db.cursor_context() as cursor:
            cursor.execute("SELECT DISTINCT training FROM training WHERE user = ?", (user,))
            raw_trainings = [row[0] for row in cursor.fetchall()]
            trainings, _ = _sort_trainings(raw_trainings)
            trainings_display = trainings.copy()

            if trainings:
                cursor.execute(
                    """
                    SELECT training, MAX(date) AS last_date
                    FROM training
                    WHERE user = ?
                    GROUP BY training
                    """,
                    (user,),
                )
                last_seen = {training: last_date for training, last_date in cursor.fetchall()}
                next_training = min(
                    trainings,
                    key=lambda name: (last_seen.get(name) or "", _training_sort_key(name)),
                )
                highlight_index = trainings.index(next_training)
                trainings_display[highlight_index] = f"▸ {next_training}"

            return trainings, trainings_display

    def get_next_training_order(self, user: str) -> Sequence[tuple[int]]:
        with self._db.cursor_context() as cursor:
            cursor.execute("SELECT DISTINCT training FROM training WHERE user = ?", (user,))
            raw_trainings = [row[0] for row in cursor.fetchall()]
            trainings, order_map = _sort_trainings(raw_trainings)
            if not trainings:
                return []

            cursor.execute(
                """
                SELECT DISTINCT training
                FROM training
                WHERE user = ?
                  AND date = (
                      SELECT MAX(date)
                      FROM training
                      WHERE user = ?
                  )
                """,
                (user, user),
            )
            last_trainings = [row[0] for row in cursor.fetchall()]
            return [(order_map.get(training, 0),) for training in last_trainings if training in order_map]

    def get_last_training(self, user: str, training: str) -> DataFrame:
        with self._db.cursor_context() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM training
                WHERE user = ?
                  AND training = ?
                  AND date = (
                      SELECT MAX(date)
                      FROM training
                      WHERE user = ?
                        AND training = ?
                  )
                """,
                (user, training, user, training),
            )
            records = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []

        return DataFrame(records, columns=columns)


def get_repository(db: Database | None = None) -> TrainingRepository:
    return TrainingRepository(db)
