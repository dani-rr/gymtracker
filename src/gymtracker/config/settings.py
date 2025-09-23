"""Configuration loading utilities for gymtracker."""
from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any


@dataclass(frozen=True)
class Settings:
    database: str
    user: str
    password: str
    host: str
    port: int


_ENV_MAP = {
    "database": "GYMTRACKER_DB_NAME",
    "user": "GYMTRACKER_DB_USER",
    "password": "GYMTRACKER_DB_PASSWORD",
    "host": "GYMTRACKER_DB_HOST",
    "port": "GYMTRACKER_DB_PORT",
}


def _load_module() -> Any:
    """Resolve the module that provides default settings."""
    module_name = os.getenv("GYMTRACKER_SETTINGS_MODULE")
    if module_name:
        return importlib.import_module(module_name)

    try:
        from . import settings_local as module  # type: ignore
    except ImportError:
        from . import settings_example as module  # type: ignore
    return module


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Produce a cached Settings instance with environment overrides."""
    module = _load_module()
    values = {}
    for attr, env_key in _ENV_MAP.items():
        if env_key == "GYMTRACKER_DB_PORT":
            raw = os.getenv(env_key, getattr(module, attr))
            values[attr] = int(raw)
        else:
            values[attr] = os.getenv(env_key, getattr(module, attr))

    return Settings(**values)


settings = get_settings()
