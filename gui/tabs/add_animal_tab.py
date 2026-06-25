import customtkinter as ctk
import params
from gui.base_tab import BaseTab
from gui.dialogs import ExportPopup


class AddAnimalTab(BaseTab):
    def __init__(self, master, mouse_service, rspace_service, today_and_before):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.rspace_service = rspace_service
        self.today_and_before = today_and_before
        self._build_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        # Pyrat ID
        ctk.CTkLabel(self, text="Pyrat ID:", anchor="e", width=100).grid(row=0, column=0)
        self.pyrat_entry = ctk.CTkEntry(self, fg_color="lightyellow", placeholder_text="AAA-xxxx")
        self.pyrat_entry.grid(row=0, column=1, padx=(10, 40))

        # Day of Birth
        ctk.CTkLabel(self, text="Day of Birth:", anchor="e", width=100).grid(row=1, column=0)
        self.dob_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.dob_entry.grid(row=1, column=1, padx=(10, 40), pady=2)

        # Sex
        ctk.CTkLabel(self, text="Sex:", anchor="e", width=100).grid(row=2, column=0)
        self.sex_combo = ctk.CTkComboBox(self, values=params.mouse_sex)
        self.sex_combo.grid(row=2, column=1, padx=(10, 40))

        # Line
        ctk.CTkLabel(self, text="Line/Genotype:", anchor="e", width=100).grid(row=3, column=0)
        self.line_combo = ctk.CTkComboBox(self, values=params.mouse_line)
        self.line_combo.grid(row=3, column=1, padx=(10, 40), pady=2)

        # Day of Surgery
        ctk.CTkLabel(self, text="Day of Surgery:", anchor="e", width=100).grid(row=0, column=2)
        self.dos_combo = ctk.CTkComboBox(self, values=self.today_and_before)
        self.dos_combo.grid(row=0, column=3, padx=(10, 40))

        # Time of Surgery
        ctk.CTkLabel(self, text="Time of Surgery:", anchor="e", width=100).grid(row=1, column=2)
        self.tos_entry = ctk.CTkEntry(self, placeholder_text="hh:mm")
        self.tos_entry.grid(row=1, column=3, padx=(10, 40), pady=2)

        # Surgeon
        ctk.CTkLabel(self, text="Surgeon:", anchor="e", width=100).grid(row=2, column=2)
        self.surgeon_combo = ctk.CTkComboBox(self, values=params.mouse_surgeon)
        self.surgeon_combo.grid(row=2, column=3, padx=(10, 40))

        # License
        ctk.CTkLabel(self, text="License:", anchor="e", width=100).grid(row=3, column=2)
        self.license_combo = ctk.CTkComboBox(self, values=params.mouse_license)
        self.license_combo.grid(row=3, column=3, padx=(10, 40))

        # Info text box
        self.info_text = ctk.CTkTextbox(
            self,
            height=50,
            width=140,
            border_width=4,
            border_color="darkred",
            text_color="darkred"
        )
        self.info_text.insert("0.0", "Check cage card to match information!")
        self.info_text.grid(row=0, column=4, rowspan=2, padx=20)

        # Submit button
        self.submit_button = ctk.CTkButton(
            self,
            text="Submit mouse",
            command=self._on_submit
        )
        self.submit_button.grid(row=3, column=4, padx=20)

        # RSpace checkbox
        self.rspace_var = ctk.StringVar(value="off")
        self.rspace_check = ctk.CTkCheckBox(
            self,
            text="also push to RSpace",
            variable=self.rspace_var,
            onvalue="on",
            offvalue="off",
            state="disabled"
        )
        self.rspace_check.grid(row=2, column=4, padx=20)

        self.update_rspace_state()

        # Info label
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            height=40,
            fg_color="lightgrey",
            corner_radius=5,
            anchor="w",
            text_color="black"
        )
        self.info_label.grid(row=4, column=0, columnspan=5, sticky="we", padx=10, pady=(10, 0))

    # ---------------------------------------------------------
    # RSpace login state
    # ---------------------------------------------------------
    def update_rspace_state(self):
        if self.rspace_service.logged_in:
            self.rspace_check.configure(state="normal")
        else:
            self.rspace_check.configure(state="disabled")

    # ---------------------------------------------------------
    # Submit new mouse
    # ---------------------------------------------------------
    def _on_submit(self):
        pyrat_id = self.pyrat_entry.get()
        dob = self.dob_entry.get()
        sex = self.sex_combo.get()
        line = self.line_combo.get()
        dos = self.dos_combo.get()
        tos = self.tos_entry.get()
        surgeon = self.surgeon_combo.get()
        license_ = self.license_combo.get()

        ok, _, err = self.mouse_service.register_mouse(
            pyrat_id, dob, sex, line, dos, tos, surgeon, license_
        )

        if not ok:
            self.show_error(err)
            return

        self.show_success(f"{pyrat_id} stored in database.")

        # Automatic RSpace upload
        if self.rspace_var.get() == "on":
            self._upload_mouse_to_rspace(pyrat_id)

        self._clear_fields()

    # ---------------------------------------------------------
    # Handle popup and RSpace upload
    # ---------------------------------------------------------
    def _upload_mouse_to_rspace(self, pyrat_id):
        ok, mouse_data, err = self.mouse_service.get_mouse_export_data(pyrat_id)

        if not ok:
            self.show_error(err)
            return

        def handle_comment(comment):
            ok, response, err = self.rspace_service.export_mouse_to_rspace(mouse_data, comment)

            if not ok:
                self.show_error(f"RSpace upload failed: {err}")
                return

            self.info_label.configure(text=f"Uploaded to RSpace: {response}")

        ExportPopup(
            master=self,
            data_dict=mouse_data,
            title=f"Export Mouse {pyrat_id}",
            on_submit=handle_comment
        )

    # ---------------------------------------------------------
    # Clear fields
    # ---------------------------------------------------------
    def _clear_fields(self):
        self.pyrat_entry.delete(0, "end")
        self.dob_entry.delete(0, "end")
        self.dob_entry.configure(placeholder_text="YYYY-MM-DD")
        self.tos_entry.delete(0, "end")
        self.tos_entry.configure(placeholder_text="hh:mm")
