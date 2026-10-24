"""Classical AI search algorithms package."""

from algorithms.astar import astar_search
from algorithms.bfs import breadth_first_search
from algorithms.dfs import depth_first_search
from algorithms.search_result import SearchResult

__all__ = ["SearchResult", "breadth_first_search", "depth_first_search", "astar_search"]
