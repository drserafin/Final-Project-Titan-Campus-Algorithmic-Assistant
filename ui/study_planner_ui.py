import tkinter as tk
from tkinter import messagebox
from algorithms.greedy_scheduler import greedy_schedule
from algorithms.dp_knapsack import dp_knapsack

class StudyPlannerFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tasks = []

        tk.Label(self, text="Task Name").grid(row=0, column=0)
        tk.Label(self, text="Time").grid(row=0, column=1)
        tk.Label(self, text="Value").grid(row=0, column=2)

        self.name_entry = tk.Entry(self)
        self.time_entry = tk.Entry(self)
        self.value_entry = tk.Entry(self)

        self.name_entry.grid(row=1, column=0)
        self.time_entry.grid(row=1, column=1)
        self.value_entry.grid(row=1, column=2)

        tk.Button(self, text="Add Task", command=self.add_task).grid(row=1, column=3)

        tk.Label(self, text="Available Time").grid(row=2, column=0)
        self.capacity_entry = tk.Entry(self)
        self.capacity_entry.grid(row=2, column=1)

        tk.Button(self, text="Run Greedy", command=self.run_greedy).grid(row=3, column=0)
        tk.Button(self, text="Run DP", command=self.run_dp).grid(row=3, column=1)

        self.output = tk.Text(self, height=10, width=60)
        self.output.grid(row=4, column=0, columnspan=4)

    def add_task(self):
        try:
            task = {
                "name": self.name_entry.get(),
                "time": int(self.time_entry.get()),
                "value": int(self.value_entry.get())
            }
            self.tasks.append(task)
            messagebox.showinfo("Success", "Task added.")
        except:
            messagebox.showerror("Error", "Invalid input.")

    def run_greedy(self):
        try:
            capacity = int(self.capacity_entry.get())
            selected, total_time, total_value = greedy_schedule(self.tasks, capacity)
            self.display_result("Greedy", selected, total_time, total_value)
        except:
            messagebox.showerror("Error", "Invalid capacity.")

    def run_dp(self):
        try:
            capacity = int(self.capacity_entry.get())
            selected, total_time, total_value = dp_knapsack(self.tasks, capacity)
            self.display_result("DP", selected, total_time, total_value)
        except:
            messagebox.showerror("Error", "Invalid capacity.")

    def display_result(self, method, selected, total_time, total_value):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"{method} Result:\n")
        for task in selected:
            self.output.insert(tk.END, f"{task['name']} (Time: {task['time']}, Value: {task['value']})\n")
        self.output.insert(tk.END, f"\nTotal Time: {total_time}\n")
        self.output.insert(tk.END, f"Total Value: {total_value}\n")
