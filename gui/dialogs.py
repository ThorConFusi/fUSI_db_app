import customtkinter as ctk
import params


class SessionDetailsPopup(ctk.CTkToplevel):
    def __init__(self, master, mouse_data: dict, session_data: dict):
        super().__init__(master)
        self.title(f"Session Details – {session_data.get('Pyrat-ID')}")
        self.minsize(700, 400)
        self.geometry("900x600")
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

        # Left column: Mouse data
        mouse_fields = [
            "Pyrat-ID", "Sex", "Line", "D.o.Birth",
            "D.o.Surgery", "T.o.Surgery",
            "D.o.Death", "T.o.Death",
            "Kill_method", "Kill_purpose", "Kill_comment"
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

        # Right column: Session data
        session_fields = {
            "Pyrat-ID": session_data.get("Pyrat-ID"),
            "D.o.Recording": session_data.get("D.o.Recording"),
            "T.o.Recording": session_data.get("T.o.Recording"),
            "Session_number": session_data.get("Session_number"),
            "Experiment": session_data.get("Experiment"),
            "Session": session_data.get("Session"),
        }

        btn_row = row - 1
        row = 1
        for key, value in session_fields.items():
            ctk.CTkLabel(container, text=f"{key}:").grid(
                row=row, column=1, sticky="w", padx=10, pady=3
            )
            ctk.CTkLabel(container, text=str(value)).grid(
                row=row, column=1, sticky="e", padx=40, pady=3
            )
            row += 1

        # Session comment
        footer = ctk.CTkFrame(self)
        footer.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(footer, text="Session Comment:", font=("Arial", 14, "bold")).pack(anchor="w")

        comment_box = ctk.CTkTextbox(footer, width=680, height=120)
        comment_box.insert("0.0", str(session_data.get("Session_comment", "")))
        comment_box.configure(state="disabled")
        comment_box.pack(fill="x", pady=5)

        # Close button
        ctk.CTkButton(container, text="Close", command=self.destroy).grid(
            row=btn_row, column=1, pady=(0, 20)
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
