import customtkinter as ctk
from tkinter import ttk

class DisplaySessionsTab(ctk.CTkFrame):
    def __init__(self, master, mouse_service, session_service):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.session_service = session_service

        self._sort_state = {}  # track sort order per column

        self._build_ui()


    # UI
    def _build_ui(self):
        # Mouse selection
        ctk.CTkLabel(self, text="Mouse:").grid(row=0, column=0, padx=10, pady=10)
        self.mouse_combo = ctk.CTkComboBox(
            self,
            values=self.mouse_service.get_alive_mice(),
            command=self._on_filter_change
        )
        self.mouse_combo.set("all")
        self.mouse_combo.grid(row=0, column=1, padx=10, pady=10)

        # Experiment selection
        ctk.CTkLabel(self, text="Experiment:").grid(row=0, column=2, padx=10, pady=10)
        self.experiment_combo = ctk.CTkComboBox(
            self,
            values=["all"] + self.session_service.get_all_experiments(),
            command=self._on_filter_change
        )
        self.experiment_combo.set("all")
        self.experiment_combo.grid(row=0, column=3, padx=10, pady=10)

        # Treeview
        columns = ("mouse", "date", "session_number", "experiment", "session")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")

        headings = {
            "mouse": "Mouse",
            "date": "Date",
            "session_number": "Session #",
            "experiment": "Experiment",
            "session": "Session"
        }

        for col, text in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=120, anchor="center")

        self.tree.bind("<Double-1>", self._on_row_double_click)

        self.tree.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)


    # Filtering logic
    def _on_filter_change(self, _=None):
        mouse_filter = self.mouse_combo.get()
        exp_filter = self.experiment_combo.get()

        ok, all_sessions = self.session_service.get_all_sessions()
        if not ok:
            self._clear_tree()
            return

        # Filter by mouse
        if mouse_filter != "all":
            all_sessions = [s for s in all_sessions if s.get("Pyrat-ID") == mouse_filter]

        # Filter by experiment
        if exp_filter != "all":
            all_sessions = [s for s in all_sessions if s.get("Experiment") == exp_filter]

        self._fill_tree(all_sessions)


    # Sorting logic
    def _sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Toggle sort order
        reverse = self._sort_state.get(col, False)
        self._sort_state[col] = not reverse

        # Sort
        data.sort(reverse=reverse)

        # Reinsert rows
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)


    # Tree helpers
    def _clear_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def _fill_tree(self, sessions):
        self._clear_tree()
        for s in sessions:
            self.tree.insert(
                "",
                "end",
                values=(
                    s.get("Pyrat-ID"),
                    s.get("D.o.Recording"),
                    s.get("Session_number"),
                    s.get("Experiment"),
                    s.get("Session")
                )
            )


    def _on_row_double_click(self, event):
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, "values")

        pyrat_id = values[0]
        date = values[1]
        session_number = values[2]

        # Get session data from DB
        ok_s, session_data = self.session_service.get_session_by_keys(
            pyrat_id, date, session_number
        )
        if not ok_s:
            session_data = {}

        # Get mouse data from DB
        ok_m, mouse_data = self.mouse_service.get_mouse_export_data(pyrat_id)
        if not ok_m:
            mouse_data = {}

        SessionDetailsPopup(self, mouse_data, session_data)


class SessionDetailsPopup(ctk.CTkToplevel):
    def __init__(self, master, mouse_data: dict, session_data: dict):
        super().__init__(master)
        self.title(f"Session Details – {session_data.get('Pyrat-ID')}")
        self.minsize(700, 400)  # Mindestbreite
        self.geometry("900x600")  # Startgröße, aber dynamisch anpassbar
        self.grab_set()

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Headlines
        ctk.CTkLabel(container, text="Mouse Information", font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        ctk.CTkLabel(container, text="Session Information", font=("Arial", 16, "bold")).grid(
            row=0, column=1, sticky="w", pady=(0, 10)
        )

        # Left column: Mouse data
        mouse_fields = [
            "Pyrat-ID", "Sex", "Line", "D.o.Birth",
            "D.o.Surgery", "T.o.Surgery",
            "D.o.Death", "T.o.Death",
            "Kill_method", "Kill_purpose", "Kill_comment"
        ]

        row = 1
        for key in mouse_fields:
            ctk.CTkLabel(container, text=f"{key}:").grid(
                row=row, column=0, sticky="w", padx=10, pady=3
            )
            ctk.CTkLabel(container, text=str(mouse_data.get(key, "—"))).grid(
                row=row, column=0, sticky="e", padx=40, pady=3
            )
            row += 1

        # Right column: Session data
        session_fields = {
            "Pyrat-ID": session_data.get("Pyrat-ID"),
            "D.o.Recording": session_data.get("D.o.Recording"),
            "T.o.Recording": session_data.get("T.o.Recording"),
            "Session_number": session_data.get("Session_number"),
            "Experiment": session_data.get("Experiment"),
            "Session": session_data.get("Session"),
        }

        btn_row = row - 1
        row = 1
        for key, value in session_fields.items():
            ctk.CTkLabel(container, text=f"{key}:").grid(
                row=row, column=1, sticky="w", padx=10, pady=3
            )
            ctk.CTkLabel(container, text=str(value)).grid(
                row=row, column=1, sticky="e", padx=40, pady=3
            )
            row += 1

        # Session comment
        footer = ctk.CTkFrame(self)
        footer.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(footer, text="Session Comment:", font=("Arial", 14, "bold")).pack(anchor="w")

        comment_box = ctk.CTkTextbox(footer, width=680, height=120)
        comment_box.insert("0.0", str(session_data.get("Session_comment", "")))
        comment_box.configure(state="disabled")
        comment_box.pack(fill="x", pady=5)

        # Close button
        ctk.CTkButton(container, text="Close", command=self.destroy).grid(
            row=btn_row, column=1, pady=(0, 20)
        )

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

