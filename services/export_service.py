import csv
import os
import datetime
from services.stimuli_formatter import StimuliFormatter


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


class SacrificeExportService:
    """
    GUI-independent service for Export of Sacrifice/Kill information into a local HTML file.
    """

    def build_html(self, pyrat_id, dod, tod, method, purpose, comment):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Sacrifice information</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #333; }}
                table {{
                    border-collapse: collapse;
                    width: 60%;
                }}
                td, th {{
                    border: 1px solid #999;
                    padding: 8px;
                }}
                th {{
                    background-color: #eee;
                }}
            </style>
        </head>
        <body>
            <h2>Sacrifice information</h2>

            <table>
                <tr><th>Pyrat ID</th><td>{pyrat_id}</td></tr>
                <tr><th>Date of Death</th><td>{dod}</td></tr>
                <tr><th>Time of Death</th><td>{tod}</td></tr>
                <tr><th>Method</th><td>{method}</td></tr>
                <tr><th>Purpose</th><td>{purpose}</td></tr>
                <tr><th>Comment</th><td>{comment}</td></tr>
            </table>

            <p><i>Generated: {timestamp}</i></p>
        </body>
        </html>
        """

        return html

    def export_html(self, file_path, html_content):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True


class StimuliExportService:
    def export_stimuli_to_csv(self, file_path, tree, headings):
        try:
            # 1) Header: internal column names (Keys)
            header = list(headings.keys())

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=",")

                writer.writerow(header)

                # 2) Treeview-Daten schreiben
                for item in tree.get_children():
                    row = list(tree.item(item, "values"))
                    cleaned = StimuliFormatter.clean_row_for_csv(row)
                    writer.writerow(cleaned)

            return True

        except Exception as e:
            print("CSV-Export Fehler:", e)
            return False

    def load_stimuli_from_csv(self, file_path):
        try:
            rows = []

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=",")

                # Skip first line = Header
                header = next(reader, None)

                for row in reader:
                    rows.append(row)

            return rows

        except Exception as e:
            print("CSV-Ladefehler:", e)
            return None
