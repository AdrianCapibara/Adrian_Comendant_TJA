import customtkinter as ctk
import cv2
from PIL import Image
import threading
import pygame
import re
import main
import time
from onboarding import OnboardingManager

pygame.mixer.init()


class SafeDriveApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SafeDrive AI")
        self.geometry("450x850")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")

        self.accent_color = "#ff5a4f"

        # USERS
        self.users_db = {
            "driver@gmail.com": {"user": "Adrian", "pass": "Password1", "scores": []}
        }

        # SCORE SYSTEM
        self.drive_scores = []
        self.drive_sessions = []
        self.current_drive_score = 100
        self.drive_active = False

        self.dark_mode = False

        self.cap = None
        self.is_running = False
        self.alarm_playing = False

        self.fatigue_start_time = None
        self.fatigue_event_triggered = False

        self.drive_start_time = None

        self.main_container = ctk.CTkFrame(self, fg_color="#0e0e10")
        self.main_container.pack(fill="both", expand=True)

        self.onboarding = OnboardingManager(
            self.main_container,
            self.draw_login_form,
            self.draw_register_form
        )

        self.onboarding.show_welcome()

    # ---------------- ALARM ----------------
    def play_alarm(self):
        if not self.alarm_playing:
            try:
                pygame.mixer.music.load("alarm.mp3")
                pygame.mixer.music.play(-1)
                self.alarm_playing = True
            except:
                pass

    def stop_alarm(self):
        if self.alarm_playing:
            pygame.mixer.music.stop()
            self.alarm_playing = False

    # ---------------- VALIDARE ----------------
    def valid_email(self, email):
        return re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email)

    def valid_password(self, password):
        return (
            len(password) >= 8 and
            re.search(r"[A-Z]", password) and
            re.search(r"[0-9]", password)
        )

    # ---------------- INPUT ----------------
    def create_input(self, parent, label, placeholder, is_pass=False):
        ctk.CTkLabel(
            parent,
            text=label,
            text_color="white",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(8, 0))

        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=45,
            show="*" if is_pass else "",
            fg_color="#1a1a1d",
            text_color="white",
            border_color=self.accent_color,
            corner_radius=12
        )
        e.pack(fill="x", pady=5)
        return e

    # ---------------- LOGIN ----------------
    def draw_login_form(self, target_frame):
        for w in target_frame.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(target_frame, fg_color="#151518", corner_radius=20)
        card.pack(expand=True, fill="both", padx=30, pady=40)

        ctk.CTkLabel(card, text="Login",
                     font=("Arial", 26, "bold"),
                     text_color="white").pack(pady=20)

        self.e_login = self.create_input(card, "Email", "driver@gmail.com")
        self.p_login = self.create_input(card, "Password", "••••", True)

        self.err = ctk.CTkLabel(card, text="", text_color=self.accent_color)
        self.err.pack()

        ctk.CTkButton(card, text="LOGIN",
                      height=50,
                      fg_color=self.accent_color,
                      command=self.handle_login).pack(pady=20, fill="x")

        ctk.CTkButton(card, text="Create account",
                      fg_color="transparent",
                      command=self.go_to_register).pack()

    # ---------------- REGISTER ----------------
    def draw_register_form(self, target_frame):
        for w in target_frame.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(target_frame, fg_color="#151518", corner_radius=20)
        card.pack(expand=True, fill="both", padx=30, pady=40)

        ctk.CTkLabel(card, text="Register",
                     font=("Arial", 26, "bold"),
                     text_color="white").pack(pady=20)

        self.r_u = self.create_input(card, "Name", "Adrian")
        self.r_e = self.create_input(card, "Email", "new@gmail.com")
        self.r_p = self.create_input(card, "Password", "••••••••", True)

        self.reg_err = ctk.CTkLabel(card, text="", text_color=self.accent_color)
        self.reg_err.pack()

        ctk.CTkButton(card, text="REGISTER",
                      height=50,
                      fg_color=self.accent_color,
                      command=self.handle_register).pack(pady=20, fill="x")

        ctk.CTkButton(card, text="Back",
                      fg_color="transparent",
                      command=self.go_to_login).pack()

    # ---------------- DASHBOARD (MODERN UI) ----------------
    def draw_dashboard(self):
        self.onboarding.clear_container()
        self.main_container.configure(fg_color="#0b0b0d")

        frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#151518",
            corner_radius=25,
            border_width=2,
            border_color=self.accent_color
        )
        frame.pack(expand=True, fill="both", padx=20, pady=40)

        ctk.CTkLabel(
            frame,
            text="SAFE DRIVE AI",
            font=("Arial", 26, "bold"),
            text_color="white"
        ).pack(pady=20)

        ctk.CTkLabel(
            frame,
            text="Driving Safety System",
            text_color="gray"
        ).pack(pady=10)

        ctk.CTkButton(
            frame,
            text="START DRIVE",
            height=90,
            fg_color=self.accent_color,
            command=self.start_driving_view
        ).pack(pady=20, fill="x", padx=20)

        ctk.CTkButton(
            frame,
            text="SCORE HISTORY",
            height=60,
            fg_color="#2b2b2f",
            command=self.show_scores
        ).pack(pady=10, fill="x", padx=20)

        # logout jos dreapta
        ctk.CTkButton(
            self.main_container,
            text="Logout",
            fg_color="transparent",
            text_color="white",
            border_width=2,
            border_color=self.accent_color,
            command=self.go_to_login
        ).place(relx=0.98, rely=0.98, anchor="se")

    # ---------------- DRIVE ----------------
    def start_driving_view(self):
        self.onboarding.clear_container()
        self.main_container.configure(fg_color="black")

        self.drive_active = True
        self.current_drive_score = 100

        self.fatigue_start_time = None
        self.fatigue_event_triggered = False

        self.drive_start_time = time.strftime("%m-%d %H:%M")

        self.top_bar = ctk.CTkFrame(self.main_container, fg_color="black", height=180)
        self.top_bar.pack(fill="x")

        cam_frame = ctk.CTkFrame(self.main_container, fg_color="black")
        cam_frame.pack(fill="both", expand=True)

        self.video_label = ctk.CTkLabel(cam_frame, text="", fg_color="black")
        self.video_label.pack(fill="both", expand=True)

        self.bottom_bar = ctk.CTkFrame(self.main_container, fg_color="black", height=180)
        self.bottom_bar.pack(fill="x")

        ctk.CTkButton(self.bottom_bar,
                      text="STOP",
                      fg_color=self.accent_color,
                      command=self.stop_driving).pack(pady=10)

        self.dark_btn = ctk.CTkButton(
            self.bottom_bar,
            text="DarkMode OFF",
            fg_color="#2b2b2f",
            command=self.toggle_dark_mode
        )
        self.dark_btn.pack(pady=10)

        self.is_running = True
        self.cap = cv2.VideoCapture(0)

        threading.Thread(target=self.video_loop, daemon=True).start()

    # ---------------- DARK MODE ----------------
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.top_bar.configure(fg_color="#f1f3f6")
            self.bottom_bar.configure(fg_color="#f1f3f6")
            self.dark_btn.configure(text="DarkMode ON", fg_color=self.accent_color)
        else:
            self.top_bar.configure(fg_color="black")
            self.bottom_bar.configure(fg_color="black")
            self.dark_btn.configure(text="DarkMode OFF", fg_color="#2b2b2f")

    # ---------------- VIDEO ----------------
    def video_loop(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame, is_fatigue, durata = main.proceseaza_ai(frame)

                if is_fatigue:
                    if self.fatigue_start_time is None:
                        self.fatigue_start_time = time.time()
                        self.fatigue_event_triggered = False

                    if time.time() - self.fatigue_start_time >= 5:
                        if not self.fatigue_event_triggered:
                            self.current_drive_score -= 10
                            self.fatigue_event_triggered = True
                            self.play_alarm()
                else:
                    self.fatigue_start_time = None
                    self.fatigue_event_triggered = False
                    self.stop_alarm()

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)

                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 500))
                self.video_label.configure(image=ctk_img)

    # ---------------- SCORE UI (MODERN + DATE) ----------------
    def show_scores(self):
        self.onboarding.clear_container()
        self.main_container.configure(fg_color="#0b0b0d")

        frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#151518",
            corner_radius=25,
            border_width=2,
            border_color=self.accent_color
        )
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="DRIVING PERFORMANCE",
            font=("Arial", 22, "bold"),
            text_color=self.accent_color
        ).pack(pady=20)

        if not self.drive_scores:
            ctk.CTkLabel(frame, text="No trips yet", text_color="gray").pack(pady=20)
        else:
            for i, s in enumerate(self.drive_scores[::-1]):
                session = self.drive_sessions[::-1][i]

                color = "#00ff88" if s >= 80 else "#ffcc00" if s >= 50 else "#ff5a4f"

                card = ctk.CTkFrame(frame, fg_color="#1a1a1d", corner_radius=15)
                card.pack(fill="x", padx=15, pady=8)

                ctk.CTkLabel(
                    card,
                    text=f"{session['start']} → {session['end']}",
                    text_color="white",
                    font=("Arial", 14, "bold")
                ).pack(anchor="w", padx=10)

                ctk.CTkLabel(
                    card,
                    text=f"{s}/100",
                    text_color=color,
                    font=("Arial", 18, "bold")
                ).pack(anchor="w", padx=10)

        ctk.CTkButton(
            self.main_container,
            text="BACK",
            fg_color=self.accent_color,
            command=self.draw_dashboard
        ).pack(pady=10)

    # ---------------- STOP ----------------
    def stop_driving(self):
        self.is_running = False
        self.drive_active = False

        end_time = time.strftime("%m-%d %H:%M")

        self.drive_scores.append(self.current_drive_score)
        self.drive_sessions.append({
            "start": self.drive_start_time,
            "end": end_time
        })

        self.stop_alarm()
        self.draw_dashboard()

    # ---------------- AUTH ----------------
    def handle_login(self):
        e, p = self.e_login.get(), self.p_login.get()

        if not self.valid_email(e):
            self.err.configure(text="Email must be @gmail.com")
            return

        if e in self.users_db and self.users_db[e]["pass"] == p:
            self.draw_dashboard()
        else:
            self.err.configure(text="Wrong credentials")

    def handle_register(self):
        u, e, p = self.r_u.get(), self.r_e.get(), self.r_p.get()

        if not self.valid_email(e):
            self.reg_err.configure(text="Use @gmail.com")
            return

        if not self.valid_password(p):
            self.reg_err.configure(text="Min 8 chars, 1 capital, 1 number")
            return

        self.users_db[e] = {"user": u, "pass": p, "scores": []}
        self.go_to_login()

    def go_to_register(self):
        self.onboarding.clear_container()
        self.draw_register_form(self.onboarding.container)

    def go_to_login(self):
        self.onboarding.go_to_login()


if __name__ == "__main__":
    app = SafeDriveApp()
    app.mainloop()