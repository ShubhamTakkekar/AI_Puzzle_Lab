"""Data structures for search algorithm results and metrics."""

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class SearchResult:
    """Standardized result object returned by all search algorithms.

    Attributes:
        success: Whether a valid goal path was found.
        path: Ordered list of states from initial state to goal state.
        actions: Ordered list of actions taken between states.
        nodes_explored: Total number of states popped/expanded from frontier.
        max_frontier_size: Peak number of states held in frontier concurrently.
        execution_time_sec: Wall-clock execution time in seconds.
        solution_length: Number of moves/actions in the solution (len(path) - 1).
        error_message: Explanatory error message if search failed or timed out.
        algorithm_name: Name of the algorithm that produced this result.
    """

    success: bool
    path: List[Any] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    nodes_explored: int = 0
    max_frontier_size: int = 0
    execution_time_sec: float = 0.0
    solution_length: int = 0
    error_message: Optional[str] = None
    algorithm_name: str = ""

    def summary(self) -> dict:
        """Return a dictionary summary of the search metrics."""
        return {
            "algorithm": self.algorithm_name,
            "success": self.success,
            "solution_length": self.solution_length,
            "nodes_explored": self.nodes_explored,
            "max_frontier_size": self.max_frontier_size,
            "execution_time_ms": round(self.execution_time_sec * 1000, 3),
            "error_message": self.error_message or "None",
        }
