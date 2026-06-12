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
        pyrat_id = self.pyrat_entry.get()
        dob = self.dob_entry.get()
        sex = self.sex_combo.get()
        line = self.line_combo.get()
        dos = self.dos_combo.get()
        tos = self.tos_entry.get()
        surgeon = self.surgeon_combo.get()
        license_ = self.license_combo.get()

        ok, msg = self.mouse_service.register_mouse(
            pyrat_id, dob, sex, line, dos, tos, surgeon, license_
        )

        # Update Info-Box
        self.info_label.configure(text=msg)

        if not ok:
            self._show_error(msg)
            return

        # Success → empty fields
        self._clear_fields()


    def _show_error(self, msg: str):
        err_window = ctk.CTkToplevel(self)
        err_window.title("Input error")
        err_window.geometry("300x150")

        # Always top level
        err_window.lift()
        err_window.attributes("-topmost", True)
        err_window.after(10, lambda: err_window.attributes("-topmost", False))

        # Set focus
        err_window.focus_force()

        # Make modal (blocks main window)
        err_window.grab_set()

        label = ctk.CTkLabel(
            err_window,
            text=msg,
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        label.pack(pady=30)

        btn = ctk.CTkButton(
            err_window,
            text="OK",
            font=ctk.CTkFont(size=16),
            command=err_window.destroy
        )
        btn.pack()

    def _clear_fields(self):
        self.pyrat_entry.delete(0, "end")
        self.dob_entry.delete(0, "end")
        self.dob_entry.configure(self, placeholder_text="YYYY-MM-DD")
        #self.sex_combo.set("")
        #self.line_combo.set("")
        #self.dos_combo.set("")
        self.tos_entry.delete(0, "end")
        self.tos_entry.configure(self, placeholder_text="hh:mm")
        #self.surgeon_combo.set("")
        #self.license_combo.set("")
