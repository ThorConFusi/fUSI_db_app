import customtkinter as ctk
from gui.base_tab import BaseTab
import params
from gui.dialogs import ExportPopup
from params import session_name


class AddSessionTab(BaseTab):
    def __init__(self, master, mouse_service, session_service, export_service, rspace_service, today_and_before):
        super().__init__(master)
        self.mouse_service = mouse_service
        self.session_service = session_service
        self.export_service = export_service
        self.rspace_service = rspace_service
        self.rspace_client = None
        self.today_and_before = today_and_before
        self._build_ui()

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        # Pyrat ID
        ctk.CTkLabel(self, text="Pyrat ID:", anchor="e", width=100).grid(row=0, column=0)

        ok, alive, err = self.mouse_service.get_alive_mice()
        if not ok or not alive:
            alive = ["none available"]

        self.pyrat_option = ctk.CTkOptionMenu(
            self,
            fg_color="lightyellow",
            button_color="darkgrey",
            button_hover_color="grey",
            text_color="black",
            values=alive,
            command=self._update_session_label
        )
        self.pyrat_option.grid(row=0, column=1, padx=(10, 40))

        # Session date
        ctk.CTkLabel(self, text="Session date:", anchor="e", width=100).grid(row=0, column=2)
        self.sess_date_combo = ctk.CTkComboBox(self, values=self.today_and_before)
        self.sess_date_combo.grid(row=0, column=3, padx=(10, 40), pady=2)

        # Session time
        ctk.CTkLabel(self, text="Session Time:", anchor="e", width=100).grid(row=1, column=2)
        self.sess_time_entry = ctk.CTkEntry(self, placeholder_text="hh:mm")
        self.sess_time_entry.grid(row=1, column=3, padx=(10, 40), pady=2)

        # Experiment
        ctk.CTkLabel(self, text="Experiment:", anchor="e", width=100).grid(row=1, column=0)
        self.exp_combo = ctk.CTkComboBox(self, values=params.experiment_name)
        self.exp_combo.grid(row=1, column=1, padx=(10, 40))

        # Session type
        ctk.CTkLabel(self, text="Session:", anchor="e", width=100).grid(row=2, column=0)
        self.session_combo = ctk.CTkComboBox(self, values=params.session_name)
        self.session_combo.grid(row=2, column=1, padx=(10, 40))

        # Start recording GUI
        self.rec_button = ctk.CTkButton(
            self,
            text="Start fUSI recording GUI",
            text_color="darkred",
            width=215,
            fg_color = "white",
            border_width = 4,
            border_color = "darkred",
            hover_color = "#dadada",
            command=self._start_session
        )
        self.rec_button.grid(row=2, column=2, columnspan=2)

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

        self.update_rspace_state()

    # ---------------------------------------------------------
    # RSpace login state
    # ---------------------------------------------------------
    def update_rspace_state(self):
        if self.rspace_service.logged_in:
            self.rspace_check.configure(state="normal")
            self.rspace_client = self.rspace_service.client
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

        ok, next_num, err = self.session_service.get_next_session_number_safe(pyrat_id)

        if not ok:
            self.show_error(err)
            return

        self.rec_label.configure(text=f"fUS recording\nsession no. {next_num}")

    # ---------------------------------------------------------
    # Start session (by opening stimulation GUI)
    # ---------------------------------------------------------
    def _start_session(self):
        pyrat_id = self.pyrat_option.get()
        experiment = self.exp_combo.get()
        session = self.session_combo.get()
        sess_num = self.session_service.get_next_session_number_safe(pyrat_id)
        sess_date = self.sess_date_combo.get()
        sess_time = self.sess_time_entry.get()

        if pyrat_id == "none available":
            self.rec_label.configure(text="No valid session data")
            return

        ok, exp_sess, err = self.session_service.update_json_to_recent_session(
            pyrat_id, sess_num, experiment, session
        )

        if not ok:
            self.show_error(err)
            return

        self.show_success(f"Ready for session {sess_num} {pyrat_id}.")

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

        ok, next_num, err = self.session_service.create_session(
            pyrat_id, exp, sess_date, sess_time, sess, comment
        )

        if not ok:
            self.show_error(err)
            return

        self.rec_label.configure(text=f"fUS recording\nsession no. {next_num}")
        self.show_success(f"Session for {pyrat_id} saved successfully.")

        # Optional RSpace upload
        if self.rspace_var.get() == "on":
            self._upload_session_to_rspace(pyrat_id, next_num, sess_date)

        self._clear_fields()
        self.refresh_pyrat_ids()

    # ---------------------------------------------------------
    # RSpace upload
    # ---------------------------------------------------------
    def _upload_session_to_rspace(self, pyrat_id, session_number, sess_date):
        # 1. Get session data
        ok, session_data, err = self.session_service.get_session_by_keys(
            pyrat_id,
            sess_date,
            session_number
        )

        if not ok:
            self.show_error(err)
            return

        # 2. Callback for Popup
        def handle_comment(data_dict, comment, folder_id, folder_type):
            ok, response, err = self.rspace_service.export_to_rspace(
                data_dict,
                comment,
                folder_id,
                folder_type
            )

            if not ok:
                self.show_error(f"RSpace upload failed: {err}")
                return

            self.info_label.configure(text=f"Uploaded to RSpace: {response}")

        # 3. Open Popup
        ExportPopup(
            master=self,
            data_dict=session_data,
            title=f"Export Session {session_number} for {pyrat_id}",
            on_submit=handle_comment,
            rspace_client=self.rspace_client
        )

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
    # Refresh Pyrat IDs
    # ---------------------------------------------------------
    def refresh_pyrat_ids(self):
        ok, alive, err = self.mouse_service.get_alive_mice()
        if not ok or not alive:
            alive = ["none available"]

        self.pyrat_option.configure(values=alive)
        self.pyrat_option.set(alive[0])
