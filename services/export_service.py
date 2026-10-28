import csv
import os
import datetime
import json
from pathlib import Path
from services.stimuli_formatter import StimuliFormatter
from services.validators import (
    validate_pyrat_id,
    validate_date,
    validate_time,
    validate_dropdown,
    ValidationError
)


class SessionExportService:
    """
    GUI-independent service for session data export
    """

    def update_json_to_recent_session(self, pyrat_id: str, sess_num: str, experiment: str, session: str):
        """
        Updates metadata in json file containing information about the last
        recording session. This allows to transmit current session information
        into the recording GUI, to be used for file naming and metadata.

        :param pyrat_id: Mouse (Pyrat-ID) to be recorded from
        :param sess_num: Current session number of this mouse
        :param experiment: Name of current experiment
        :param session: Name of current session
        """

        try:
            # Validation
            pyrat_id = validate_pyrat_id(pyrat_id)
            experiment = validate_dropdown(experiment, "Experiment")
            session = validate_dropdown(session, "Session Type")

        except ValidationError as e:
            return False, None, str(e)

        # Merging experiment and session name for metadata
        exp_sess = experiment + "_" + session

        if Path().cwd().name == "fUSI_db_app":
            os.chdir(Path().cwd().parent)

        try:
            with open("iEECR_fUSI_Stim/last_config.json", "r") as f:
                config = json.load(f)

            if "experiment_metadata" in config:
                meta = config["experiment_metadata"]
                if "experiment_name" in meta:
                    meta["experiment_name"] = exp_sess
                if "mouse_id" in meta:
                    meta['mouse_id'] = pyrat_id
                if "imaging_day" in meta:
                    meta["imaging_day"] = sess_num

            with open("iEECR_fUSI_Stim/last_config.json", "w") as f:
                json.dump(config, f, indent=2)

        except FileNotFoundError:
            config = {
                'experiment_metadata': {
                    'experiment_name': exp_sess,
                    'mouse_id': pyrat_id,
                    'imaging_day': sess_num,
                }
            }
            with open("iEECR_fUSI_Stim/last_config.json", "w") as f:
                json.dump(config, f, indent=2)

        return True, exp_sess, None


    def export_treeview_to_csv(self, file_path: str, tree: str, mouse_filter: str, exp_filter: str, headings: dict):
        """
        Exports content of treeview in display_sessions_tab into a CSV-file.

        :param file_path: target path
        :param tree: ttk.Treeview
        :param mouse_filter: current filter for mouse ID
        :param exp_filter: current filter for experiment
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
    GUI-independent service for export of sacrifice/kill information into a local HTML file
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
    """
    GUI-independent service for export or retrieval of trial stimulation sequence into/from a local csv file
    """

    def export_stimuli_to_csv(self, file_path, tree, headings):
        try:
            # 1) Header: internal column names (Keys)
            header = list(headings.keys())

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=",")

                writer.writerow(header)

                # 2) Write treeview data
                for item in tree.get_children():
                    row = list(tree.item(item, "values"))
                    cleaned = StimuliFormatter.clean_row_for_csv(row)
                    writer.writerow(cleaned)

            return True

        except Exception as e:
            print("CSV export error:", e)
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
            print("CSV loading error:", e)
            return None
