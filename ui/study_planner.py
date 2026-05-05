"""
ui/study_planner.py — Study Planner module UI.
Calculates study schedules based on available time and task priority.
"""

import tkinter as tk
from tkinter import messagebox
from ui.theme import (COLORS, FONT_BODY, FONT_SUBHEAD, FONT_SMALL,
                      section_header, card, accent_button, ghost_button,
                      output_box, write_output)

from algorithms.greedy_scheduler import greedy_schedule
from algorithms.dp_knapsack import dp_knapsack


class StudyPlannerFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self._tasks = []
        self._build()

    def _build(self):
        section_header(self,
                       "📅  Study Planner",
                       "Optimize your study sessions using Greedy Scheduling")

        body = tk.Frame(self, bg=COLORS["bg_dark"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        body.columnconfigure(0, weight=0, minsize=300)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_input_panel(body)
        self._build_results_panel(body)

    def _build_input_panel(self, parent):
        pnl = card(parent)
        pnl.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(pnl, text="Plan Details", font=FONT_SUBHEAD,
                 fg=COLORS["accent"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12).pack(fill="x", pady=10)

        tk.Frame(pnl, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 10))

        tk.Label(pnl, text="Available Time (hrs)", font=FONT_BODY,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12).pack(fill="x", pady=(10, 2))

        self._time_entry = tk.Entry(
            pnl, font=FONT_BODY, bg=COLORS["bg_hover"],
            fg=COLORS["text_primary"], insertbackground=COLORS["accent"],
            relief="flat", bd=4)
        self._time_entry.pack(fill="x", padx=12, pady=(0, 15))

        tk.Frame(pnl, bg=COLORS["border"], height=1).pack(fill="x", pady=(0, 10))

        tk.Label(pnl, text="Task Name", font=FONT_BODY,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12).pack(fill="x", pady=(5, 2))

        self._task_name = tk.Entry(
            pnl, font=FONT_BODY, bg=COLORS["bg_hover"],
            fg=COLORS["text_primary"], insertbackground=COLORS["accent"],
            relief="flat", bd=4)
        self._task_name.pack(fill="x", padx=12, pady=2)

        tk.Label(pnl, text="Duration (hrs)", font=FONT_BODY,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12).pack(fill="x", pady=(8, 2))

        self._task_duration = tk.Entry(
            pnl, font=FONT_BODY, bg=COLORS["bg_hover"],
            fg=COLORS["text_primary"], insertbackground=COLORS["accent"],
            relief="flat", bd=4)
        self._task_duration.pack(fill="x", padx=12, pady=2)

        tk.Label(pnl, text="Priority (value)", font=FONT_BODY,
                 fg=COLORS["text_secondary"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12).pack(fill="x", pady=(8, 2))

        self._task_priority = tk.Entry(
            pnl, font=FONT_BODY, bg=COLORS["bg_hover"],
            fg=COLORS["text_primary"], insertbackground=COLORS["accent"],
            relief="flat", bd=4)
        self._task_priority.pack(fill="x", padx=12, pady=2)

        accent_button(pnl, "➕  Add Task", command=self._add_task).pack(
            fill="x", padx=12, pady=10)

        tk.Frame(pnl, bg=COLORS["border"], height=1).pack(fill="x", pady=10)

        accent_button(pnl, "🚀  Generate Plan", command=self._generate_plan).pack(
            fill="x", padx=12, pady=5)

        ghost_button(pnl, "✕  Clear All", command=self._clear).pack(
            fill="x", padx=12, pady=5)

    def _build_results_panel(self, parent):
        right = tk.Frame(parent, bg=COLORS["bg_dark"])
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        res_card = card(right)
        res_card.grid(row=0, column=0, sticky="nsew")

        tk.Label(res_card, text="Optimized Schedule", font=FONT_SUBHEAD,
                 fg=COLORS["accent"], bg=COLORS["bg_panel"],
                 anchor="w", padx=12).pack(fill="x", pady=10)

        tk.Frame(res_card, bg=COLORS["border"], height=1).pack(fill="x")

        self._output = output_box(res_card, height=20)

    def _add_task(self):
        name = self._task_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Task name cannot be empty.")
            return

        try:
            duration = int(self._task_duration.get().strip())
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Duration must be a positive number.")
            return

        try:
            priority = int(self._task_priority.get().strip())
            if priority <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Priority must be a positive number.")
            return

        self._tasks.append((name, duration, priority))

        self._task_name.delete(0, tk.END)
        self._task_duration.delete(0, tk.END)
        self._task_priority.delete(0, tk.END)

        messagebox.showinfo("Task Added", f"'{name}' ({duration} hrs, priority {priority}) added!")

    def _generate_plan(self):
        if not self._time_entry.get().strip():
            messagebox.showwarning("Input Error", "Please enter available time.")
            return

        try:
            available_time = int(self._time_entry.get().strip())
            if available_time <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Available time must be a positive number.")
            return

        if not self._tasks:
            messagebox.showwarning("Input Error", "Please add at least one task.")
            return

        tasks = [
            {"name": t[0], "time": t[1], "value": t[2]}
            for t in self._tasks
        ]

        greedy_result, greedy_time, greedy_value = greedy_schedule(tasks, available_time)
        selected, total_time, total_value = dp_knapsack(tasks, available_time)

        output_text = "═══ Optimized Study Plan ═══\n\n"

        output_text += "📋 Greedy Selected Tasks:\n"
        if greedy_result:
            for task in greedy_result:
                output_text += f"  • {task['name']} ({task['time']} hrs, priority {task['value']})\n"
        else:
            output_text += "  No tasks fit within available time.\n"
        output_text += f"  ⏱ Greedy Time Used : {greedy_time} hrs\n"
        output_text += f"  ⭐ Greedy Priority  : {greedy_value}\n"

        output_text += "\n🧠 DP Knapsack Selected Tasks:\n"
        if selected:
            for task in selected:
                output_text += f"  • {task['name']} ({task['time']} hrs, priority {task['value']})\n"
        else:
            output_text += "  No tasks fit within available time.\n"
        output_text += f"\n⏱  Total Time Used : {total_time} hrs"
        output_text += f"\n⭐ Total Priority  : {total_value}"

        write_output(self._output, output_text)

    def _clear(self):
        self._tasks = []
        self._time_entry.delete(0, tk.END)
        self._task_name.delete(0, tk.END)
        self._task_duration.delete(0, tk.END)
        self._task_priority.delete(0, tk.END)
        write_output(self._output, "")
