import customtkinter as ctk
import params
from tkinter import filedialog, messagebox


class SessionDetailsPopup(ctk.CTkToplevel):
    def __init__(self, master, mouse_data: dict, session_data: dict):
        super().__init__(master)
        self.title(f"Session Details – {session_data.get('Pyrat-ID')}")
        self.minsize(700, 500)
        self.geometry("900x750")
        self.grab_set()

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Headlines
        ctk.CTkLabel(container, text="Mouse Information", font=("Arial", 16, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10)
        )
        ctk.CTkLabel(container, text="Session Information", font=("Arial", 16, "bold")).grid(
            row=0, column=1, sticky="w", pady=(0, 10)
        )
        ctk.CTkLabel(container, text="Sacrifice Information", font=("Arial", 16, "bold")).grid(
            row=8, column=1, sticky="w", pady=(0, 10)
        )

        # Left column: Mouse data
        mouse_fields = [
            "Pyrat-ID", "Sex", "Line", "D.o.Birth", "License",
            "D.o.Surgery", "Surgeon" #, "T.o.Surgery",
            #"D.o.Death", "T.o.Death",
            #"Kill_method", "Kill_purpose", "Kill_comment"
        ]

        row = 1
        for key in mouse_fields:
            ctk.CTkLabel(container, text=f"{key}:").grid(
                row=row, column=0, sticky="w", padx=10, pady=3
            )
            ctk.CTkLabel(container, text=str(mouse_data.get(key, "—"))).grid(
                row=row, column=0, sticky="e", padx=40, pady=3
            )
            row += 1

        if mouse_data.get("Mouse_in_RSpace") == 0:
            in_rspace = "Mouse not uploaded to RSpace yet!"
            color = "red"
        else:
            in_rspace = "Mouse already uploaded to RSpace."
            color = "green"

        ctk.CTkLabel(container, text=in_rspace, text_color=color).grid(
            row=row, column=0, sticky="w", padx=10, pady=3
        )

        # Right column: Session data
        session_fields = {
            #"Pyrat-ID": session_data.get("Pyrat-ID"),
            "D.o.Recording": session_data.get("D.o.Recording"),
            "T.o.Recording": session_data.get("T.o.Recording"),
            "Session_number": session_data.get("Session_number"),
            "Experiment": session_data.get("Experiment"),
            "Session": session_data.get("Session"),
        }

        row = 1
        for key, value in session_fields.items():
            ctk.CTkLabel(container, text=f"{key}:").grid(
                row=row, column=1, sticky="w", padx=10, pady=3
            )
            ctk.CTkLabel(container, text=str(value)).grid(
                row=row, column=1, sticky="e", padx=40, pady=3
            )
            row += 1

        if session_data.get("Session_in_RSpace") == 0:
            in_rspace = "Session not uploaded to RSpace yet!"
            color = "red"
        else:
            in_rspace = "Session already uploaded to RSpace."
            color = "green"

        ctk.CTkLabel(container, text=in_rspace, text_color=color).grid(
            row=row, column=1, sticky="w", padx=10, pady=3
        )

        # Right column: Sacrifice data
        sacrifice_fields = [
            "D.o.Death", "Kill_method", "Kill_purpose"#, "Kill_comment"
        ]

        row = row + 3

        if mouse_data.get("D.o.Death") == mouse_data.get("T.o.Death"):
            ctk.CTkLabel(container, text="Mouse not sacrificed yet.").grid(
                row=row, column=1, sticky="w", padx=10, pady=3
            )
        else:
            for key in sacrifice_fields:
                ctk.CTkLabel(container, text=f"{key}:").grid(
                    row=row, column=1, sticky="w", padx=10, pady=3
                )
                ctk.CTkLabel(container, text=str(mouse_data.get(key, "—"))).grid(
                    row=row, column=1, sticky="e", padx=40, pady=3
                )
                row += 1

            if mouse_data.get("Sacrifice_in_RSpace") == 0:
                in_rspace = "Sacrifice not uploaded to RSpace yet!"
                color = "red"
            else:
                in_rspace = "Sacrifice already uploaded to RSpace."
                color = "green"

            ctk.CTkLabel(container, text=in_rspace, text_color=color).grid(
                row=row, column=1, sticky="w", padx=10, pady=3
            )

        # Session comment
        footer_session = ctk.CTkFrame(self)
        footer_session.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(footer_session, text="Session Comment:", font=("Arial", 14, "bold")).pack(anchor="w")

        comment_box_session = ctk.CTkTextbox(footer_session, width=680, height=80)
        comment_box_session.insert("0.0", str(session_data.get("Session_comment", "")))
        comment_box_session.configure(state="disabled")
        comment_box_session.pack(fill="x", pady=5)

        # Sacrifice comment
        footer_sacrifice = ctk.CTkFrame(self)
        footer_sacrifice.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(footer_sacrifice, text="Sacrifice Comment:", font=("Arial", 14, "bold")).pack(anchor="w")

        comment_box_sacrifice = ctk.CTkTextbox(footer_sacrifice, width=680, height=40)
        comment_box_sacrifice.insert("0.0", str(mouse_data.get("Kill_comment", "")))
        comment_box_sacrifice.configure(state="disabled")
        comment_box_sacrifice.pack(fill="x", pady=5)

        # Close button
        ctk.CTkButton(container, text="Close Information Window", command=self.destroy).grid(
            row=11, column=0, pady=(0, 20)
        )

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)


class ExportPopup(ctk.CTkToplevel):
    def __init__(self, master, data_dict: dict, title: str, on_submit, rspace_client):
        super().__init__(master)
        self.title(title)
        self.geometry("750x600")
        self.minsize(750, 600)
        self.grab_set()

        self.on_submit = on_submit
        self.rspace_client = rspace_client
        self.data_dict = data_dict

        # ---------------------------------------------------------
        # AUTOMATIC DATASET RECOGNITION
        # ---------------------------------------------------------
        self.is_mouse = "D.o.Surgery" in data_dict
        self.is_session = "Session_number" in data_dict

        if self.is_mouse:
            if data_dict.get("D.o.Death") is None:
                title_text = "Mouse Record – Add Mouse"
                keys_to_display = params.mouse_keys
                add_info = params.comment_surgery
            else:
                title_text = "Mouse Record – Sacrifice Mouse"
                keys_to_display = params.sacrifice_keys
                if data_dict["Kill_method"] == "perfusion":
                    add_info = params.comment_sacrifice
                else:
                    add_info = []
        elif self.is_session:
            title_text = "Session Record - Add Session"
            keys_to_display = params.session_keys
            add_info = []
        else:
            title_text = "Record Information"
            keys_to_display = list(data_dict.keys())
            add_info = []

        # Dummy-Werte (Upload geht immer in Api Inbox)
        self.selected_folder_id = 492620
        self.selected_folder_type = "api_inbox"

        # ---------------------------------------------------------
        # MAIN CONTAINER
        # ---------------------------------------------------------
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=(20, 10))

        ctk.CTkLabel(
            container,
            text=title_text,
            font=("Arial", 16, "bold")
        ).pack(fill="x", padx=20, pady=(0, 10))

        # ---------------------------------------------------------
        # DATA DISPLAY
        # ---------------------------------------------------------
        data_frame = ctk.CTkFrame(container)
        data_frame.pack(fill="x", padx=20, pady=(0, 10))

        for i, key in enumerate(keys_to_display):
            value = data_dict.get(key, "—")

            ctk.CTkLabel(data_frame, text=f"{key}:").grid(
                row=i, column=0, sticky="w", padx=(3, 20)
            )
            ctk.CTkLabel(data_frame, text=str(value)).grid(
                row=i, column=1, sticky="w", padx=20
            )

        # ---------------------------------------------------------
        # COMMENT SECTION
        # ---------------------------------------------------------
        footer = ctk.CTkFrame(self)
        footer.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            footer,
            text="Additional Information (optional):",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.comment_box = ctk.CTkTextbox(footer, width=560, height=120)
        self.comment_box.pack(fill="x", pady=5)
        self.comment_box.insert("0.0", add_info)

        # ---------------------------------------------------------
        # BUTTON FRAME
        # ---------------------------------------------------------
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            button_frame,
            text="Target Folder: Api Inbox",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy).pack(
            side="right", padx=10
        )
        ctk.CTkButton(button_frame, text="Submit", command=self._submit).pack(
            side="right"
        )

    # ---------------------------------------------------------
    # SUBMIT
    # ---------------------------------------------------------
    def _submit(self):
        comment = self.comment_box.get("0.0", "end").strip()
        if comment == "":
            comment = None

        # Callback (Tabs stay untouched)
        self.on_submit(
            self.data_dict,
            comment,
            self.selected_folder_id,
            self.selected_folder_type
        )

        self.destroy()


class StimuliEditPopup(ctk.CTkToplevel):
    def __init__(self, master, initial_values=None, on_submit=None):
        super().__init__(master)
        self.title("Edit Stimuli Line")
        self.geometry("450x500")
        self.grab_set()

        self.on_submit = on_submit
        self.initial = initial_values or {}

        # -------------------------
        # Widgets
        # -------------------------
        # Pause
        self.pause_var = ctk.BooleanVar(value=self.initial.get("pause", True))
        self.pause_cb = ctk.CTkCheckBox(self, text="Pause", variable=self.pause_var,
                                        command=self._update_state)
        self.pause_cb.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Visual Stim (PNG)
        ctk.CTkLabel(self, text="Visual Stim (.png):").grid(row=1, column=0, sticky="w", padx=10)
        self.visual_entry = ctk.CTkEntry(self, width=250)
        self.visual_entry.grid(row=2, column=0, padx=10, sticky="w")
        self.visual_entry.insert(0, self.initial.get("visual_stim", ""))

        self.visual_btn = ctk.CTkButton(self, text="Browse", command=self._browse_visual)
        self.visual_btn.grid(row=2, column=1, padx=10)

        # Acoustic Stim (.wav)
        ctk.CTkLabel(self, text="Acoustic Stim (.wav):").grid(row=3, column=0, sticky="w", padx=10)
        self.acoustic_entry = ctk.CTkEntry(self, width=250)
        self.acoustic_entry.grid(row=4, column=0, padx=10, sticky="w")
        self.acoustic_entry.insert(0, self.initial.get("acoustic_stim", ""))

        self.acoustic_btn = ctk.CTkButton(self, text="Browse", command=self._browse_acoustic)
        self.acoustic_btn.grid(row=4, column=1, padx=10)

        # Whisker Stim
        self.whisker_var = ctk.BooleanVar(value=self.initial.get("whisker_stim", False))
        self.whisker_cb = ctk.CTkCheckBox(self, text="Whisker Stim", variable=self.whisker_var)
        self.whisker_cb.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Odour Stim
        self.odour_var = ctk.BooleanVar(value=self.initial.get("odour_stim", False))
        self.odour_cb = ctk.CTkCheckBox(self, text="Odour Stim", variable=self.odour_var)
        self.odour_cb.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # Air Puff
        self.air_var = ctk.BooleanVar(value=self.initial.get("air_puff", False))
        self.air_cb = ctk.CTkCheckBox(self, text="Air Puff", variable=self.air_var)
        self.air_cb.grid(row=7, column=0, padx=10, pady=10, sticky="w")

        # Duration
        ctk.CTkLabel(self, text="Duration (ms):").grid(row=8, column=0, sticky="w", padx=10)
        self.duration_entry = ctk.CTkEntry(self, width=100)
        self.duration_entry.grid(row=9, column=0, padx=10, sticky="w")
        self.duration_entry.insert(0, self.initial.get("duration_ms", ""))

        # Submit
        submit_btn = ctk.CTkButton(self, text="Apply", command=self._submit)
        submit_btn.grid(row=10, column=0, columnspan=2, pady=20)

        self._update_state()

    # -------------------------
    # File Browsers
    # -------------------------
    def _browse_visual(self):
        path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if path:
            self.visual_entry.delete(0, "end")
            self.visual_entry.insert(0, path)

    def _browse_acoustic(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            self.acoustic_entry.delete(0, "end")
            self.acoustic_entry.insert(0, path)

    # -------------------------
    # Pause disables fields
    # -------------------------
    def _update_state(self):
        pause = self.pause_var.get()

        state = "disabled" if pause else "normal"

        # Disable all except duration
        for widget in [
            self.visual_entry, self.visual_btn,
            self.acoustic_entry, self.acoustic_btn,
            self.whisker_cb, self.odour_cb, self.air_cb
        ]:
            widget.configure(state=state)

    # -------------------------
    # Validation + Submit
    # -------------------------
    def _submit(self):
        pause = self.pause_var.get()
        duration = self.duration_entry.get().strip()

        # Duration must be integer
        if not duration.isdigit():
            messagebox.showerror("Error", "Duration must be an integer.")
            return

        duration = int(duration)

        # If pause=False → at least one stim must be set
        if not pause:
            stim_values = [
                self.visual_entry.get().strip(),
                self.acoustic_entry.get().strip(),
                self.whisker_var.get(),
                self.odour_var.get(),
                self.air_var.get()
            ]
            if not any(stim_values):
                messagebox.showerror("Error", "At least one stimulus must be set.")
                return

        result = {
            "pause": pause,
            "visual_stim": self.visual_entry.get().strip(),
            "acoustic_stim": self.acoustic_entry.get().strip(),
            "whisker_stim": self.whisker_var.get(),
            "odour_stim": self.odour_var.get(),
            "air_puff": self.air_var.get(),
            "duration_ms": duration
        }

        if self.on_submit:
            self.on_submit(result)

        self.destroy()
