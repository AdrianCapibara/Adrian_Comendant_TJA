import customtkinter as ctk

class OnboardingManager:
    def __init__(
        self,
        container,
        show_login_callback,
        show_register_callback,
        toggle_language_callback=None   # ✅ acum NU mai e obligatoriu
    ):
        self.container = container
        self.show_login_callback = show_login_callback
        self.show_register_callback = show_register_callback
        self.toggle_language_callback = toggle_language_callback

        self.accent_color = "#ff5a4f"

    # ---------------- WELCOME ----------------
    def show_welcome(self):
        self.clear_container()
        self.container.configure(fg_color="#0b0b0d")

        ctk.CTkLabel(
            self.container,
            text="SafeDrive AI",
            font=("Arial", 40, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        self.container.after(2000, self.show_features_screen)

    # ---------------- FEATURES SCREEN ----------------
    def show_features_screen(self):
        self.clear_container()
        self.container.configure(fg_color="#0b0b0d")

        header = ctk.CTkFrame(
            self.container,
            fg_color=self.accent_color,
            height=160,
            corner_radius=0
        )
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="SafeDrive AI",
            font=("Arial", 26, "bold"),
            text_color="white"
        ).pack(pady=55)

        features_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        features_frame.pack(pady=25, padx=20, fill="both", expand=True)

        features = [
            ("AI Detection", "Detectăm oboseala în timp real."),
            ("5s Alert System", "Alarmă dacă ochii rămân închiși."),
            ("Road Safety", "Reducem accidentele la volan.")
        ]

        for title, desc in features:
            card = ctk.CTkFrame(
                features_frame,
                fg_color="#151518",
                corner_radius=15,
                border_width=1,
                border_color=self.accent_color,
                height=90
            )
            card.pack(fill="x", pady=10)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 15, "bold"),
                text_color=self.accent_color
            ).pack(pady=(10, 0), padx=15, anchor="w")

            ctk.CTkLabel(
                card,
                text=desc,
                font=("Arial", 12),
                text_color="white"
            ).pack(pady=(2, 10), padx=15, anchor="w")

        # CONTINUE BUTTON
        ctk.CTkButton(
            self.container,
            text="CONTINUE",
            fg_color=self.accent_color,
            hover_color="#e14b40",
            height=50,
            command=self.go_to_login
        ).pack(side="bottom", fill="x", padx=25, pady=35)

        # LANGUAGE BUTTON (SAFE)
        if self.toggle_language_callback is not None:
            ctk.CTkButton(
                self.container,
                text="RO / EN",
                fg_color="#1a1a1d",
                text_color="white",
                command=self.toggle_language_callback
            ).place(relx=0.86, rely=0.05)

    # ---------------- LOGIN ----------------
    def go_to_login(self):
        self.clear_container()
        self.container.configure(fg_color="#0b0b0d")

        panel = ctk.CTkFrame(
            self.container,
            fg_color="#151518",
            corner_radius=20
        )
        panel.pack(expand=True, fill="both", padx=30, pady=40)

        self.show_login_callback(panel)

    # ---------------- REGISTER ----------------
    def go_to_register(self):
        self.clear_container()
        self.container.configure(fg_color="#0b0b0d")

        panel = ctk.CTkFrame(
            self.container,
            fg_color="#151518",
            corner_radius=20
        )
        panel.pack(expand=True, fill="both", padx=30, pady=40)

        self.show_register_callback(panel)

    # ---------------- CLEAR ----------------
    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()