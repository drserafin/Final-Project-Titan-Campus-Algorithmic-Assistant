"""
app.py - TCAApp window + top navbar routing.
"""

import tkinter as tk

from ui.theme import COLORS, FONT_LOGO, FONT_NAV, gradient_bar
from ui.campus_navigator import CampusNavigatorFrame
from ui.study_planner import StudyPlannerFrame
from ui.notes_search import NotesSearchFrame
from ui.algorithm_info import AlgorithmInfoFrame


class TCAApp(tk.Tk):
    MODULES = [
        ("Navigator", CampusNavigatorFrame),
        ("Planner", StudyPlannerFrame),
        ("Search", NotesSearchFrame),
        ("Info", AlgorithmInfoFrame),
    ]

    def __init__(self):
        super().__init__()
        self.title("Titan Campus Algorithmic Assistant (TCAA)")
        self.geometry("1200x750")
        self.minsize(960, 620)
        self.configure(bg=COLORS["bg_dark"])
        self.resizable(True, True)

        self._active_idx = tk.IntVar(value=0)
        self._nav_buttons: list[tk.Button] = []
        self._frames: dict[int, tk.Frame] = {}

        self._build_navbar()
        self._build_content_area()
        self._show_module(0)

    def _build_navbar(self):
        nav = tk.Frame(self, bg=COLORS["nav_bg"], height=62)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)

        brand = tk.Frame(nav, bg=COLORS["nav_bg"])
        brand.pack(side="left", fill="y", padx=(14, 24))

        tk.Label(
            brand,
            text="▣",
            font=("Courier New", 20, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["nav_bg"],
        ).pack(side="left", pady=13)
        tk.Label(
            brand,
            text=" TITAN CAMPUS ALGORITHMIC ASSISTANT",
            font=FONT_LOGO,
            fg=COLORS["text_primary"],
            bg=COLORS["nav_bg"],
        ).pack(side="left")

        tk.Frame(nav, bg=COLORS["border"], width=1).pack(side="left", fill="y", pady=11)

        btn_area = tk.Frame(nav, bg=COLORS["nav_bg"])
        btn_area.pack(side="left", padx=8, fill="y")

        for idx, (label, _) in enumerate(self.MODULES):
            btn = tk.Button(
                btn_area,
                text=label,
                font=FONT_NAV,
                fg=COLORS["text_secondary"],
                bg=COLORS["nav_bg"],
                activebackground=COLORS["bg_hover"],
                activeforeground=COLORS["text_primary"],
                relief="flat",
                bd=0,
                padx=15,
                pady=0,
                cursor="hand2",
                command=lambda i=idx: self._show_module(i),
            )
            btn.pack(side="left", fill="y")
            btn.bind("<Enter>", lambda _e, b=btn, i=idx: self._on_hover(b, i, True))
            btn.bind("<Leave>", lambda _e, b=btn, i=idx: self._on_hover(b, i, False))
            self._nav_buttons.append(btn)

        tk.Label(
            nav,
            text="Campus Navigator Module",
            font=("Courier New", 11),
            fg=COLORS["text_secondary"],
            bg=COLORS["nav_bg"],
        ).pack(side="right", padx=20)

        gradient_bar(self, height=3)

    def _on_hover(self, btn: tk.Button, idx: int, entering: bool):
        if idx == self._active_idx.get():
            return
        btn.configure(
            fg=COLORS["text_primary"] if entering else COLORS["text_secondary"],
            bg=COLORS["bg_hover"] if entering else COLORS["nav_bg"],
        )

    def _set_active_nav(self, idx: int):
        for i, btn in enumerate(self._nav_buttons):
            if i == idx:
                btn.configure(fg=COLORS["accent"], bg=COLORS["bg_hover"])
            else:
                btn.configure(fg=COLORS["text_secondary"], bg=COLORS["nav_bg"])

    def _build_content_area(self):
        self._content = tk.Frame(self, bg=COLORS["bg_dark"])
        self._content.pack(fill="both", expand=True)

    def _show_module(self, idx: int):
        if idx not in self._frames:
            _, frame_class = self.MODULES[idx]
            frame = frame_class(self._content)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._frames[idx] = frame

        for i, frame in self._frames.items():
            frame.lift() if i == idx else frame.lower()

        self._active_idx.set(idx)
        self._set_active_nav(idx)


if __name__ == "__main__":
    TCAApp().mainloop()
