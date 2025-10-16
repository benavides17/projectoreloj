import time
import math
import datetime as dt
from zoneinfo import ZoneInfo
import tkinter as tk
from tkinter import ttk, messagebox

APP = "Reloj Python - Todo en uno"
REFRESH_MS = 200
LANGS = {
    "es": {"weekdays": ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"],
           "months":   ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"],
           "fmt": "{weekday}, {day} de {month} de {year}"},
    "en": {"weekdays": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
           "months":   ["January","February","March","April","May","June","July","August","September","October","November","December"],
           "fmt": "{weekday}, {month} {day}, {year}"},
    "pt": {"weekdays": ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"],
           "months":   ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"],
           "fmt": "{weekday}, {day} de {month} de {year}"},
    "fr": {"weekdays": ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"],
           "months":   ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"],
           "fmt": "{weekday} {day} {month} {year}"},
}

def fmt_date_localized(now: dt.datetime, lang: str) -> str:
    l = LANGS.get(lang, LANGS["es"])
    wd = l["weekdays"][now.weekday()]
    mo = l["months"][now.month - 1]
    s = l["fmt"].format(weekday=wd, day=f"{now.day:02d}", month=mo, year=now.year)
    return s[:1].upper() + s[1:]

def fmt_hhmmss(s: int) -> str:
    h = s // 3600; m = (s % 3600) // 60; ss = s % 60
    return f"{h:02d}:{m:02d}:{ss:02d}"

class AnalogClock(ttk.Frame):
    """Reloj analógico dibujado en Canvas, con soporte de tema."""
    def __init__(self, master, size=260, bg="#f7f7f7", fg="#1a1a1a", accent="#e11d48"):
        super().__init__(master)
        self.size = size
        self.r = size // 2 - 10
        self.bg, self.fg, self.accent = bg, fg, accent
        self.canvas = tk.Canvas(self, width=size, height=size, highlightthickness=0, bd=0, bg=self.bg)
        self.canvas.pack()
        self._hands = {}
        self._draw_face()
        self.update_time()

    def set_theme(self, bg, fg, accent=None):
        if accent is None:
            accent = self.accent
        self.bg, self.fg, self.accent = bg, fg, accent
        self.canvas.configure(bg=self.bg)
        self.canvas.delete("all")
        self._hands = {}
        self._draw_face()

    def _draw_face(self):
        c = self.canvas; s = self.size; r = self.r
        c.create_oval(10, 10, s-10, s-10, width=2, outline=self.fg)
        for i in range(60):
            ang = math.radians(i*6)
            x0 = s/2 + (r-10) * math.sin(ang)
            y0 = s/2 - (r-10) * math.cos(ang)
            length = 12 if i % 5 == 0 else 5
            x1 = s/2 + (r-10-length) * math.sin(ang)
            y1 = s/2 - (r-10-length) * math.cos(ang)
            w = 2 if i % 5 == 0 else 1
            c.create_line(x0, y0, x1, y1, width=w, fill=self.fg)
        for h in range(1, 13):
            ang = math.radians(h*30)
            x = s/2 + (r-30) * math.sin(ang)
            y = s/2 - (r-30) * math.cos(ang)
            c.create_text(x, y, text=str(h), font=("Arial", 12, "bold"), fill=self.fg)
        c.create_oval(s/2-4, s/2-4, s/2+4, s/2+4, fill=self.fg, outline="")
        self._hands["hour"] = c.create_line(s/2, s/2, s/2, s/2- r*0.5, width=4, capstyle="round", fill=self.fg)
        self._hands["min"]  = c.create_line(s/2, s/2, s/2, s/2- r*0.72, width=3, capstyle="round", fill=self.fg)
        self._hands["sec"]  = c.create_line(s/2, s/2, s/2, s/2- r*0.82, width=1, capstyle="round", fill=self.accent)

    def update_time(self, now=None):
        if now is None:
            now = dt.datetime.now()
        s = self.size; r = self.r
        h = now.hour % 12 + now.minute/60 + now.second/3600
        m = now.minute + now.second/60
        sec = now.second + now.microsecond/1e6

        def endpoint(deg, length):
            ang = math.radians(deg)
            x = s/2 + length * math.sin(ang)
            y = s/2 - length * math.cos(ang)
            return x, y

        hx, hy = endpoint(h*30, r*0.5)
        mx, my = endpoint(m*6, r*0.72)
        sx, sy = endpoint(sec*6, r*0.82)
        c = self.canvas
        c.coords(self._hands["hour"], s/2, s/2, hx, hy)
        c.coords(self._hands["min"],  s/2, s/2, mx, my)
        c.coords(self._hands["sec"],  s/2, s/2, sx, sy)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP)
        self.geometry("1000x680")

        # Estado
        self.is_24h = tk.BooleanVar(value=True)
        self.dark = tk.BooleanVar(value=False)
        self.lang = tk.StringVar(value="es")
        self.blink = True
        self.last_hour_chime = None

        self._init_style()
        self._menu()

        # Topbar controles
        topbar = ttk.Frame(self); topbar.pack(fill="x", padx=12, pady=(10, 0))
        ttk.Checkbutton(topbar, text="24h", variable=self.is_24h).pack(side="left", padx=(0,8))
        ttk.Checkbutton(topbar, text="Oscuro", variable=self.dark, command=self._apply_colors).pack(side="left", padx=(0,8))
        ttk.Label(topbar, text="Idioma:").pack(side="left", padx=(8,4))
        lang_cb = ttk.Combobox(topbar, textvariable=self.lang, state="readonly", width=6, values=list(LANGS.keys()))
        lang_cb.pack(side="left")
        lang_cb.bind("<<ComboboxSelected>>", lambda e: self._render_date())

        top = ttk.Frame(self); top.pack(fill="x", padx=12, pady=12)
        self.lbl = ttk.Label(top, text="00:00:00", font=("SF Pro Display", 72, "bold"))
        self.lbl.pack(side="left", padx=(0, 20))
        self.analog = AnalogClock(top, size=260)  
        self.analog.pack(side="left")

        self.lbl_date = ttk.Label(self, text="", style="Sub.TLabel", font=("SF Pro Text", 16))
        self.lbl_date.pack(pady=(0, 10))

      
        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=True, padx=12, pady=8)
        self._tab_alarma()
        self._tab_temporizador()
        self._tab_crono()
        self._tab_timezones()

        self.after(REFRESH_MS, self._tick)
        self._apply_colors()  

    def _init_style(self):
        self.style = ttk.Style(self)
        base = "clam" if "clam" in self.style.theme_names() else self.style.theme_use()
        self.style.theme_use(base)
        self._apply_colors()

    def _apply_colors(self):
        if self.dark.get():
            bg, fg, sub, acc = "#0f1115", "#e8e8e8", "#9aa4ad", "#4f9cff"
        else:
            bg, fg, sub, acc = "#f7f7f7", "#1a1a1a", "#4b5563", "#2563eb"
        self.configure(bg=bg)
        self.style.configure(".", background=bg, foreground=fg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("Sub.TLabel", foreground=sub)
        self.style.configure("Accent.TButton", padding=8, background=acc)
        self.style.map("Accent.TButton", background=[("active", acc)])
        try:
            self.analog.set_theme(bg=bg, fg=fg, accent="#e11d48")
        except Exception:
            pass

    def _menu(self):
        m = tk.Menu(self); self.config(menu=m)
        vista = tk.Menu(m, tearoff=False)
        vista.add_checkbutton(label="Formato 24 h", variable=self.is_24h)
        vista.add_checkbutton(label="Tema oscuro", variable=self.dark, command=self._apply_colors)
        m.add_cascade(label="Vista", menu=vista)
        ayuda = tk.Menu(m, tearoff=False)
        ayuda.add_command(label="Acerca de", command=lambda: messagebox.showinfo(
            "Acerca de",
            "Reloj: Digital + Analógico, Alarma, Temporizador, Cronómetro,\n"
            "Idiomas (ES/EN/PT/FR) y Zonas horarias."
        ))
        m.add_cascade(label="Ayuda", menu=ayuda)

    def _tab_alarma(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Alarma")
        ttk.Label(f, text="Hora (24h) HH:MM").grid(row=0, column=0, sticky="w")
        self.al_h = tk.StringVar(value=dt.datetime.now().strftime("%H"))
        self.al_m = tk.StringVar(value="00")
        row = ttk.Frame(f); row.grid(row=1, column=0, pady=4, sticky="w")
        ttk.Entry(row, width=4, textvariable=self.al_h, justify="center").pack(side="left")
        ttk.Label(row, text=":").pack(side="left")
        ttk.Entry(row, width=4, textvariable=self.al_m, justify="center").pack(side="left")
        self.al_msg = tk.StringVar(value="¡Despierta!")
        ttk.Label(f, text="Mensaje").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(f, textvariable=self.al_msg).grid(row=3, column=0, sticky="ew", pady=4)
        btns = ttk.Frame(f); btns.grid(row=4, column=0, pady=8, sticky="w")
        self.btn_al_on = ttk.Button(btns, text="Activar", command=self._alarm_on, style="Accent.TButton"); self.btn_al_on.pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Desactivar", command=self._alarm_off).pack(side="left")
        self.lbl_al = ttk.Label(f, text="Alarma inactiva", style="Sub.TLabel"); self.lbl_al.grid(row=5, column=0, sticky="w", pady=(6, 0))
        f.columnconfigure(0, weight=1)
        self.al_active = False; self._last_beep_sec = -1

    def _alarm_on(self):
        try:
            h = int(self.al_h.get()); m = int(self.al_m.get())
            assert 0 <= h < 24 and 0 <= m < 60
        except Exception:
            messagebox.showerror("Formato inválido", "Usa HH (00-23) y MM (00-59)."); return
        self.al_active = True
        self.lbl_al.config(text=f"Alarma activada para {int(self.al_h.get()):02d}:{int(self.al_m.get()):02d}")
        self.btn_al_on.state(["disabled"])

    def _alarm_off(self):
        self.al_active = False
        self.lbl_al.config(text="Alarma inactiva")
        self.btn_al_on.state(["!disabled"])

    def _check_alarm(self, now):
        if not self.al_active: return
        try:
            hh = int(self.al_h.get()); mm = int(self.al_m.get())
        except Exception:
            return
        if now.hour == hh and now.minute == mm:
            if now.second != self._last_beep_sec:
                self._beep(); self._last_beep_sec = now.second
            if now.second == 0:
                self._beep(3); messagebox.showinfo("Alarma", self.al_msg.get()); self._alarm_off()

    def _tab_temporizador(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Temporizador")
        ttk.Label(f, text="Duración (HH:MM:SS)").grid(row=0, column=0, sticky="w")
        self.t_h = tk.StringVar(value="00"); self.t_m = tk.StringVar(value="05"); self.t_s = tk.StringVar(value="00")
        row = ttk.Frame(f); row.grid(row=1, column=0, pady=4, sticky="w")
        for var, last in ((self.t_h, ":"), (self.t_m, ":"), (self.t_s, "")):
            ttk.Entry(row, width=4, textvariable=var, justify="center").pack(side="left")
            if last: ttk.Label(row, text=last).pack(side="left")
        self.lbl_t = ttk.Label(f, text="00:05:00", font=("SF Pro Display", 36, "bold")); self.lbl_t.grid(row=2, column=0, pady=8, sticky="w")
        self.pbar = ttk.Progressbar(f, mode="determinate", length=420); self.pbar.grid(row=3, column=0, sticky="ew")
        btns = ttk.Frame(f); btns.grid(row=4, column=0, pady=8, sticky="w")
        ttk.Button(btns, text="Iniciar", command=self._t_start, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Pausar/Reanudar", command=self._t_toggle).pack(side="left", padx=4)
        ttk.Button(btns, text="Reiniciar", command=self._t_reset).pack(side="left", padx=4)
        f.columnconfigure(0, weight=1)
        self.t_total = 300; self.t_left = 300; self.t_running = False; self.t_paused = False

    def _t_start(self):
        try:
            h = int(self.t_h.get()); m = int(self.t_m.get()); s = int(self.t_s.get())
            assert h >= 0 and 0 <= m < 60 and 0 <= s < 60
        except Exception:
            messagebox.showerror("Formato inválido", "HH:MM:SS válidos."); return
        self.t_total = h*3600 + m*60 + s
        if self.t_total <= 0: messagebox.showwarning("Duración inválida", "Debe ser > 0."); return
        self.t_left = self.t_total; self.t_running = True; self.t_paused = False; self._t_tick()

    def _t_toggle(self):
        if self.t_running: self.t_paused = not self.t_paused

    def _t_reset(self):
        self.t_running = False; self.t_paused = False; self.t_left = self.t_total; self._t_render()

    def _t_tick(self):
        if not self.t_running: return
        if not self.t_paused and self.t_left > 0: self.t_left -= 1
        if self.t_left <= 0:
            self._t_render(); self._beep(3); messagebox.showinfo("Temporizador", "¡Tiempo cumplido!"); self.t_running = False; return
        self._t_render(); self.after(1000, self._t_tick)

    def _t_render(self):
        self.lbl_t.config(text=fmt_hhmmss(self.t_left))
        self.pbar["value"] = 100 * (1 - (self.t_left / max(1, self.t_total)))

    def _tab_crono(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Cronómetro")
        self.lbl_c = ttk.Label(f, text="00:00:00.00", font=("SF Pro Display", 36, "bold")); self.lbl_c.pack(anchor="w", pady=6)
        btns = ttk.Frame(f); btns.pack(anchor="w", pady=4)
        ttk.Button(btns, text="Iniciar/Pausa", command=self._c_toggle, style="Accent.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Lap", command=self._c_lap).pack(side="left", padx=4)
        ttk.Button(btns, text="Reiniciar", command=self._c_reset).pack(side="left", padx=4)
        self.laps = tk.Listbox(f, height=8); self.laps.pack(fill="both", expand=True, pady=8)
        self.c_running = False; self.c_start = None; self.c_acc = 0.0; self.c_last_lap = 0.0

    def _c_toggle(self):
        if not self.c_running:
            self.c_running = True; self.c_start = time.perf_counter(); self.after(10, self._c_tick)
        else:
            self.c_running = False; self.c_acc += time.perf_counter() - self.c_start

    def _c_tick(self):
        if not self.c_running: return
        tot = self.c_acc + (time.perf_counter() - self.c_start)
        self.lbl_c.config(text=self._fmt_ms(tot)); self.after(10, self._c_tick)

    def _c_reset(self):
        self.c_running = False; self.c_start = None; self.c_acc = 0.0; self.c_last_lap = 0.0
        self.lbl_c.config(text="00:00:00.00"); self.laps.delete(0, tk.END)

    def _c_lap(self):
        total = self._c_total(); lap = total - self.c_last_lap; self.c_last_lap = total
        idx = self.laps.size() + 1
        self.laps.insert(tk.END, f"Lap {idx:02d} | Total {self._fmt_ms(total)} | +{self._fmt_ms(lap)}")

    def _c_total(self):
        if self.c_running and self.c_start is not None:
            return self.c_acc + (time.perf_counter() - self.c_start)
        return self.c_acc

    @staticmethod
    def _fmt_ms(t):
        h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); cs = int((t - int(t)) * 100)
        return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"

    def _tab_timezones(self):
        f = ttk.Frame(self.nb); self.nb.add(f, text="Zonas Horarias")
        self.timezones = tk.Variable(value=[
            "UTC", "America/Bogota", "America/Mexico_City",
            "Europe/Madrid", "America/New_York", "Europe/London", "Asia/Tokyo"
        ])

        left = ttk.Frame(f); left.pack(side="left", fill="y", padx=(0,12), pady=8)
        ttk.Label(left, text="Zonas (IANA):").pack(anchor="w")
        self.lb_tz = tk.Listbox(left, listvariable=self.timezones, height=12)
        self.lb_tz.pack(fill="y")
        controls = ttk.Frame(left); controls.pack(anchor="w", pady=6)
        self.entry_tz = ttk.Entry(controls, width=24); self.entry_tz.pack(side="left")
        ttk.Button(controls, text="Agregar", command=self._tz_add).pack(side="left", padx=6)
        ttk.Button(controls, text="Quitar", command=self._tz_remove).pack(side="left")

        right = ttk.Frame(f); right.pack(side="left", fill="both", expand=True, pady=8)
        cols = ("zona", "hora")
        self.tv = ttk.Treeview(right, columns=cols, show="headings", height=12)
        self.tv.heading("zona", text="Zona"); self.tv.heading("hora", text="Hora")
        self.tv.column("zona", width=260, anchor="w"); self.tv.column("hora", width=160, anchor="center")
        self.tv.pack(fill="both", expand=True)
        self._tz_refresh()

    def _tz_add(self):
        z = self.entry_tz.get().strip()
        if not z: return
        try:
            _ = ZoneInfo(z)
            items = list(self.timezones.get())
            if z not in items:
                items.append(z); self.timezones.set(items)
                self._tz_refresh(); self.entry_tz.delete(0, tk.END)
        except Exception:
            messagebox.showerror("Zona inválida", "Usa un nombre IANA válido, p.ej. Europe/Madrid, America/Los_Angeles.")

    def _tz_remove(self):
        sel = list(self.lb_tz.curselection())
        if not sel: return
        items = list(self.timezones.get())
        for idx in reversed(sel): items.pop(idx)
        self.timezones.set(items); self._tz_refresh()

    def _tz_refresh(self):
        for i in self.tv.get_children(): self.tv.delete(i)
        now = dt.datetime.now(dt.timezone.utc)
        for z in self.timezones.get():
            try:
                local = now.astimezone(ZoneInfo(z))
                self.tv.insert("", "end", values=(z, local.strftime("%H:%M:%S")))
            except Exception:
                pass

    def _tick(self):
        now = dt.datetime.now()
        self.blink = not self.blink
        sep = ":" if self.blink else " "
        txt = now.strftime(f"%H{sep}%M{sep}%S") if self.is_24h.get() else now.strftime(f"%I{sep}%M{sep}%S %p")
        self.lbl.config(text=txt)
        self._render_date(now)
        self.analog.update_time(now)
        self._check_alarm(now)
        if now.minute == 0 and now.second == 0 and self.last_hour_chime != now.hour:
            self._beep(2); self.last_hour_chime = now.hour
        self._tz_refresh()
        self.after(REFRESH_MS, self._tick)

    def _render_date(self, now=None):
        if now is None: now = dt.datetime.now()
        self.lbl_date.config(text=fmt_date_localized(now, self.lang.get()))

    def _beep(self, n=1):
        for _ in range(n):
            try:
                import winsound; winsound.Beep(1000, 220)
            except Exception:
                self.bell()
            self.after(60, lambda: None)

if __name__ == "__main__":
    App().mainloop()
