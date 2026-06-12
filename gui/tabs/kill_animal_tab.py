

import customtkinter as ctk
import params


class KillAnimalTab(ctk.CTkFrame):
    def __init__(self, master, mouse_service, rspace_service, today_and_before):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.rspace_service = rspace_service
        self.today_and_before = today_and_before
        self._build_ui()

    def _build_ui(self):
        # Pyrat ID
        ctk.CTkLabel(self, text="Pyrat ID:", anchor="e", width=100).grid(row=0, column=0)
        self.pyrat_option = ctk.CTkOptionMenu(
            self,
            fg_color="lightyellow",
            button_color="darkgrey",
            button_hover_color="grey",
            text_color="black",
            values=self.mouse_service.get_alive_mice_with_none()
        )
        self.pyrat_option.grid(row=0, column=1, padx=(10, 40))

        # Kill date
        ctk.CTkLabel(self, text="Day of Death:", anchor="e", width=100).grid(row=1, column=0)
        self.kill_date_combo = ctk.CTkComboBox(self, values=self.today_and_before)
        self.kill_date_combo.grid(row=1, column=1, padx=(10, 40), pady=2)

        # Kill time
        ctk.CTkLabel(self, text="Time of Death:", anchor="e", width=100).grid(row=1, column=2)
        self.kill_time_entry = ctk.CTkEntry(self, placeholder_text="hh:mm")
        self.kill_time_entry.grid(row=1, column=3, padx=(10, 40), pady=2)

        # Kill method
        ctk.CTkLabel(self, text="Method:", anchor="e", width=100).grid(row=2, column=0)
        self.method_combo = ctk.CTkComboBox(self, values=params.kill_method)
        self.method_combo.grid(row=2, column=1, padx=(10, 40))

        # Kill purpose
        ctk.CTkLabel(self, text="Purpose:", anchor="e", width=100).grid(row=2, column=2)
        self.purpose_combo = ctk.CTkComboBox(self, values=params.kill_purpose)
        self.purpose_combo.grid(row=2, column=3, padx=(10, 40))

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            height=50,
            width=140,
            fg_color="lightyellow",
            corner_radius=5,
            text="Mouse won't\nbe visible in\napp anymore",
            anchor="center"
        )
        self.status_label.grid(row=0, column=4, rowspan=2)

        # Submit button
        self.submit_button = ctk.CTkButton(
            self,
            text="Kill animal",
            command=self._on_submit
        )
        self.submit_button.grid(row=3, column=4, padx=20)

        # RSpace checkbox (disabled until login)
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

        # Comment
        ctk.CTkLabel(self, text="Comment:", anchor="e", width=100).grid(row=3, column=0)
        self.comment_entry = ctk.CTkEntry(
            self,
            width=440,
            placeholder_text="e. g. lost headmount or for histology"
        )
        self.comment_entry.grid(row=3, column=1, columnspan=3, padx=(10, 40), pady=2)

        self.update_rspace_state()

        # Info box (read-only)
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


    # Update login state
    def update_rspace_state(self):
        if self.rspace_service.logged_in:
            self.rspace_check.configure(state="normal")
        else:
            self.rspace_check.configure(state="disabled")


    # Update Pyrat-ID pulldown
    def refresh_pyrat_ids(self):
        alive_ids = self.mouse_service.get_alive_mice_with_none()
        self.pyrat_option.configure(values=alive_ids)

        # Optional: Auswahl zurücksetzen
        if alive_ids:
            self.pyrat_option.set(alive_ids[0])


    # Submit kill event
    def _on_submit(self):
        pyrat_id = self.pyrat_option.get()
        dod = self.kill_date_combo.get()
        tod = self.kill_time_entry.get()
        method = self.method_combo.get()
        purpose = self.purpose_combo.get()
        comment = self.comment_entry.get()

        ok, msg = self.mouse_service.kill_mouse(
            pyrat_id, dod, tod, method, purpose, comment
        )

        self.info_label.configure(text=msg)

        if ok:
            self._clear_fields()
            self.refresh_pyrat_ids()

        if not ok:
            self.info_label.configure(text=msg)
            self._show_error(msg)
            return

        # Success
        self.status_label.configure(text=f"{pyrat_id}\nmarked as dead.")


    # Error popup
    def _show_error(self, msg: str):
        err_window = ctk.CTkToplevel(self)
        err_window.title("Input error")
        err_window.geometry("300x150")

        label = ctk.CTkLabel(
            err_window,
            text=msg,
            font=ctk.CTkFont(size=16),
            text_color="red"
        )
        label.pack(pady=30)

        def close():
            err_window.destroy()

        btn = ctk.CTkButton(err_window, text="OK", font=ctk.CTkFont(size=16), command=close)
        btn.pack()

    def _clear_fields(self):
        self.kill_date_combo.set("")
        self.kill_time_entry.delete(0, "end")
        self.kill_time_entry.configure(self, placeholder_text="hh:mm")
        #self.method_combo.set("")
        #self.purpose_combo.set("")
        self.comment_entry.delete(0, "end")
        self.comment_entry.configure(placeholder_text = "e. g. lost headmount or for histology")