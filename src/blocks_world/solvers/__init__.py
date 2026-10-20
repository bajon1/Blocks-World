"""Search algorithms used by the Blocks World project."""

from .bfs import bfs
from .dfs import dfs
from .idastar import ida_star

__all__ = ["bfs", "dfs", "ida_star"]
