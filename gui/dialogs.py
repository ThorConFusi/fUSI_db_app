import customtkinter as ctk


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
    def __init__(self, master, data_dict: dict, title: str, on_submit):
        super().__init__(master)
        self.title(title)
        self.minsize(600, 600)
        self.geometry("600x600")
        self.grab_set()

        self.on_submit = on_submit

        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(
            container,
            text="Record Information",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Display dictionary content (read‑only)
        row = 1
        for key, value in data_dict.items():
            ctk.CTkLabel(container, text=f"{key}:").grid(
                row=row, column=0, sticky="w", padx=10, pady=3
            )
            ctk.CTkLabel(container, text=str(value)).grid(
                row=row, column=0, sticky="e", padx=200, pady=3
            )
            row += 1

        # Comment section
        footer = ctk.CTkFrame(self)
        footer.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            footer,
            text="Additional Information (optional):",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.comment_box = ctk.CTkTextbox(footer, width=680, height=120)
        self.comment_box.pack(fill="x", pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy).pack(
            side="right", padx=10
        )
        ctk.CTkButton(button_frame, text="Submit", command=self._submit).pack(
            side="right"
        )

    def _submit(self):
        comment = self.comment_box.get("0.0", "end").strip()
        if comment == "":
            comment = None
        self.on_submit(comment)
        self.destroy()
