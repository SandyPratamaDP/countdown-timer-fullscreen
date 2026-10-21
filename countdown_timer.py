import os
import sys
import tkinter as tk
import tkinter.font as tkfont

BG_IDLE = "black"
FG_IDLE = "white"
BG_DONE = "red"
FG_DONE = "white"
FG_PAUSED = "#ffd400"
FG_RESET = "#ff3b30"

BG_SETUP = "#0f1117"
BG_FIELD = "#1a1e2b"
BORDER = "#2a3142"
ACCENT = "#3b82f6"
ACCENT_HOVER = "#5b9bff"
MUTED = "#7b8499"
CHIP_HOVER = "#262c3d"


UI_FONT = "Arial"
MONO_FONT = "Courier New"

UI_FONT_CHOICES = ("Segoe UI", "Inter", "Ubuntu", "Noto Sans", "Helvetica", "Arial")
MONO_FONT_CHOICES = ("Consolas", "JetBrains Mono", "DejaVu Sans Mono", "Noto Sans Mono", "Courier New")


def pick_fonts():
    """Use the nicest installed font from each list; needs a Tk root to exist."""
    global UI_FONT, MONO_FONT
    installed = set(tkfont.families())
    UI_FONT = next((f for f in UI_FONT_CHOICES if f in installed), UI_FONT)
    MONO_FONT = next((f for f in MONO_FONT_CHOICES if f in installed), MONO_FONT)


def resource_path(name):
    """Locate a bundled file, both when run from source and from a PyInstaller exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


class CountdownApp:
    def __init__(self, root):
        self.root = root
        pick_fonts()
        self.root.title("Countdown Timer")
        try:
            self.app_icon = tk.PhotoImage(file=resource_path("icon.png"))
            self.root.iconphoto(True, self.app_icon)
        except tk.TclError:
            pass
        self.remaining_seconds = 0
        self.total_seconds = 0
        self.timer_job = None
        self.running = False
        self.finished = False
        self.user_paused = False
        self.reset_flash = False
        self.flash_job = None

        self.build_setup_screen()

    # ---------- setup screen ----------
    def build_setup_screen(self):
        self.clear_root()
        self.root.attributes("-fullscreen", False)
        self.root.configure(bg=BG_SETUP)
        self.root.geometry("460x400")
        self.root.eval("tk::PlaceWindow . center")

        frame = tk.Frame(self.root, bg=BG_SETUP)
        frame.pack(expand=True)

        tk.Label(
            frame, text="COUNTDOWN TIMER", fg=MUTED, bg=BG_SETUP,
            font=(UI_FONT, 11, "bold"),
        ).pack(pady=(0, 18))

        entry_frame = tk.Frame(frame, bg=BG_SETUP)
        entry_frame.pack()

        self.minutes_var = tk.StringVar(value="05")
        self.seconds_var = tk.StringVar(value="00")

        vcmd = (self.root.register(self._validate_digits), "%P")

        min_entry = self._make_entry(entry_frame, self.minutes_var, vcmd)
        min_entry.grid(row=0, column=0)
        tk.Label(
            entry_frame, text=":", fg=MUTED, bg=BG_SETUP, font=(UI_FONT, 40, "bold")
        ).grid(row=0, column=1, padx=12)
        sec_entry = self._make_entry(entry_frame, self.seconds_var, vcmd)
        sec_entry.grid(row=0, column=2)

        for col, text in ((0, "MIN"), (2, "SEC")):
            tk.Label(
                entry_frame, text=text, fg=MUTED, bg=BG_SETUP, font=(UI_FONT, 9, "bold")
            ).grid(row=1, column=col, pady=(6, 0))

        chips = tk.Frame(frame, bg=BG_SETUP)
        chips.pack(pady=(22, 0))
        for minutes in (5, 12, 15, 25):
            self._flat_button(
                chips, f"{minutes}m", lambda m=minutes: self._set_preset(m),
                bg=BG_FIELD, hover=CHIP_HOVER, fg="#c8cedd", font=(UI_FONT, 11),
                padx=16, pady=7, radius=16,
            ).pack(side="left", padx=4)

        self._flat_button(
            frame, "Start", self.start_countdown,
            bg=ACCENT, hover=ACCENT_HOVER, fg="white", font=(UI_FONT, 15, "bold"),
            padx=80, pady=12, radius=22,
        ).pack(pady=(28, 0))

        tk.Label(
            frame, text="Press Enter to start", fg=MUTED, bg=BG_SETUP,
            font=(UI_FONT, 9),
        ).pack(pady=(10, 0))

        for key in ("<space>", "<Escape>", "<q>", "<Q>"):
            self.root.unbind(key)
        self.root.bind("<Return>", lambda e: self.start_countdown())
        min_entry.focus_set()

    def _make_entry(self, parent, var, vcmd):
        entry = tk.Entry(
            parent, textvariable=var, width=3, font=(UI_FONT, 40, "bold"),
            justify="center", relief="flat", bd=0,
            fg="white", bg=BG_FIELD, insertbackground="white",
            selectbackground=ACCENT, selectforeground="white",
            highlightthickness=2, highlightbackground=BORDER, highlightcolor=ACCENT,
            validate="key", validatecommand=vcmd,
        )
        entry.bind("<FocusIn>", lambda e: entry.after_idle(entry.select_range, 0, "end"))
        return entry

    @staticmethod
    def _flat_button(parent, text, command, bg, hover, fg, font, padx, pady, radius):
        """Rounded 'pill' button drawn on a canvas."""
        f = tkfont.Font(font=font)
        w = f.measure(text) + 2 * padx
        h = f.metrics("linespace") + 2 * pady
        r = min(radius, h // 2)
        canvas = tk.Canvas(
            parent, width=w, height=h, bg=BG_SETUP,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        d = 2 * r
        for box in ((0, 0, d, d), (w - d, 0, w, d), (0, h - d, d, h), (w - d, h - d, w, h)):
            canvas.create_oval(*box, fill=bg, outline=bg, tags="shape")
        canvas.create_rectangle(r, 0, w - r, h, fill=bg, outline=bg, tags="shape")
        canvas.create_rectangle(0, r, w, h - r, fill=bg, outline=bg, tags="shape")
        canvas.create_text(w / 2, h / 2, text=text, fill=fg, font=font)
        canvas.bind("<Enter>", lambda e: canvas.itemconfig("shape", fill=hover, outline=hover))
        canvas.bind("<Leave>", lambda e: canvas.itemconfig("shape", fill=bg, outline=bg))
        canvas.bind("<Button-1>", lambda e: command())
        return canvas

    def _set_preset(self, minutes):
        self.minutes_var.set(f"{minutes:02d}")
        self.seconds_var.set("00")

    @staticmethod
    def _validate_digits(new_value):
        return new_value == "" or (new_value.isdigit() and len(new_value) <= 2)

    def start_countdown(self):
        try:
            minutes = int(self.minutes_var.get() or 0)
            seconds = int(self.seconds_var.get() or 0)
        except ValueError:
            return
        total = minutes * 60 + seconds
        if total <= 0:
            return
        self.total_seconds = total
        self.remaining_seconds = total
        self.build_timer_screen()
        self.running = True
        self.update_display()
        self.tick()

    @staticmethod
    def _fit_font_size(sample_text, max_width, max_height):
        """Largest font size (in points) whose rendered text fits the box."""
        ref = 100
        f = tkfont.Font(family=MONO_FONT, size=ref, weight="bold")
        scale = min(max_width / f.measure(sample_text), max_height / f.metrics("linespace"))
        size = max(10, int(ref * scale))
        f.config(size=size)
        while size > 10 and (f.measure(sample_text) > max_width or f.metrics("linespace") > max_height):
            size -= 2
            f.config(size=size)
        return size

    # ---------- fullscreen timer screen ----------
    def build_timer_screen(self):
        self.clear_root()
        self.root.configure(bg=BG_IDLE)
        self.root.attributes("-fullscreen", True)

        self.clock_font_size = 100
        self.done_font_size = 100
        self._fitted_for = None

        self.time_label = tk.Label(
            self.root, text="", fg=FG_IDLE, bg=BG_IDLE,
            font=(MONO_FONT, self.clock_font_size, "bold"),
        )
        self.time_label.pack(expand=True, fill="both")

        self.time_label.bind("<Configure>", self.refit_fonts)

        self.hint_label = tk.Label(
            self.root,
            text="SPACE = pause / resume     ESC = reset     Q / EXIT button (top right) = back to setup",
            font=(UI_FONT, 14), fg="#777777", bg=BG_IDLE,
        )
        self.hint_label.place(relx=0.5, rely=1.0, y=-25, anchor="s")

        self.exit_btn = tk.Label(
            self.root, text="✕  Exit", font=(UI_FONT, 13),
            fg="#777777", bg=BG_IDLE, padx=14, pady=6, cursor="hand2",
        )
        self.exit_btn.place(relx=1.0, x=-15, y=15, anchor="ne")
        self.exit_btn.bind("<Enter>", lambda e: self.exit_btn.config(fg=FG_IDLE, bg="#333333"))
        self.exit_btn.bind("<Leave>", lambda e: self.exit_btn.config(fg="#777777", bg=self.root.cget("bg")))
        self.exit_btn.bind("<Button-1>", lambda e: self.exit_to_setup())

        self.root.unbind("<Return>")
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Escape>", lambda e: self.reset())
        self.root.bind("<q>", lambda e: self.exit_to_setup())
        self.root.bind("<Q>", lambda e: self.exit_to_setup())
        self.finished = False
        self.running = False
        self.update_display()

    def refit_fonts(self, event):
        """Size the fonts to the label's real size (the actual monitor, not the whole desktop)."""
        if event.width < 200 or (event.width, event.height) == self._fitted_for:
            return
        self._fitted_for = (event.width, event.height)
        self.clock_font_size = self._fit_font_size(
            "00:00", max_width=event.width * 0.85, max_height=event.height * 0.7
        )
        self.done_font_size = self._fit_font_size(
            "TIME'S UP!", max_width=event.width * 0.85, max_height=event.height * 0.5
        )
        if self.finished:
            self.time_label.config(font=(MONO_FONT, self.done_font_size, "bold"))
        else:
            self.time_label.config(font=(MONO_FONT, self.clock_font_size, "bold"))

    def update_display(self):
        minutes, seconds = divmod(self.remaining_seconds, 60)
        if self.running:
            fg = FG_IDLE
        elif self.reset_flash:
            fg = FG_RESET
        elif self.user_paused:
            fg = FG_PAUSED
        else:
            fg = FG_IDLE
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}", fg=fg)

    def tick(self):
        """Schedule the next one-second step; the display always shows remaining_seconds."""
        self.timer_job = self.root.after(1000, self.step)

    def step(self):
        self.timer_job = None
        self.remaining_seconds -= 1
        self.update_display()

        if self.remaining_seconds <= 0:
            self.running = False
            self.finished = True
            self.show_times_up()
            return
        self.tick()

    def toggle_pause(self):
        if self.finished:
            return
        if self.running:
            self.running = False
            self.user_paused = True
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
        else:
            self.running = True
            self.user_paused = False
            self.tick()
        self.update_display()

    def show_times_up(self):
        self.root.configure(bg=BG_DONE)
        self.exit_btn.config(bg=BG_DONE, fg="#ffcccc")
        self.hint_label.config(bg=BG_DONE, fg="#ffcccc")
        self.time_label.config(
            text="TIME'S UP!", fg=FG_DONE, bg=BG_DONE,
            font=(MONO_FONT, self.done_font_size, "bold"),
        )

    def reset(self):
        """Back to the initial time, paused; Space starts it again."""
        total = self.total_seconds
        self.build_timer_screen()
        self.remaining_seconds = total
        self.reset_flash = True
        self.update_display()
        self.flash_job = self.root.after(1000, self.end_reset_flash)

    def end_reset_flash(self):
        self.flash_job = None
        self.reset_flash = False
        self.update_display()

    def exit_to_setup(self):
        self.build_setup_screen()

    def clear_root(self):
        if self.flash_job is not None:
            self.root.after_cancel(self.flash_job)
            self.flash_job = None
        self.reset_flash = False
        self.user_paused = False
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    root = tk.Tk()
    CountdownApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
