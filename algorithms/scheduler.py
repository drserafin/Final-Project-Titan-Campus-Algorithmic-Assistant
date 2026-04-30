"""
algorithms/scheduler.py — Greedy and DP scheduling algorithms.

Task format:
    {"name": str, "time": int, "value": int}

Zero GUI / tkinter imports — pure Python only.

Time references:
    Greedy  — O(n log n)   [sort by value/time ratio]
    DP      — O(n · W)     [pseudo-polynomial, W = capacity]
"""


# ── Greedy Scheduler ─────────────────────────────────────────────────────────

def greedy_schedule(tasks: list[dict], capacity: int) -> dict:
    """
    Greedy task scheduler — selects tasks by best value-per-hour ratio
    until the time budget is exhausted.

    Args:
        tasks:    list of {"name", "time", "value"}
        capacity: total available hours

    Returns:
        {
          "selected":    list[dict],   # chosen tasks
          "total_time":  int,
          "total_value": int,
        }

    Time:  O(n log n)
    Space: O(n)
    """
    # TODO: implement greedy scheduler
    raise NotImplementedError("Greedy scheduler not yet implemented")


# ── DP 0/1 Knapsack ──────────────────────────────────────────────────────────

def dp_knapsack(tasks: list[dict], capacity: int) -> dict:
    """
    0/1 Knapsack via dynamic programming — finds the globally optimal
    subset of tasks that maximizes total value within the time budget.

    Args:
        tasks:    list of {"name", "time", "value"}
        capacity: total available hours (integer)

    Returns:
        {
          "selected":    list[dict],   # chosen tasks
          "total_time":  int,
          "total_value": int,
          "dp_table":    list[list[int]],  # full DP table (optional display)
        }

    Time:  O(n · W)    — pseudo-polynomial
    Space: O(n · W)
    """
    # TODO: implement DP knapsack
    raise NotImplementedError("DP Knapsack not yet implemented")
