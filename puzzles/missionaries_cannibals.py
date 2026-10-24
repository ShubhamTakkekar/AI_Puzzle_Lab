"""Missionaries and Cannibals river crossing puzzle environment and constraints."""

from typing import List, Optional, Tuple

# State tuple: (missionaries_left, cannibals_left, boat_position)
# boat_position: 0 = Left bank, 1 = Right bank
INITIAL_STATE: Tuple[int, int, int] = (3, 3, 0)
GOAL_STATE: Tuple[int, int, int] = (0, 0, 1)
TOTAL_MISSIONARIES = 3
TOTAL_CANNIBALS = 3
BOAT_CAPACITY = 2


class MissionariesCannibals:
    """Environment simulating the Missionaries and Cannibals river crossing problem."""

    def __init__(
        self,
        total_m: int = TOTAL_MISSIONARIES,
        total_c: int = TOTAL_CANNIBALS,
        boat_cap: int = BOAT_CAPACITY,
    ) -> None:
        self.total_m = total_m
        self.total_c = total_c
        self.boat_cap = boat_cap
        self.initial_state = (total_m, total_c, 0)
        self.goal_state = (0, 0, 1)

    @staticmethod
    def is_valid_counts(m_left: int, c_left: int, total_m: int = 3, total_c: int = 3) -> bool:
        """Verify that counts are within domain bounds."""
        return 0 <= m_left <= total_m and 0 <= c_left <= total_c

    @staticmethod
    def is_safe(m_left: int, c_left: int, total_m: int = 3, total_c: int = 3) -> bool:
        """Check if the state satisfies the cannibalism safety constraint.

        Cannibals must never outnumber missionaries on either bank,
        unless there are zero missionaries on that bank.
        """
        if not MissionariesCannibals.is_valid_counts(m_left, c_left, total_m, total_c):
            return False

        m_right = total_m - m_left
        c_right = total_c - c_left

        # Check left bank constraint
        if m_left > 0 and c_left > m_left:
            return False

        # Check right bank constraint
        if m_right > 0 and c_right > m_right:
            return False

        return True

    @staticmethod
    def explain_state_safety(m_left: int, c_left: int, total_m: int = 3, total_c: int = 3) -> str:
        """Provide human-readable explanation of why a state is safe or rejected."""
        if not MissionariesCannibals.is_valid_counts(m_left, c_left, total_m, total_c):
            return f"Invalid: Counts ({m_left}M, {c_left}C) are outside allowed range [0, 3]."

        m_right = total_m - m_left
        c_right = total_c - c_left

        if m_left > 0 and c_left > m_left:
            return (
                f"Violation on Left Bank: {c_left} Cannibals outnumber {m_left} Missionaries! "
                "The missionaries would be devoured."
            )

        if m_right > 0 and c_right > m_right:
            return (
                f"Violation on Right Bank: {c_right} Cannibals outnumber {m_right} Missionaries! "
                "The missionaries would be devoured."
            )

        return "Safe: Missionaries are never outnumbered on either riverbank."

    def is_goal(self, state: Tuple[int, int, int]) -> bool:
        """Check if all missionaries, cannibals, and the boat are on the right bank."""
        return state == self.goal_state

    def get_neighbors(
        self, state: Tuple[int, int, int]
    ) -> List[Tuple[str, Tuple[int, int, int], float]]:
        """Generate all legal, safe river crossings from current state."""
        m_left, c_left, boat = state
        neighbors: List[Tuple[str, Tuple[int, int, int], float]] = []

        # Generate all passenger loads up to boat_cap
        moves = []
        for dm in range(self.boat_cap + 1):
            for dc in range(self.boat_cap + 1 - dm):
                if 1 <= (dm + dc) <= self.boat_cap:
                    parts = []
                    if dm > 0:
                        parts.append(f"{dm} Missionary" if dm == 1 else f"{dm} Missionaries")
                    if dc > 0:
                        parts.append(f"{dc} Cannibal" if dc == 1 else f"{dc} Cannibals")
                    moves.append((dm, dc, " and ".join(parts)))

        if boat == 0:  # Boat on Left Bank -> crossing to Right
            for dm, dc, desc in moves:
                if dm > m_left or dc > c_left:
                    continue
                new_m_left = m_left - dm
                new_c_left = c_left - dc
                if self.is_safe(new_m_left, new_c_left, self.total_m, self.total_c):
                    next_state = (new_m_left, new_c_left, 1)
                    action = f"Cross to Right Bank with {desc}"
                    neighbors.append((action, next_state, 1.0))
        else:  # Boat on Right Bank -> returning to Left
            m_right = self.total_m - m_left
            c_right = self.total_c - c_left
            for dm, dc, desc in moves:
                if dm > m_right or dc > c_right:
                    continue
                new_m_left = m_left + dm
                new_c_left = c_left + dc
                if self.is_safe(new_m_left, new_c_left, self.total_m, self.total_c):
                    next_state = (new_m_left, new_c_left, 0)
                    action = f"Return to Left Bank with {desc}"
                    neighbors.append((action, next_state, 1.0))

        return neighbors

    def explain_crossing(self, prev_state: Tuple[int, int, int], next_state: Tuple[int, int, int]) -> str:
        """Provide detailed human-readable explanation of river crossing."""
        m1, c1, b1 = prev_state
        m2, c2, b2 = next_state
        dm = abs(m1 - m2)
        dc = abs(c1 - c2)

        parts = []
        if dm > 0:
            parts.append(f"{dm} Missionary" if dm == 1 else f"{dm} Missionaries")
        if dc > 0:
            parts.append(f"{dc} Cannibal" if dc == 1 else f"{dc} Cannibals")
        passengers = " and ".join(parts) if parts else "Empty boat"

        direction = "Left Bank to Right Bank" if b1 == 0 else "Right Bank to Left Bank"
        return (
            f"Boat crossed from {direction} carrying {passengers}. "
            f"Resulting banks: Left Bank ({m2}M, {c2}C), Right Bank ({self.total_m - m2}M, {self.total_c - c2}C)."
        )

    def state_description(self, state: Tuple[int, int, int]) -> dict:
        """Return a structured representation of the river scene."""
        m_left, c_left, boat = state
        m_right = self.total_m - m_left
        c_right = self.total_c - c_left
        return {
            "left_missionaries": m_left,
            "left_cannibals": c_left,
            "right_missionaries": m_right,
            "right_cannibals": c_right,
            "boat_location": "Left Bank" if boat == 0 else "Right Bank",
            "is_safe": self.is_safe(m_left, c_left, self.total_m, self.total_c),
        }
