import customtkinter as ctk
import params


class AddAnimalTab(ctk.CTkFrame):
    def __init__(self, master, mouse_service, rspace_service, today_and_before):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.rspace_service = rspace_service
        self.today_and_before = today_and_before
        self._build_ui()


    def _build_ui(self):
        ctk.CTkLabel(self, text="Pyrat ID:", anchor="e", width=100).grid(row=0, column=0)
        self.pyrat_entry = ctk.CTkEntry(self, fg_color="lightyellow", placeholder_text="AAA-xxxx")
        self.pyrat_entry.grid(row=0, column=1, padx=(10, 40))

        ctk.CTkLabel(self, text="Day of Birth:", anchor="e", width=100).grid(row=1, column=0)
        self.dob_entry = ctk.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.dob_entry.grid(row=1, column=1, padx=(10, 40), pady=2)

        ctk.CTkLabel(self, text="Sex:", anchor="e", width=100).grid(row=2, column=0)
        self.sex_combo = ctk.CTkComboBox(self, values=params.mouse_sex)
        self.sex_combo.grid(row=2, column=1, padx=(10, 40))

        ctk.CTkLabel(self, text="Line/Genotype:", anchor="e", width=100).grid(row=3, column=0)
        self.line_combo = ctk.CTkComboBox(self, values=params.mouse_line)
        self.line_combo.grid(row=3, column=1, padx=(10, 40), pady=2)

        ctk.CTkLabel(self, text="Day of Surgery:", anchor="e", width=100).grid(row=0, column=2)
        self.dos_combo = ctk.CTkComboBox(self, values=self.today_and_before)
        self.dos_combo.grid(row=0, column=3, padx=(10, 40))

        ctk.CTkLabel(self, text="Time of Surgery:", anchor="e", width=100).grid(row=1, column=2)
        self.tos_entry = ctk.CTkEntry(self, placeholder_text="hh:mm")
        self.tos_entry.grid(row=1, column=3, padx=(10, 40), pady=2)

        ctk.CTkLabel(self, text="Surgeon:", anchor="e", width=100).grid(row=2, column=2)
        self.surgeon_combo = ctk.CTkComboBox(self, values=params.mouse_surgeon)
        self.surgeon_combo.grid(row=2, column=3, padx=(10, 40))

        ctk.CTkLabel(self, text="License:", anchor="e", width=100).grid(row=3, column=2)
        self.license_combo = ctk.CTkComboBox(self, values=params.mouse_license)
        self.license_combo.grid(row=3, column=3, padx=(10, 40))

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

        self.submit_button = ctk.CTkButton(
            self,
            text="Submit mouse",
            command=self._on_submit
        )
        self.submit_button.grid(row=3, column=4, padx=20)

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


    def update_rspace_state(self):
        if self.rspace_service.logged_in:
            self.rspace_check.configure(state="normal")
        else:
            self.rspace_check.configure(state="disabled")


    def _normalize(self, value):
        if value is None:
            return None
        value = value.strip()
        return value if value != "" else None

    def _on_submit(self):
        pyrat_id = self._normalize(self.pyrat_entry.get())
        dob = self._normalize(self.dob_entry.get())
        sex = self._normalize(self.sex_combo.get())
        line = self._normalize(self.line_combo.get())
        dos = self._normalize(self.dos_combo.get())
        tos = self._normalize(self.tos_entry.get())
        surgeon = self._normalize(self.surgeon_combo.get())
        license_ = self._normalize(self.license_combo.get())

        ok, msg = self.mouse_service.register_mouse(
            pyrat_id, dob, sex, line, dos, tos, surgeon, license_
        )

        if not ok:
            self._show_error(msg)
            return

        self.pyrat_entry.delete(0, "end")
        self.info_text.delete("0.0", "end")
        self.info_text.insert("0.0", f"{pyrat_id} stored in database.")

        # RSpace Export (optional)
        if self.rspace_service.logged_in and self.rspace_var.get() == "on":
            ok, msg = self.mouse_service.export_mouse(
                pyrat_id=pyrat_id,
                comment="Created at registration",
                rspace_service=self.rspace_service
            )

            if not ok:
                self._show_error(f"RSpace export failed:\n{msg}")
                return

            self.info_text.insert("end", f"\nExported to RSpace as #{pyrat_id.replace('-', '')}")


    def _show_error(self, msg: str):
        err_window = ctk.CTkToplevel(self)
        err_window.title("Database conflict")
        err_window.geometry("300x150")

        label = ctk.CTkLabel(err_window, text=msg,
                             font=ctk.CTkFont(size=16),
                             text_color="red")
        label.pack(pady=30)

        def close():
            err_window.destroy()

        btn = ctk.CTkButton(err_window, text="OK", font=ctk.CTkFont(size=16), command=close)
        btn.pack()
