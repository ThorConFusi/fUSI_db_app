import csv

class SessionExportService:
    """
    GUI-independent service for session data export from treeview in display_sessions_tab.
    """

    def export_treeview_to_csv(self, file_path, tree, mouse_filter, exp_filter, headings):
        """
        Exports content of a Treeview into a CSV-file.

        :param file_path: Zielpfad
        :param tree: ttk.Treeview
        :param mouse_filter: aktueller Mouse-Filter
        :param exp_filter: aktueller Experiment-Filter
        :param headings: dict {column_key: heading_text}
        """

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Filter am Anfang
            writer.writerow([f"# Mouse: {mouse_filter}"])
            writer.writerow([f"# Experiment: {exp_filter}"])
            writer.writerow([])

            # Header
            header_row = [headings[col] for col in tree["columns"]]
            writer.writerow(header_row)

            # Daten
            for item in tree.get_children():
                row = tree.item(item, "values")
                writer.writerow(row)

        return True
