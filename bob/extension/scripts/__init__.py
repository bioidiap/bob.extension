from . import click_helper  # noqa: F401
from .main_cli import main as main_cli  # noqa: F401

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith("_")]
