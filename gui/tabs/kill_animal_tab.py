import customtkinter as ctk
from gui.base_tab import BaseTab
from gui.dialogs import ExportPopup
import params


class KillAnimalTab(BaseTab):
    def __init__(self, master, mouse_service, rspace_service, today_and_before):
        super().__init__(master)
        self.mouse_service = mouse_service
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

        ok, mice, err = self.mouse_service.get_alive_mice()
        if not ok or not mice:
            mice = ["none available"]

        self.pyrat_option = ctk.CTkOptionMenu(
            self,
            values=mice,
            fg_color="lightyellow",
            button_color="darkgrey",
            button_hover_color="grey",
            text_color="black"
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
            placeholder_text="e. g. lost headmount or for histology"
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
    # Submit kill
    # ---------------------------------------------------------
    def _on_submit(self):
        pyrat_id = self.pyrat_option.get()
        dod = self.kill_date_combo.get()
        tod = self.kill_time_entry.get()
        method = self.method_combo.get()
        purpose = self.purpose_combo.get()
        comment = self.comment_entry.get()

        ok, _, err = self.mouse_service.kill_mouse(
            pyrat_id, dod, tod, method, purpose, comment
        )

        if not ok:
            self.show_error(err)
            return

        self.show_success(f"{pyrat_id} updated (killed).")

        # Automatic RSpace upload
        if self.rspace_var.get() == "on":
            self._upload_sacrifice_to_rspace(pyrat_id)

        self._clear_fields()
        self.refresh_pyrat_ids()

    # ---------------------------------------------------------
    # Handle popup and RSpace upload
    # ---------------------------------------------------------
    def _upload_sacrifice_to_rspace(self, pyrat_id):
        # 1. Get mouse data
        ok, mouse_data, err = self.mouse_service.get_mouse_export_data(pyrat_id)

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
            data_dict=mouse_data,
            title=f"Export Sacrifice Info for {pyrat_id}",
            on_submit=handle_comment,
            rspace_client=self.rspace_client
        )

    # ---------------------------------------------------------
    # Clear fields
    # ---------------------------------------------------------
    def _clear_fields(self):
        self.kill_time_entry.delete(0, "end")
        self.kill_time_entry.configure(placeholder_text="hh:mm")
        self.comment_entry.delete(0, "end")

    # ---------------------------------------------------------
    # Refresh Pyrat IDs
    # ---------------------------------------------------------
    def refresh_pyrat_ids(self):
        ok, mice, err = self.mouse_service.get_alive_mice()
        if not ok or not mice:
            mice = ["none available"]

        self.pyrat_option.configure(values=mice)
        self.pyrat_option.set(mice[0])
