import customtkinter as ctk
import params
from tkinter import filedialog, messagebox
from services.validators import (
    validate_bool,
    validate_file,
    validate_duration,
    ValidationError
)


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
    def __init__(self, master, initial_values, on_submit):
        super().__init__(master)
        self.title("Edit Stimuli Line")
        self.geometry("450x500")
        self.resizable(False, False)
        self.grab_set()

        self.initial = initial_values
        self.on_submit = on_submit

        self._build_ui()
        self._apply_pause_state()   # direkt anwenden

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Pause
        self.chk_pause = ctk.CTkCheckBox(self, text="Pause", command=self._apply_pause_state)
        self.chk_pause.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        self.chk_pause.select() if self.initial.get("pause") else self.chk_pause.deselect()

        # Visual Stim
        frame_visual = ctk.CTkFrame(self)
        frame_visual.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        frame_visual.columnconfigure(0, weight=1)

        self.ent_visual = ctk.CTkEntry(frame_visual, placeholder_text="Visual Stim (*.png)")
        self.ent_visual.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.ent_visual.insert(0, self.initial.get("visual_stim", ""))

        self.btn_visual = ctk.CTkButton(frame_visual, text="Browse", width=80,
                                        command=lambda: self._choose_file(self.ent_visual, "png"))
        self.btn_visual.grid(row=0, column=1)

        # Acoustic Stim
        frame_acoustic = ctk.CTkFrame(self)
        frame_acoustic.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        frame_acoustic.columnconfigure(0, weight=1)

        self.ent_acoustic = ctk.CTkEntry(frame_acoustic, placeholder_text="Acoustic Stim (*.wav)")
        self.ent_acoustic.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.ent_acoustic.insert(0, self.initial.get("acoustic_stim", ""))

        self.btn_acoustic = ctk.CTkButton(frame_acoustic, text="Browse", width=80,
                                          command=lambda: self._choose_file(self.ent_acoustic, "wav"))
        self.btn_acoustic.grid(row=0, column=1)

        # Whisker Stim
        self.chk_whisker = ctk.CTkCheckBox(self, text="Whisker Stim")
        self.chk_whisker.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.chk_whisker.select() if self.initial.get("whisker_stim") else self.chk_whisker.deselect()

        # Odour Stim
        self.chk_odour = ctk.CTkCheckBox(self, text="Odour Stim")
        self.chk_odour.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.chk_odour.select() if self.initial.get("odour_stim") else self.chk_odour.deselect()

        # Air Puff
        self.chk_air = ctk.CTkCheckBox(self, text="Air Puff")
        self.chk_air.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        self.chk_air.select() if self.initial.get("air_puff") else self.chk_air.deselect()

        # Duration Label
        self.lbl_duration = ctk.CTkLabel(self, text="Duration (ms)")
        self.lbl_duration.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")

        # Duration Entry
        self.ent_duration = ctk.CTkEntry(self)
        self.ent_duration.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="w")
        self.ent_duration.insert(0, self.initial.get("duration_ms", ""))

        # Fußzeile für Fehlermeldungen
        self.lbl_error = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_error.grid(row=7, column=0, padx=20, pady=(5, 10), sticky="w")

        # Save Button
        self.btn_save = ctk.CTkButton(self, text="Save", command=self._validate_and_submit)
        self.btn_save.grid(row=8, column=0, padx=20, pady=20)

    # ---------------------------------------------------------
    # File selection
    # ---------------------------------------------------------
    def _choose_file(self, entry_widget, ext):
        file_path = filedialog.askopenfilename(
            filetypes=[(f"{ext.upper()} files", f"*.{ext}")]
        )
        if file_path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

    # ---------------------------------------------------------
    # Pause logic
    # ---------------------------------------------------------
    def _apply_pause_state(self):
        pause = self.chk_pause.get() == 1

        # Wenn Pause aktiv → alle Stimuli-Felder deaktivieren
        state = "disabled" if pause else "normal"

        self.ent_visual.configure(state=state)
        self.btn_visual.configure(state=state)

        self.ent_acoustic.configure(state=state)
        self.btn_acoustic.configure(state=state)

        self.chk_whisker.configure(state=state)
        self.chk_odour.configure(state=state)
        self.chk_air.configure(state=state)

        # Duration bleibt immer aktiv

    # ---------------------------------------------------------
    # Validation + submit
    # ---------------------------------------------------------
    def _validate_and_submit(self):
        try:
            data = {
                "pause": validate_bool(self.chk_pause.get(), "pause"),
                "visual_stim": validate_file(self.ent_visual.get(), "visual_stim"),
                "acoustic_stim": validate_file(self.ent_acoustic.get(), "acoustic_stim"),
                "whisker_stim": validate_bool(self.chk_whisker.get(), "whisker_stim"),
                "odour_stim": validate_bool(self.chk_odour.get(), "odour_stim"),
                "air_puff": validate_bool(self.chk_air.get(), "air_puff"),
                "duration_ms": validate_duration(self.ent_duration.get())
            }

        except ValidationError as e:
            self.lbl_error.configure(text=str(e))
            return

        self.lbl_error.configure(text="")
        self.on_submit(data)
        self.destroy()


class StimuliTimelinePopup(ctk.CTkToplevel):
    def __init__(self, master, rows):
        super().__init__(master)
        self.title("Timeline Preview")
        self.grab_set()

        # --- Calculate duration ---
        self.rows = rows
        self.total_duration = sum(int(r["duration_ms"]) for r in rows)

        # --- Identify tracks ---
        self.used_tracks = self._get_used_tracks(rows)

        # --- Dynamic Scaling ---
        self.left_margin = 150
        self.right_margin = 50

        self.scale = max(0.2, (900 - self.left_margin - self.right_margin) / self.total_duration)

        # Dynamic window width
        width = int(self.left_margin + self.total_duration * self.scale + self.right_margin)
        height = 80 + len(self.used_tracks) * 20

        self.geometry(f"{width}x{height}")

        # Canvas
        self.canvas = ctk.CTkCanvas(self, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Draw
        self._draw_time_axis()
        self._draw_tracks()

    # ---------------------------------------------------------
    # Get used stimuli
    # ---------------------------------------------------------
    def _get_used_tracks(self, rows):
        used = set()
        for row in rows:
            if row["pause"]:
                used.add("pause")
            for stim in ["visual_stim", "acoustic_stim", "whisker_stim", "odour_stim", "air_puff"]:
                if row[stim] not in ("", False, None):
                    used.add(stim)
        return list(used)

    # ---------------------------------------------------------
    # Time axis w/ ticks at stimulus onset
    # ---------------------------------------------------------
    def _draw_time_axis(self):
        scale = self.scale
        left = self.left_margin

        self.canvas.create_line(
            left,
            30,
            left + self.total_duration * scale,
            30,
            width=2
        )

        start_times = []
        t = 0
        for row in self.rows:
            start_times.append(t)
            t += int(row["duration_ms"])

        for t in start_times:
            x = left + t * scale
            self.canvas.create_line(x, 25, x, 35, width=1)
            self.canvas.create_text(x, 15, text=f"{t} ms")

    # ---------------------------------------------------------
    # Draw tracks
    # ---------------------------------------------------------
    def _draw_tracks(self):
        colors = {
            "pause": "#aaaaaa",
            "visual_stim": "#3377c8",
            "acoustic_stim": "#55aa55",
            "whisker_stim": "#aa5533",
            "odour_stim": "#aa33aa",
            "air_puff": "#ffaa00"
        }

        scale = self.scale
        y = 60

        for track in self.used_tracks:
            # Track-Label
            self.canvas.create_text(10, y, anchor="w",
                                    text=track.replace("_", " ").capitalize())

            x = self.left_margin

            for row in self.rows:
                duration = int(row["duration_ms"])
                width_px = duration * scale

                active = False
                if track == "pause" and row["pause"]:
                    active = True
                elif track != "pause":
                    if row[track] not in ("", False, None):
                        active = True

                if active:
                    self.canvas.create_rectangle(
                        x, y - 10, x + width_px, y + 10,
                        fill=colors[track], outline=""
                    )

                x += width_px

            y += 20
