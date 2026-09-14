import tkinter as tk
import tkinter.font as tkfont

BG_IDLE = "black"
FG_IDLE = "white"
BG_DONE = "red"
FG_DONE = "white"


class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.remaining_seconds = 0
        self.timer_job = None

        self.build_setup_screen()

    # ---------- setup screen ----------
    def build_setup_screen(self):
        self.clear_root()
        self.root.attributes("-fullscreen", False)
        self.root.configure(bg=BG_IDLE)
        self.root.geometry("420x260")
        self.root.eval("tk::PlaceWindow . center")

        frame = tk.Frame(self.root, bg=BG_IDLE)
        frame.pack(expand=True)

        tk.Label(
            frame, text="Atur Waktu (mm:ss)", fg=FG_IDLE, bg=BG_IDLE,
            font=("Arial", 16),
        ).pack(pady=(0, 15))

        entry_frame = tk.Frame(frame, bg=BG_IDLE)
        entry_frame.pack()

        self.minutes_var = tk.StringVar(value="05")
        self.seconds_var = tk.StringVar(value="00")

        vcmd = (self.root.register(self._validate_digits), "%P")

        min_entry = tk.Entry(
            entry_frame, textvariable=self.minutes_var, width=3,
            font=("Arial", 28), justify="center",
            validate="key", validatecommand=vcmd,
        )
        min_entry.grid(row=0, column=0)

        tk.Label(
            entry_frame, text=":", fg=FG_IDLE, bg=BG_IDLE, font=("Arial", 28)
        ).grid(row=0, column=1, padx=6)

        sec_entry = tk.Entry(
            entry_frame, textvariable=self.seconds_var, width=3,
            font=("Arial", 28), justify="center",
            validate="key", validatecommand=vcmd,
        )
        sec_entry.grid(row=0, column=2)

        start_btn = tk.Button(
            frame, text="Mulai", font=("Arial", 14),
            command=self.start_countdown, width=12,
        )
        start_btn.pack(pady=25)

        tk.Label(
            frame, text="Esc = keluar", fg="#888888", bg=BG_IDLE,
            font=("Arial", 9),
        ).pack()

        self.root.bind("<Return>", lambda e: self.start_countdown())
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        min_entry.focus_set()

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
        self.remaining_seconds = total
        self.build_timer_screen()
        self.tick()

    @staticmethod
    def _fit_font_size(sample_text, max_width, max_height, family="Consolas"):
        size = 10
        best = size
        while True:
            f = tkfont.Font(family=family, size=size, weight="bold")
            width = f.measure(sample_text)
            height = f.metrics("linespace")
            if width > max_width or height > max_height:
                break
            best = size
            size += 10
        return best

    # ---------- fullscreen timer screen ----------
    def build_timer_screen(self):
        self.clear_root()
        self.root.configure(bg=BG_IDLE)
        self.root.attributes("-fullscreen", True)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.clock_font_size = self._fit_font_size(
            "00:00", max_width=screen_w * 0.9, max_height=screen_h * 0.7
        )
        self.done_font_size = self._fit_font_size(
            "TIME'S UP!", max_width=screen_w * 0.9, max_height=screen_h * 0.5
        )

        self.time_label = tk.Label(
            self.root, text="", fg=FG_IDLE, bg=BG_IDLE,
            font=("Consolas", self.clock_font_size, "bold"),
        )
        self.time_label.pack(expand=True, fill="both")

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<r>", lambda e: self.reset())
        self.root.bind("<R>", lambda e: self.reset())
        self.time_label.bind("<Button-1>", lambda e: self.reset())

    def tick(self):
        minutes, seconds = divmod(self.remaining_seconds, 60)
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")

        if self.remaining_seconds <= 0:
            self.show_times_up()
            return

        self.remaining_seconds -= 1
        self.timer_job = self.root.after(1000, self.tick)

    def show_times_up(self):
        self.root.configure(bg=BG_DONE)
        self.time_label.config(
            text="TIME'S UP!", fg=FG_DONE, bg=BG_DONE,
            font=("Consolas", self.done_font_size, "bold"),
        )

    def reset(self):
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.root.attributes("-fullscreen", False)
        self.build_setup_screen()

    def clear_root(self):
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
