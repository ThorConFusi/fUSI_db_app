import os
import customtkinter as ctk
from tkinter import ttk
from tkinter import filedialog, messagebox
from gui.dialogs import StimuliEditPopup
from services.export_service import StimuliExportService
from services.stimuli_formatter import StimuliFormatter


class StimuliTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self._sort_state = {}
        self.export_service = StimuliExportService()
        self._build_ui()
        self._style_treeview()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        # --- Erste Reihe: fünf Buttons ---
        self.btn_load = ctk.CTkButton(self, text="Load trial", command=self._load_csv)
        self.btn_load.grid(row=0, column=0, padx=10, pady=10)

        self.btn_new = ctk.CTkButton(self, text="New line", command=self._new_line)
        self.btn_new.grid(row=0, column=1, padx=10, pady=10)

        self.btn_edit = ctk.CTkButton(self, text="Edit line", command=self._edit_line)
        self.btn_edit.grid(row=0, column=2, padx=10, pady=10)

        self.btn_delete = ctk.CTkButton(self, text="Delete line", command=self._delete_line)
        self.btn_delete.grid(row=0, column=3, padx=10, pady=10)

        self.btn_save = ctk.CTkButton(self, text="Save trial", command=self._export_csv)
        self.btn_save.grid(row=0, column=4, padx=10, pady=10)

        # --- Treeview mit 7 Spalten ---
        columns = (
            "pause",
            "visual_stim",
            "acoustic_stim",
            "whisker_stim",
            "odour_stim",
            "air_puff",
            "duration_ms"
        )

        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)

        # Spalten-Header definieren
        self._headings = {
            "pause": "Pause",
            "visual_stim": "Visual Stim",
            "acoustic_stim": "Acoustic Stim",
            "whisker_stim": "Whisker Stim",
            "odour_stim": "Odour Stim",
            "air_puff": "Air Puff",
            "duration_ms": "Duration (ms)"
        }

        for col, text in self._headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, anchor="center", stretch=True, width=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=5, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

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
    # Sorting (unverändert übernommen)
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

    def _new_line(self):
        popup = StimuliEditPopup(
            master=self,
            initial_values={},   # später kannst du hier Treeview-Werte übergeben
            on_submit=self._add_line_to_tree
        )

    def _edit_line(self):
        selected = self.tree.focus()
        if not selected:
            return  # oder messagebox.showinfo("Info", "Bitte eine Zeile auswählen.")

        values = self.tree.item(selected, "values")

        # Werte in dict umwandeln
        initial = {
            "pause": values[0] == "True",
            "visual_stim": values[1],
            "acoustic_stim": values[2],
            "whisker_stim": values[3] == "True",
            "odour_stim": values[4] == "True",
            "air_puff": values[5] == "True",
            "duration_ms": values[6]
        }

        # Popup öffnen
        StimuliEditPopup(
            master=self,
            initial_values=initial,
            on_submit=lambda data: self._update_line_in_tree(selected, data)
        )

    def _add_line_to_tree(self, data):
        row = [
            data["pause"],
            data["visual_stim"],
            data["acoustic_stim"],
            data["whisker_stim"],
            data["odour_stim"],
            data["air_puff"],
            data["duration_ms"]
        ]

        cleaned = StimuliFormatter.clean_row_for_tree(row)

        self.tree.insert("", "end", values=tuple(cleaned))

    def _update_line_in_tree(self, item_id, data):
        row = [
            data["pause"],
            data["visual_stim"],
            data["acoustic_stim"],
            data["whisker_stim"],
            data["odour_stim"],
            data["air_puff"],
            data["duration_ms"]
        ]

        cleaned = StimuliFormatter.clean_row_for_tree(row)

        self.tree.item(item_id, values=tuple(cleaned))

    def _delete_line(self):
        selected = self.tree.focus()
        if not selected:
            # Optional:
            # messagebox.showinfo("Info", "Bitte eine Zeile auswählen.")
            return

        self.tree.delete(selected)

    def _export_csv(self):
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        default_dir = os.path.join(project_root, "01_Protocol_Config_Files")

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="CSV speichern",
            initialdir=default_dir
        )

        if not file_path:
            return

        ok = self.export_service.export_stimuli_to_csv(
            file_path=file_path,
            tree=self.tree,
            headings=self._headings
        )

        if ok:
            messagebox.showinfo("Export erfolgreich", f"CSV gespeichert:\n{file_path}")
        else:
            messagebox.showerror("Fehler", "Export fehlgeschlagen.")

    def _load_csv(self):
        # Dateidialog
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="CSV laden"
        )

        if not file_path:
            return

        # Treeview leeren
        for item in self.tree.get_children():
            self.tree.delete(item)

        # CSV laden
        rows = self.export_service.load_stimuli_from_csv(file_path)

        if rows is None:
            messagebox.showerror("Fehler", "CSV konnte nicht geladen werden.")
            return

        # Einfügen in Treeview
        for row in rows:
            cleaned = StimuliFormatter.clean_row_for_tree(row)
            self.tree.insert("", "end", values=tuple(cleaned))

        messagebox.showinfo("CSV geladen", f"Trial erfolgreich geladen:\n{file_path}")
