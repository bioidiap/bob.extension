from .new_version import main as new_version
from .dependency_graph import main as dependency_graph

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
