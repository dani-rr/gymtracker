"""Create a throwaway Postgres database populated with sample TrainingLog data."""
from __future__ import annotations

import argparse
import os
from datetime import date, timedelta

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


DEFAULT_DB_NAME = "gymtracker"
DEFAULT_ADMIN_DB = os.environ.get("PGDATABASE", "postgres")

TRAINING_ROWS = [
    # (name, training, order, date offset, exercise number, exercise, set, weight, goal reps, reps)
    ("User 1", "Legs", 1, 3, 1, "Back Squat", 1, 40, 10, 10),
    ("User 1", "Legs", 1, 3, 1, "Back Squat", 2, 40, 10, 9),
    ("User 1", "Legs", 1, 3, 2, "Romanian Deadlift", 1, 32, 12, 12),
    ("User 1", "Legs", 1, 3, 2, "Romanian Deadlift", 2, 32, 12, 11),
    ("User 1", "Push", 2, 1, 1, "Bench Press", 1, 34, 8, 8),
    ("User 1", "Push", 2, 1, 1, "Bench Press", 2, 34, 8, 7),
    ("User 1", "Pull", 3, 0, 1, "Barbell Row", 1, 30, 10, 10),
    ("User 1", "Pull", 3, 0, 1, "Barbell Row", 2, 30, 10, 9),
    ("User 2", "Full Body", 1, 2, 1, "Kettlebell Swing", 1, 20, 15, 15),
    ("User 2", "Full Body", 1, 2, 2, "Push Press", 1, 23, 12, 11),
    ("User 2", "Conditioning", 2, 0, 1, "Bike Sprint", 1, 0, 30, 30),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admin-host", default=os.environ.get("PGHOST", "192.168.1.212"))
    parser.add_argument("--admin-port", type=int, default=int(os.environ.get("PGPORT", 5432)))
    parser.add_argument("--admin-user", default=os.environ.get("PGUSER", "gymtracker"))
    parser.add_argument("--admin-password", default=os.environ.get("PGPASSWORD", "gymtracker"))
    parser.add_argument("--admin-db", default=DEFAULT_ADMIN_DB)
    parser.add_argument("--target-db", default=DEFAULT_DB_NAME)
    parser.add_argument("--drop-first", action="store_true", help="Drop the target database before recreating it.")
    return parser.parse_args()


def admin_connect(args: argparse.Namespace) -> psycopg2.extensions.connection:
    conn = psycopg2.connect(
        host=args.admin_host,
        port=args.admin_port,
        user=args.admin_user,
        password=args.admin_password,
        dbname=args.admin_db,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def ensure_database(args: argparse.Namespace) -> None:
    conn = admin_connect(args)
    cur = conn.cursor()
    identifier = sql.Identifier(args.target_db)
    if args.drop_first:
        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {};").format(identifier))
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (args.target_db,))
    exists = cur.fetchone() is not None
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {};").format(identifier))
    cur.close()
    conn.close()


def seed_database(args: argparse.Namespace) -> None:
    conn = psycopg2.connect(
        host=args.admin_host,
        port=args.admin_port,
        user=args.admin_user,
        password=args.admin_password,
        dbname=args.target_db,
    )
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS "TrainingLog" (
            "Id" SERIAL PRIMARY KEY,
            "Name" TEXT NOT NULL,
            "Training" TEXT NOT NULL,
            "TrainingOrder" INTEGER NOT NULL,
            "Date" DATE NOT NULL,
            "ExerciseNumber" INTEGER NOT NULL,
            "Exercise" TEXT NOT NULL,
            "Set" INTEGER NOT NULL,
            "Weight" INTEGER NOT NULL,
            "GoalReps" INTEGER NOT NULL,
            "Reps" INTEGER NOT NULL
        );
    ''')

    cur.execute('DELETE FROM "TrainingLog";')

    today = date.today()
    rows = [
        (
            name,
            training,
            training_order,
            today - timedelta(days=date_offset),
            exercise_number,
            exercise,
            set_number,
            weight,
            goal_reps,
            reps,
        )
        for (
            name,
            training,
            training_order,
            date_offset,
            exercise_number,
            exercise,
            set_number,
            weight,
            goal_reps,
            reps,
        ) in TRAINING_ROWS
    ]

    cur.executemany(
        '''
        INSERT INTO "TrainingLog" (
            "Name", "Training", "TrainingOrder", "Date", "ExerciseNumber",
            "Exercise", "Set", "Weight", "GoalReps", "Reps"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        ''',
        rows,
    )

    cur.close()
    conn.close()


def main() -> None:
    args = parse_args()
    ensure_database(args)
    seed_database(args)
    print(f"Seeded database '{args.target_db}' on {args.admin_host}:{args.admin_port}.")
if __name__ == "__main__":
    main()
