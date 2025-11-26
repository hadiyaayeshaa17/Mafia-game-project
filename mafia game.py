import tkinter as tk
from tkinter import messagebox
import random

# --- Dark Theme Constants ---
BG_MAIN = "#1a1a2e"
BG_FRAME = "#2c394b"
TEXT_LIGHT = "#e9edf0"
ACCENT_HEADER = "#f3e034"
ACCENT_MAFIA = "#c0392b"
ACCENT_DOCTOR = "#27ae60"
ACCENT_VOTE = "#d35400"
BTN_HOVER = "#5b6d7f"


class MafiaGame(tk.Tk):

    TOTAL_PLAYERS = 4
    REQUIRED_ROLES = {"Mafia": 1, "Doctor": 1, "Civilian": 2}

    def __init__(self):
        super().__init__()
        self.title("Mafia Wars — 4 Player Edition")
        self.geometry("650x750")
        self.configure(bg=BG_MAIN)

        self.players = {}
        self.status = {}
        self.living_players = []
        self.phase = "Setup"
        self.round_number = 1
        self.summary_log = []

        # Setup trackers
        self.setup_step = 0
        self.setup_player_data = []
        self.setup_role_counts = {"Mafia": 0, "Doctor": 0, "Civilian": 0}

        # Main layout frame
        self.main_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # Start with title screen (IMPORTANT FIX)
        self.show_title_screen()

    # Utility
    def create_button(self, parent, text, cmd, bg, fg):
        btn = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                        font=("Segoe UI", 14, "bold"), relief=tk.RAISED, bd=4,
                        activebackground=BTN_HOVER, activeforeground=TEXT_LIGHT,
                        highlightthickness=0)
        return btn

    def clear_ui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------------------- TITLE SCREEN ----------------------
    def show_title_screen(self):
        self.clear_ui()

        frame = tk.Frame(self.main_frame, bg=BG_FRAME, padx=50, pady=50)
        frame.pack(pady=100)

        tk.Label(frame, text="Mafia Wars — 4-Player Edition",
                 font=("Segoe UI", 28, "bold"),
                 bg=BG_FRAME, fg=ACCENT_HEADER).pack(pady=25)

        tk.Label(frame, text="A Mini Mafia Project",
                 font=("Segoe UI", 14),
                 bg=BG_FRAME, fg=TEXT_LIGHT).pack(pady=15)

        start_btn = tk.Button(
            frame, text="START GAME", font=("Segoe UI", 16, "bold"),
            bg=ACCENT_DOCTOR, fg="black", padx=20, pady=10,
            command=self.setup_ui
        )
        start_btn.pack(pady=35)

    # ---------------------- SETUP UI ----------------------
    def setup_ui(self):
        self.clear_ui()
        self.setup_step = 0
        self.setup_player_data = []
        self.setup_role_counts = {"Mafia": 0, "Doctor": 0, "Civilian": 0}
        self.next_setup_step()

    def next_setup_step(self):
        self.clear_ui()
        if self.setup_step >= self.TOTAL_PLAYERS:
            self.finalize_setup()
            return

        frame = tk.Frame(self.main_frame, bg=BG_FRAME, padx=40, pady=40, width=600, height=400)
        frame.pack(pady=40)

        tk.Label(frame, text=f"PLAYER {self.setup_step + 1} SETUP", font=("Segoe UI", 18, "bold"),
                 bg=BG_FRAME, fg=ACCENT_HEADER).pack(pady=14)

        tk.Label(frame, text="Enter Name:", bg=BG_FRAME, fg=TEXT_LIGHT).pack()
        self.name_entry = tk.Entry(frame, width=30, font=("Segoe UI", 12), bg=BG_MAIN, fg=TEXT_LIGHT)
        self.name_entry.pack(pady=8)

        tk.Label(frame, text="Select Role:", bg=BG_FRAME, fg=TEXT_LIGHT).pack(pady=4)

        role_options = []
        for r, limit in self.REQUIRED_ROLES.items():
            if self.setup_role_counts[r] < limit:
                role_options.append(r)

        self.role_var = tk.StringVar(self)
        self.role_var.set(role_options[0])

        tk.OptionMenu(frame, self.role_var, *role_options).pack(pady=8)

        self.create_button(self.main_frame,
                           text="Save Player & Continue",
                           cmd=self.process_setup_step,
                           bg=ACCENT_DOCTOR, fg=BG_MAIN).pack(pady=20)

    def process_setup_step(self):
        name = self.name_entry.get().strip()
        role = self.role_var.get()

        if not name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        if name in [p[0] for p in self.setup_player_data]:
            messagebox.showerror("Error", "Name must be unique.")
            return

        self.setup_player_data.append((name, role))
        self.setup_role_counts[role] += 1
        self.setup_step += 1
        self.next_setup_step()

    # ---------------------- AFTER SETUP ----------------------
    def finalize_setup(self):
        self.players = {name: role for name, role in self.setup_player_data}
        self.status = {name: 'alive' for name in self.players}
        self.living_players = list(self.players.keys())

        self.summary_log.append("Game Started with 4 players.")
        self.summary_log.append("--- Assigned Roles (Hidden until End) ---")
        for n, r in self.players.items():
            self.summary_log.append(f"{n} → {r}")

        self.phase = "Night"
        self.start_night_phase()

    # ---------------------- NIGHT PHASE ----------------------
    def start_night_phase(self):
        self.summary_log.append(f"Night {self.round_number} begins.")
        self.night_kill_target = None
        self.night_save_target = None
        self.pending_roles = ["Mafia", "Doctor"]
        self.night_action_ui()

    def night_action_ui(self):
        self.clear_ui()

        if not self.pending_roles:
            self.process_night_results()
            return

        role = self.pending_roles.pop(0)

        frame = tk.Frame(self.main_frame, bg=BG_FRAME, padx=20, pady=20)
        frame.pack(pady=40)

        tk.Label(frame, text=f"{role} — Select Target", font=("Segoe UI", 18, "bold"),
                 bg=BG_FRAME, fg=ACCENT_HEADER).pack(pady=10)

        self.target_var = tk.StringVar(self)
        self.target_var.set(self.living_players[0])

        tk.OptionMenu(frame, self.target_var, *self.living_players).pack(pady=10)

        self.create_button(
            self.main_frame, "Confirm Action",
            lambda r=role: self.record_night_action(r),
            ACCENT_MAFIA if role == "Mafia" else ACCENT_DOCTOR,
            TEXT_LIGHT
        ).pack(pady=20)

    def record_night_action(self, role):
        target = self.target_var.get()
        if role == "Mafia":
            self.night_kill_target = target
        if role == "Doctor":
            self.night_save_target = target
        self.night_action_ui()

    def process_night_results(self):
        kill = self.night_kill_target
        save = self.night_save_target

        if kill == save:
            self.summary_log.append(f"Doctor saved {kill}. No one died.")
            self.show_end_screen("No one died — The Doctor saved the target. Game Over.")
            return
        else:
            self.status[kill] = 'dead'
            self.living_players.remove(kill)
            self.summary_log.append(f"{kill} was killed during the night.")

        if self.check_win():
            return

        self.round_number += 1
        self.start_day_phase()

    # ---------------------- DAY PHASE ----------------------
    def start_day_phase(self):
        self.summary_log.append(f"Day {self.round_number} voting begins.")
        self.day_votes = {}
        self.voter_index = 0
        self.voters = list(self.living_players)
        self.day_vote_ui()

    def day_vote_ui(self):
        self.clear_ui()

        if self.voter_index >= len(self.voters):
            self.process_day_results()
            return

        voter = self.voters[self.voter_index]

        frame = tk.Frame(self.main_frame, bg=BG_FRAME, padx=20, pady=20)
        frame.pack(pady=40)

        tk.Label(frame, text=f"{voter} — Vote a Player", font=("Segoe UI", 18, "bold"),
                 bg=BG_FRAME, fg=ACCENT_VOTE).pack(pady=10)

        targets = [p for p in self.living_players if p != voter]

        self.vote_var = tk.StringVar(self)
        self.vote_var.set(targets[0])

        tk.OptionMenu(frame, self.vote_var, *targets).pack(pady=10)

        self.create_button(
            self.main_frame, "Cast Vote",
            self.record_day_vote,
            ACCENT_VOTE, BG_MAIN
        ).pack(pady=20)

    def record_day_vote(self):
        target = self.vote_var.get()
        self.day_votes[target] = self.day_votes.get(target, 0) + 1
        self.voter_index += 1
        self.day_vote_ui()

    def process_day_results(self):
        lynch = max(self.day_votes, key=self.day_votes.get)
        self.status[lynch] = 'dead'
        self.living_players.remove(lynch)

        self.summary_log.append(f"The town lynched {lynch}.")

        if self.check_win():
            return

        self.round_number += 1
        self.start_night_phase()

    # ---------------------- WIN CHECK ----------------------
    def check_win(self):
        living_roles = [self.players[p] for p in self.living_players]
        mafia_alive = living_roles.count("Mafia")
        town_alive = len(self.living_players) - mafia_alive

        if mafia_alive == 0:
            self.show_end_screen("Town Wins — Mafia eliminated!")
            return True
        if mafia_alive >= town_alive:
            self.show_end_screen("Mafia Wins — Outnumbered the town!")
            return True
        return False

    # ---------------------- END SCREEN ----------------------
    def show_end_screen(self, msg):
        self.clear_ui()

        frame = tk.Frame(self.main_frame, bg=BG_FRAME, padx=20, pady=20)
        frame.pack(pady=40, fill="x")

        tk.Label(frame, text="GAME SUMMARY", font=("Segoe UI", 20, "bold"),
                 bg=BG_FRAME, fg=ACCENT_HEADER).pack(pady=10)

        for line in self.summary_log:
            tk.Label(frame, text=line, bg=BG_FRAME, fg=TEXT_LIGHT, anchor="w").pack(fill="x")

        tk.Label(frame, text=msg, font=("Segoe UI", 16, "bold"),
                 bg=BG_FRAME, fg=ACCENT_HEADER).pack(pady=20)

        self.create_button(
            self.main_frame, "Restart Game",
            self.show_title_screen,
            ACCENT_DOCTOR, BG_MAIN
        ).pack(pady=30)


if __name__ == "__main__":
    MafiaGame().mainloop()
