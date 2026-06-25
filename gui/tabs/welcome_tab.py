import customtkinter as ctk
from PIL import Image


class WelcomeTab(ctk.CTkFrame):
    def __init__(self, master, rspace_service, db, main_window):
        super().__init__(master)
        self.rspace_service = rspace_service
        self.db = db
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        # Title
        ctk.CTkLabel(
            self,
            text="RSpace Login",
            font=ctk.CTkFont(size=16)
        ).grid(row=0, column=1)

        # Surgeon dropdown
        ctk.CTkLabel(self, text="Surgeon:", anchor="e", width=100).grid(row=1, column=0)

        ok, surgeons, err = self.rspace_service.get_reg_surgeons()
        if not ok or not surgeons:
            surgeons = ["none available"]

        self.login_option = ctk.CTkOptionMenu(
            self,
            values=surgeons
        )
        self.login_option.grid(row=1, column=1, padx=10)

        # Password entry
        ctk.CTkLabel(self, text="Password:", anchor="e", width=100).grid(row=2, column=0)
        self.pw_entry = ctk.CTkEntry(self, show="*")
        self.pw_entry.grid(row=2, column=1, padx=10, pady=3)

        # Login button
        self.login_button = ctk.CTkButton(
            self,
            text="Login",
            command=self._on_login
        )
        self.login_button.grid(row=3, column=1)

        # Status label
        self.rspace_label = ctk.CTkLabel(
            self,
            text="Not connected to RSpace",
            fg_color="lightyellow",
            corner_radius=5,
            width=300,
            height=90,
            anchor="center"
        )
        self.rspace_label.grid(row=1, column=2, rowspan=3, columnspan=2)

        # fUSI logo
        self.logo_img = ctk.CTkImage(
            light_image=Image.open("iFUSI_Logo.png"),
            dark_image=Image.open("iFUSI_Logo.png"),
            size=(240, 120)
        )

        self.logo_label = ctk.CTkLabel(
            self,
            text="",
            image=self.logo_img,
        )

        self.logo_label.grid(row=1, column=5, rowspan=3, columnspan=2)

    # Login handler
    def _on_login(self):
        surgeon = self.login_option.get()
        pw = self.pw_entry.get()

        ok, _, err = self.rspace_service.check_login(surgeon, pw)

        if not ok:
            self.rspace_label.configure(
                text=f"Login failed:\n{err}",
                fg_color="lightyellow"
            )
            return

        # Success
        self.rspace_label.configure(
            text=f"Password correct!\n{surgeon} connected.",
            fg_color="lightgreen"
        )

        # Activate checkboxes in all upload tabs
        self.main_window.add_animal_tab.update_rspace_state()
        self.main_window.add_session_tab.update_rspace_state()
        self.main_window.kill_tab.update_rspace_state()
