import customtkinter as ctk


class ErrorPopup(ctk.CTkToplevel):
    def __init__(self, master, message: str):
        super().__init__(master)

        self.title("Input error")
        self.geometry("320x160")

        # Fenster immer im Vordergrund
        self.lift()
        self.attributes("-topmost", True)
        self.after(10, lambda: self.attributes("-topmost", False))

        # Fokus setzen
        self.focus_force()

        # Modal machen
        self.grab_set()

        label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=16),
            text_color="red",
            wraplength=280,
            justify="center"
        )
        label.pack(pady=25)

        btn = ctk.CTkButton(
            self,
            text="OK",
            font=ctk.CTkFont(size=16),
            command=self.destroy
        )
        btn.pack(pady=5)


class SuccessPopup(ctk.CTkToplevel):
    def __init__(self, master, message: str):
        super().__init__(master)

        self.title("Success")
        self.geometry("320x160")

        # Fenster immer im Vordergrund
        self.lift()
        self.attributes("-topmost", True)
        self.after(10, lambda: self.attributes("-topmost", False))

        # Fokus setzen
        self.focus_force()

        # Modal machen
        self.grab_set()

        label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=16),
            text_color="green",
            wraplength=280,
            justify="center"
        )
        label.pack(pady=25)

        btn = ctk.CTkButton(
            self,
            text="OK",
            font=ctk.CTkFont(size=16),
            command=self.destroy
        )
        btn.pack(pady=5)
