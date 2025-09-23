"""Application entry point and orchestration."""
from __future__ import annotations

if __package__ is None or __package__ == "":  # pragma: no cover - script execution fallback
    import sys
    from pathlib import Path

    package_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(package_root))
    __package__ = "gymtracker"

from .services.training_service import TrainingService
from .ui.forms.timer import TimerForm
from .ui.forms.training import TrainingForm
from .ui.forms.user import UserForm


class GymTrackerApp:
    def __init__(self, training_service: TrainingService | None = None) -> None:
        self.training_service = training_service or TrainingService()

    def start(self) -> None:
        self.show_user_form()

    def show_user_form(self) -> None:
        user_form = UserForm(
            service=self.training_service,
            on_user_selected=self.show_training_form,
        )
        user_form.init_selection_user()

    def show_training_form(self, user: str) -> None:
        training_form = TrainingForm(
            user=user,
            service=self.training_service,
            on_training_selected=lambda training: self.show_timer_form(user, training),
            on_back=self.show_user_form,
        )
        training_form.init_selection_training()

    def show_timer_form(self, user: str, training: str) -> None:
        TimerForm(user=user, training=training, service=self.training_service)


def main() -> None:
    app = GymTrackerApp()
    app.start()


def run() -> None:
    main()


if __name__ == "__main__":
    run()
