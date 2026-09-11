import os

class StimuliFormatter:
    """
    Zentrale Utility-Klasse für alle Stimuli-Formatierungen:
    - Booleans für Treeview
    - Booleans für CSV
    - Filenamen extrahieren
    - Werte aus CSV zurück in Treeview-Format
    """

    @staticmethod
    def bool_to_tree(v):
        """
        True → "True"
        False → ""
        """
        if isinstance(v, bool):
            return "True" if v else ""
        if isinstance(v, str) and v.lower() == "false":
            return ""
        return v

    @staticmethod
    def bool_to_csv(v):
        """
        True → "True"
        False → ""
        """
        if isinstance(v, bool):
            return "True" if v else ""
        if isinstance(v, str) and v.lower() == "false":
            return ""
        return v

    @staticmethod
    def filename_only(v):
        """
        Extrahiert Filenamen aus Pfaden.
        """
        if isinstance(v, str) and ("/" in v or "\\" in v):
            return os.path.basename(v)
        return v

    @staticmethod
    def clean_for_tree(v):
        """
        Kombiniert alle Treeview-Regeln:
        - False → ""
        - Pfade → Filenamen
        """
        v = StimuliFormatter.bool_to_tree(v)
        v = StimuliFormatter.filename_only(v)
        return v

    @staticmethod
    def clean_for_csv(v):
        """
        Kombiniert alle CSV-Regeln:
        - False → ""
        - Pfade → Filenamen
        """
        v = StimuliFormatter.bool_to_csv(v)
        v = StimuliFormatter.filename_only(v)
        return v

    @staticmethod
    def clean_row_for_tree(row):
        """
        Wendet clean_for_tree auf eine komplette Zeile an.
        """
        return [StimuliFormatter.clean_for_tree(v) for v in row]

    @staticmethod
    def clean_row_for_csv(row):
        """
        Wendet clean_for_csv auf eine komplette Zeile an.
        """
        return [StimuliFormatter.clean_for_csv(v) for v in row]
