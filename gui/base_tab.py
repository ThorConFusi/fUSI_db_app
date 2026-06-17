import customtkinter as ctk


class BaseTab(ctk.CTkFrame):
    """Common basis for all Tabs with inline status messages."""

    def set_info(self, msg: str, color="black"):
        """Update the info label if the tab has one."""
        if hasattr(self, "info_label"):
            self.info_label.configure(text=msg, text_color=color)

    def show_error(self, msg: str):
        self.set_info(msg, color="red")

    def show_success(self, msg: str):
        self.set_info(msg, color="green")
