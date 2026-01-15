import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import ctypes
from ctypes import wintypes

PROGMAN_FILE = """[programs]
notepad = c:\\windows\\notepad.exe
calc = c:\\windows\\system32\\calc.exe

[paint]
paint =pbrush.exe"""

BUTTONS_PER_ROW = 4

shell32 = ctypes.windll.shell32
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


# ---------------- ICON EXTRACT ----------------

def extract_icon(exe_path):
    large, small = wintypes.HICON(), wintypes.HICON()
    result = shell32.ExtractIconExW(exe_path, 0,
                                    ctypes.byref(large),
                                    ctypes.byref(small), 1)
    if result == 0:
        return None

    hicon = large or small
    if not hicon:
        return None

    hdc = user32.GetDC(0)
    memdc = gdi32.CreateCompatibleDC(hdc)

    bmp = gdi32.CreateCompatibleBitmap(hdc, 32, 32)
    gdi32.SelectObject(memdc, bmp)

    user32.DrawIconEx(memdc, 0, 0, hicon, 32, 32, 0, 0, 3)

    bmpinfo = ctypes.create_string_buffer(40)
    ctypes.memset(bmpinfo, 0, 40)
    ctypes.memmove(bmpinfo, b'\x28', 1)

    bits = ctypes.create_string_buffer(32 * 32 * 4)
    gdi32.GetDIBits(memdc, bmp, 0, 32, bits, bmpinfo, 0)

    image = tk.PhotoImage(width=32, height=32)
    for y in range(32):
        for x in range(32):
            i = (31 - y) * 32 * 4 + x * 4
            b, g, r, a = bits[i:i+4]
            image.put(f"#{r:02x}{g:02x}{b:02x}", (x, y))

    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(memdc)
    user32.ReleaseDC(0, hdc)
    user32.DestroyIcon(hicon)

    return image


def get_exe_from_command(cmd):
    for part in cmd.split(";"):
        part = part.strip()
        if part.lower().endswith(".exe"):
            return part
    return None


# ---------------- GUI ----------------

class ProgManGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ProgMan")
        self.root.configure(bg="black")
        self.root.geometry("720x520")

        self.icons = []  # evitar GC
        self.create_scroll_area()
        self.load_programs()

    def create_scroll_area(self):
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical",
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.frame = tk.Frame(self.canvas, bg="black")
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def load_programs(self):
        if PROGMAN_FILE=="":
            messagebox.showerror("Erro", "progman.dat não encontrado")
            return

        current_group = None
        row = col = 0
        f=PROGMAN_FILE.split("\n")
        if 0==0:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("[") and line.endswith("]"):
                    name = line[1:-1].strip().upper()
                    tk.Label(self.frame, text=f"[ {name} ]",
                             fg="cyan", bg="black",
                             font=("Courier", 12, "bold")).pack(
                        anchor="w", padx=10, pady=(15, 5))

                    current_group = tk.Frame(self.frame, bg="black")
                    current_group.pack(anchor="w", padx=20)

                    row = col = 0
                    continue

                if "=" in line and current_group:
                    text, commands = line.split("=", 1)
                    text = text.strip()
                    commands = commands.strip()

                    icon = None
                    exe = get_exe_from_command(commands)
                    if exe and os.path.exists(exe):
                        icon = extract_icon(exe)
                        if icon:
                            self.icons.append(icon)

                    btn = tk.Button(
                        current_group,
                        text=text,
                        image=icon,
                        compound="top",
                        width=90,
                        height=90,
                        bg="#202020",
                        fg="white",
                        activebackground="#404040",
                        activeforeground="lime",
                        command=lambda c=commands: self.execute_commands(c)
                    )

                    btn.grid(row=row, column=col, padx=6, pady=6)

                    col += 1
                    if col >= BUTTONS_PER_ROW:
                        col = 0
                        row += 1

    def execute_commands(self, command_string):
        for cmd in [c.strip() for c in command_string.split(";") if c.strip()]:
            subprocess.Popen(cmd, shell=True)


# ---------------- MAIN ----------------

if __name__ == "__main__":
    root = tk.Tk()
    ProgManGUI(root)
    root.mainloop()
