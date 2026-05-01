def dp_knapsack(tasks, capacity):
    n = len(tasks)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if tasks[i - 1]["time"] <= w:
                dp[i][w] = max(
                    tasks[i - 1]["value"] + dp[i - 1][w - tasks[i - 1]["time"]],
                    dp[i - 1][w]
                )
            else:
                dp[i][w] = dp[i - 1][w]

    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(tasks[i - 1])
            w -= tasks[i - 1]["time"]

    selected.reverse()

    return selected, sum(t["time"] for t in selected), sum(t["value"] for t in selected)
