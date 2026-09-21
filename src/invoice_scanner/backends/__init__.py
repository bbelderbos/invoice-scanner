from collections.abc import Callable
from importlib.metadata import entry_points
from pathlib import Path

Backend = Callable[[Path, str], str]

_GROUP = "invoice_scanner.backends"


def available() -> list[str]:
    return sorted({ep.name for ep in entry_points(group=_GROUP)})


def get_backend(name: str, model: str | None = None) -> Backend:
    for ep in entry_points(group=_GROUP):
        if ep.name == name:
            make = ep.load()  # make(model=None) -> Backend
            return make(model)
    raise ValueError(f"unknown backend {name!r}; available: {', '.join(available()) or 'none'}")
