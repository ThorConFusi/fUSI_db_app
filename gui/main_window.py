import customtkinter as ctk
from datetime import date, timedelta
import params

from gui.tabs.welcome_tab import WelcomeTab
from gui.tabs.add_animal_tab import AddAnimalTab
from gui.tabs.add_session_tab import AddSessionTab
from gui.tabs.kill_animal_tab import KillAnimalTab
from gui.tabs.display_sessions_tab import DisplaySessionsTab


class MainWindow(ctk.CTk):
    def __init__(self, mouse_service, session_service, rspace_service, db):
        super().__init__()

        self.mouse_service = mouse_service
        self.session_service = session_service
        self.rspace_service = rspace_service
        self.db = db

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        self.title("fUSI Experiment Information")
        self.geometry("800x280")

        title_label = ctk.CTkLabel(
            self,
            text=("Input relevant experiment information, then submit to the "
                  "fUSI session database (and optional RSpace)"),
            font=ctk.CTkFont(size=16),
            text_color="grey"
        )
        title_label.pack(pady=(20, 5))

        self.tabview = ctk.CTkTabview(self, anchor="nw")
        self.tabview.pack(padx=5, pady=5, fill="both", expand=True)

        # Prepare date list
        today = date.today()
        self.today_and_before = [str(today)] + [
            str(today - timedelta(days=i)) for i in range(1, 7)
        ]

        self._build_tabs()

    def _build_tabs(self):
        # Welcome / RSpace
        welcome_frame = self.tabview.add(params.tab_title[3])
        self.welcome_tab = WelcomeTab(
            master=welcome_frame,
            rspace_service=self.rspace_service,
            db=self.db,
            main_window=self
        )
        self.welcome_tab.pack(fill="both", expand=True)

        # Add Animal
        add_animal_frame = self.tabview.add(params.tab_title[0])
        self.add_animal_tab = AddAnimalTab(
            master=add_animal_frame,
            mouse_service=self.mouse_service,
            rspace_service=self.rspace_service,
            today_and_before=self.today_and_before
        )
        self.add_animal_tab.pack(fill="both", expand=True)

        # Add Session
        add_session_frame = self.tabview.add(params.tab_title[1])
        self.add_session_tab = AddSessionTab(
            master=add_session_frame,
            mouse_service=self.mouse_service,
            session_service=self.session_service,
            rspace_service=self.rspace_service,
            today_and_before=self.today_and_before
        )
        self.add_session_tab.pack(fill="both", expand=True)

        # Kill Animal
        kill_frame = self.tabview.add(params.tab_title[2])
        self.kill_tab = KillAnimalTab(
            master=kill_frame,
            mouse_service=self.mouse_service,
            rspace_service=self.rspace_service,
            today_and_before=self.today_and_before
        )

        self.kill_tab.pack(fill="both", expand=True)

        # Display Sessions
        display_frame = self.tabview.add(params.tab_title[4])
        self.display_tab = DisplaySessionsTab(
            master=display_frame,
            mouse_service=self.mouse_service,
            session_service=self.session_service
        )
        self.display_tab.pack(fill="both", expand=True)
