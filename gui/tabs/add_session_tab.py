import customtkinter as ctk
from gui.base_tab import BaseTab
import params


class AddSessionTab(BaseTab):
    def __init__(self, master, mouse_service, session_service, rspace_service, today_and_before):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.session_service = session_service
        self.rspace_service = rspace_service
        self.today_and_before = today_and_before
        self._build_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        # Pyrat ID
        ctk.CTkLabel(self, text="Pyrat ID:", anchor="e", width=100).grid(row=0, column=0)
        self.pyrat_option = ctk.CTkOptionMenu(
            self,
            fg_color="lightyellow",
            button_color="darkgrey",
            button_hover_color="grey",
            text_color="black",
            values=self.mouse_service.get_alive_mice_with_none(),
            command=self._update_session_label
        )
        self.pyrat_option.grid(row=0, column=1, padx=(10, 40))

        # Session date
        ctk.CTkLabel(self, text="Session date:", anchor="e", width=100).grid(row=1, column=0)
        self.sess_date_combo = ctk.CTkComboBox(self, values=self.today_and_before)
        self.sess_date_combo.grid(row=1, column=1, padx=(10, 40), pady=2)

        # Session time
        ctk.CTkLabel(self, text="Session Time:", anchor="e", width=100).grid(row=1, column=2)
        self.sess_time_entry = ctk.CTkEntry(self, placeholder_text="hh:mm")
        self.sess_time_entry.grid(row=1, column=3, padx=(10, 40), pady=2)

        # Experiment
        ctk.CTkLabel(self, text="Experiment:", anchor="e", width=100).grid(row=2, column=0)
        self.exp_combo = ctk.CTkComboBox(self, values=params.experiment_name)
        self.exp_combo.grid(row=2, column=1, padx=(10, 40))

        # Session type
        ctk.CTkLabel(self, text="Session:", anchor="e", width=100).grid(row=2, column=2)
        self.session_combo = ctk.CTkComboBox(self, values=params.session_name)
        self.session_combo.grid(row=2, column=3, padx=(10, 40))

        # Recording session number
        self.rec_label = ctk.CTkLabel(
            self,
            height=50,
            width=140,
            fg_color="lightyellow",
            corner_radius=5,
            text="fUS recording\nsession no.",
            anchor="center"
        )
        self.rec_label.grid(row=0, column=4, rowspan=2)

        # Submit button
        self.submit_button = ctk.CTkButton(
            self,
            text="Submit fUSI session",
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

        # Comment
        ctk.CTkLabel(self, text="Comment:", anchor="e", width=100).grid(row=3, column=0)
        self.comment_entry = ctk.CTkEntry(
            self,
            width=440,
            placeholder_text="e. g. quality of cranial window"
        )
        self.comment_entry.grid(row=3, column=1, columnspan=3, padx=(10, 40), pady=2)

        # Info label (BaseTab uses this)
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

        self.update_rspace_state()

    # ---------------------------------------------------------
    # RSpace login state
    # ---------------------------------------------------------
    def update_rspace_state(self):
        if self.rspace_service.logged_in:
            self.rspace_check.configure(state="normal")
        else:
            self.rspace_check.configure(state="disabled")

    # ---------------------------------------------------------
    # Update session number
    # ---------------------------------------------------------
    def _update_session_label(self, _choice=None):
        pyrat_id = self.pyrat_option.get()

        if pyrat_id == "none available":
            self.rec_label.configure(text="No valid mouse")
            return

        ok, result = self.session_service.get_next_session_number_safe(pyrat_id)
        if not ok:
            self.show_error(result)
            return

        next_num = result
        self.rec_label.configure(text=f"fUS recording\nsession no. {next_num}")

    # ---------------------------------------------------------
    # Submit session
    # ---------------------------------------------------------
    def _on_submit(self):
        pyrat_id = self.pyrat_option.get()
        exp = self.exp_combo.get()
        sess_date = self.sess_date_combo.get()
        sess_time = self.sess_time_entry.get()
        sess = self.session_combo.get()
        comment = self.comment_entry.get()

        ok, result = self.session_service.create_session(
            pyrat_id, exp, sess_date, sess_time, sess, comment
        )

        if not ok:
            self.show_error(result)
            return

        next_num = result
        self.rec_label.configure(text=f"fUS recording\nsession no. {next_num}")

        self.show_success(f"Session for {pyrat_id} saved successfully.")

        self._clear_fields()
        self.refresh_pyrat_ids()

    # ---------------------------------------------------------
    # Clear fields
    # ---------------------------------------------------------
    def _clear_fields(self):
        self.sess_date_combo.set("")
        self.sess_time_entry.delete(0, "end")
        self.sess_time_entry.configure(placeholder_text="hh:mm")

        self.comment_entry.delete(0, "end")
        self.comment_entry.configure(placeholder_text="e. g. quality of cranial window")

    # ---------------------------------------------------------
    # Refresh Pyrat IDs (called by MainWindow polling)
    # ---------------------------------------------------------
    def refresh_pyrat_ids(self):
        alive_ids = self.mouse_service.get_alive_mice_with_none()
        self.pyrat_option.configure(values=alive_ids)

        if alive_ids:
            self.pyrat_option.set(alive_ids[0])

    # ---------------------------------------------------------
    # Error handler (now via BaseTab)
    # ---------------------------------------------------------
    def _show_error(self, msg: str):
        self.show_error(msg)
