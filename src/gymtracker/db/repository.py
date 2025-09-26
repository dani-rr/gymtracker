"""Data-access helpers for training information."""
from __future__ import annotations

from collections.abc import Sequence

from pandas import DataFrame

from .connection import Database, default_db


class TrainingRepository:
    """Encapsulates all queries against the TrainingLog table."""

    def __init__(self, db: Database | None = None) -> None:
        self._db = db or default_db

    def get_user_names(self) -> list[str]:
        with self._db.cursor_context() as cursor:
            cursor.execute('''SELECT DISTINCT "Name" FROM "TrainingLog" ORDER BY "Name"''')
            return [name[0] for name in cursor.fetchall()]

    def get_trainings(self, user: str) -> tuple[list[str], list[str]]:
        with self._db.cursor_context() as cursor:
            cursor.execute(
                '''SELECT "Training" FROM "TrainingLog" WHERE "Name" = %s GROUP BY "Training", "TrainingOrder" ORDER BY "TrainingOrder"''',
                (user,),
            )
            trainings = [row[0] for row in cursor.fetchall()]
            trainings_display = trainings.copy()

            cursor.execute(
                '''SELECT DISTINCT "TrainingOrder" FROM "TrainingLog" WHERE "Name" = %s AND "Date" = (SELECT MAX("Date") FROM "TrainingLog" WHERE "Name" = %s)''',
                (user, user),
            )
            last_training_order = cursor.fetchone()[0]

            next_training_order = 1 if last_training_order == 3 else last_training_order + 1

            cursor.execute(
                '''SELECT DISTINCT "Training" FROM "TrainingLog" WHERE "TrainingOrder" = %s AND "Name" = %s''',
                (next_training_order, user),
            )
            next_training = cursor.fetchone()[0]

            for idx, training in enumerate(trainings):
                if training == next_training:
                    trainings_display[idx] = f"▸ {next_training}"

            return trainings, trainings_display

    def get_next_training_order(self, user: str) -> Sequence[tuple[int]]:
        with self._db.cursor_context() as cursor:
            cursor.execute(
                '''SELECT DISTINCT "TrainingOrder" FROM "TrainingLog" WHERE "Name" = %s AND "Date" = (SELECT MAX("Date") FROM "TrainingLog" WHERE "Name" = %s);''',
                (user, user),
            )
            return cursor.fetchall()

    def get_last_training(self, user: str, training: str) -> DataFrame:
        with self._db.cursor_context() as cursor:
            cursor.execute(
                '''SELECT * FROM "TrainingLog" WHERE "Name" = %s AND "Training" = %s AND "Date" = (SELECT MAX("Date") FROM "TrainingLog" WHERE "Name" = %s AND "Training" = %s);''',
                (user, training, user, training),
            )
            records = cursor.fetchall()
            cursor.execute(
                """SELECT column_name FROM information_schema.columns WHERE table_name = 'TrainingLog' ORDER BY ordinal_position"""
            )
            columns = [row[0] for row in cursor.fetchall()]

        training_df = DataFrame(records)
        training_df.columns = columns
        return training_df


def get_repository(db: Database | None = None) -> TrainingRepository:
    return TrainingRepository(db)
