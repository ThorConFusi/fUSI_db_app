import customtkinter as ctk
from tkinter import ttk
from gui.dialogs import SessionDetailsPopup


class DisplaySessionsTab(ctk.CTkFrame):
    def __init__(self, master, mouse_service, session_service):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.session_service = session_service

        self._sort_state = {}

        self._build_ui()
        self._style_treeview()
        self._refresh_mouse_list()
        self._refresh_experiment_list()

        # Initial load
        self.mouse_combo.set("all")
        self.experiment_combo.set("all")
        self._on_filter_change()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        ctk.CTkLabel(self, text="Mouse:").grid(row=0, column=0, padx=10)
        self.mouse_combo = ctk.CTkComboBox(self, command=self._on_filter_change)
        self.mouse_combo.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(self, text="Experiment:").grid(row=0, column=2, padx=10)
        self.experiment_combo = ctk.CTkComboBox(self, command=self._on_filter_change)
        self.experiment_combo.grid(row=0, column=3, padx=10)

        ctk.CTkButton(self, text="Export csv").grid(row=0, column=4, padx=20)

        columns = ("mouse", "date", "session_number", "experiment", "session")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)

        self._headings = {
            "mouse": "Mouse",
            "date": "Date",
            "session_number": "Session #",
            "experiment": "Experiment",
            "session": "Session"
        }

        for col, text in self._headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=120, anchor="center")

        self.tree.bind("<Double-1>", self._on_row_double_click)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=5, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

    # ---------------------------------------------------------
    # Styling
    # ---------------------------------------------------------
    def _style_treeview(self):
        style = ttk.Style()
        try:
            style.theme_use("default")
        except:
            pass

        style.configure(
            "Treeview.Heading",
            background="#3377c8",
            foreground="#cacaca",
            font=("Arial", 11, "bold")
        )

        style.configure("Treeview", rowheight=24)
        style.map("Treeview", background=[("selected", "#797979")])

        self.tree.tag_configure("odd", background="#dadada")
        self.tree.tag_configure("even", background="white")

    # ---------------------------------------------------------
    # Mouse list
    # ---------------------------------------------------------
    def _refresh_mouse_list(self):
        ok, mice, err = self.mouse_service.get_alive_mice()
        if not ok or not mice:
            mice = ["all"]

        # remove accidental "all"
        mice_clean = [m for m in mice if m != "all"]

        values = ["all", "all living"] + mice_clean
        self.mouse_combo.configure(values=values)

    # ---------------------------------------------------------
    # Experiment list
    # ---------------------------------------------------------
    def _refresh_experiment_list(self):
        ok, exps, err = self.session_service.get_all_experiments()
        if not ok or not exps:
            exps = []
        self.experiment_combo.configure(values=["all"] + exps)

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------
    def _on_filter_change(self, _=None):
        mouse_filter = self.mouse_combo.get()
        exp_filter = self.experiment_combo.get()

        ok, all_sessions, err = self.session_service.get_all_sessions()
        if not ok:
            self._clear_tree()
            return

        # Filter by mouse
        if mouse_filter == "all":
            pass
        elif mouse_filter == "all living":
            ok, alive, err = self.mouse_service.get_alive_mice()
            if not ok:
                alive = []
            all_sessions = [s for s in all_sessions if s.get("Pyrat-ID") in alive]
        else:
            all_sessions = [s for s in all_sessions if s.get("Pyrat-ID") == mouse_filter]

        # Filter by experiment
        if exp_filter != "all":
            all_sessions = [s for s in all_sessions if s.get("Experiment") == exp_filter]

        self._fill_tree(all_sessions)

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------
    def _convert_for_sort(self, value):
        if value is None:
            return ""
        try:
            return float(value)
        except:
            return value.lower()

    def _sort_by_column(self, col):
        data = []
        for item in self.tree.get_children(""):
            raw = self.tree.set(item, col)
            key = self._convert_for_sort(raw)
            data.append((key, item))

        reverse = self._sort_state.get(col, False)
        self._sort_state[col] = not reverse

        data.sort(reverse=reverse)

        for index, (_, item) in enumerate(data):
            self.tree.move(item, "", index)

        for c in self.tree["columns"]:
            base = self._headings[c]
            if c == col:
                arrow = "▲" if not reverse else "▼"
                self.tree.heading(c, text=f"{base}   {arrow}")
            else:
                self.tree.heading(c, text=base)

    # ---------------------------------------------------------
    # Tree helpers
    # ---------------------------------------------------------
    def _clear_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def _fill_tree(self, sessions):
        self._clear_tree()
        for i, s in enumerate(sessions):
            tag = "odd" if i % 2 else "even"
            self.tree.insert(
                "",
                "end",
                values=(
                    s.get("Pyrat-ID"),
                    s.get("D.o.Recording"),
                    s.get("Session_number"),
                    s.get("Experiment"),
                    s.get("Session")
                ),
                tags=(tag,)
            )

    # ---------------------------------------------------------
    # Popup
    # ---------------------------------------------------------
    def _on_row_double_click(self, event):
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, "values")

        pyrat_id = values[0]
        date = values[1]
        session_number = values[2]

        ok_s, session_data, err_s = self.session_service.get_session_by_keys(
            pyrat_id, date, session_number
        )
        if not ok_s:
            session_data = {}

        ok_m, mouse_data, err_m = self.mouse_service.get_mouse_export_data(pyrat_id)
        if not ok_m:
            mouse_data = {}

        SessionDetailsPopup(self, mouse_data, session_data)
