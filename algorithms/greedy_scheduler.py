def greedy_schedule(tasks, capacity):
    tasks_sorted = sorted(tasks, key=lambda x: x["value"] / x["time"], reverse=True)
    selected = []
    total_time = 0
    total_value = 0

    for task in tasks_sorted:
        if total_time + task["time"] <= capacity:
            selected.append(task)
            total_time += task["time"]
            total_value += task["value"]

    return selected, total_time, total_value
