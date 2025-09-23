"""Domain-level operations related to trainings."""
from __future__ import annotations

from pandas import DataFrame

from ..db.repository import TrainingRepository, get_repository


class TrainingService:
    def __init__(self, repository: TrainingRepository | None = None) -> None:
        self._repository = repository or get_repository()

    def list_users(self) -> list[str]:
        return self._repository.get_user_names()

    def list_trainings(self, user: str) -> tuple[list[str], list[str]]:
        return self._repository.get_trainings(user)

    def fetch_last_training(self, user: str, training: str) -> DataFrame:
        return self._repository.get_last_training(user, training)

    def next_training_order(self, user: str):
        return self._repository.get_next_training_order(user)
