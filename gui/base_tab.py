import customtkinter as ctk
from gui.dialogs import ErrorPopup, SuccessPopup


class BaseTab(ctk.CTkFrame):
    """Common basis for all Tabs."""

    def show_error(self, msg: str):
        ErrorPopup(self, msg)


    def show_success(self, msg: str):
        SuccessPopup(self, msg)