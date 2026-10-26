import os

class StimuliFormatter:
    """
    Central utility class for all stimuli formats:
    - Booleans for treeview
    - Booleans for CSV
    - Extract file names
    - Values from CSV back into treeview format
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
        Extracts filenames from paths
        """
        if isinstance(v, str) and ("/" in v or "\\" in v):
            return os.path.basename(v)
        return v

    @staticmethod
    def clean_for_tree(v):
        """
        Combines all treeview rules:
        - False → ""
        - Paths → Filenames
        """
        v = StimuliFormatter.bool_to_tree(v)
        v = StimuliFormatter.filename_only(v)
        return v

    @staticmethod
    def clean_for_csv(v):
        """
        Combines all CSV rules:
        - False → ""
        - Paths → Filenames
        """
        v = StimuliFormatter.bool_to_csv(v)
        v = StimuliFormatter.filename_only(v)
        return v

    @staticmethod
    def clean_row_for_tree(row):
        """
        Applies clean_for_tree to a complete row.
        """
        return [StimuliFormatter.clean_for_tree(v) for v in row]

    @staticmethod
    def clean_row_for_csv(row):
        """
        Applies clean_for_csv to a complete row.
        """
        return [StimuliFormatter.clean_for_csv(v) for v in row]
