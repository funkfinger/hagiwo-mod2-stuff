#!/usr/bin/env python3
# make_table_gui.py — WAV → comma‑separated 0x?? text
# MIT‑like license, standard library only

import sys
import wave
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


MAX_FILES = 18
MAX_SECONDS = 20


def pick_files() -> list[Path]:
    """Open a file‑selection dialog and return the chosen paths."""
    root = tk.Tk()
    root.withdraw()
    paths = filedialog.askopenfilenames(
        title=f"Select up to {MAX_FILES} mono 16‑bit PCM WAV files",
        filetypes=[("Wave files", "*.wav"), ("All files", "*.*")]
    )
    root.destroy()
    return [Path(p) for p in paths]


def bail(msg: str) -> None:
    """Show an error dialog and exit."""
    messagebox.showerror("Aborted", msg)
    sys.exit(1)


def process_file(in_path: Path) -> None:
    if not in_path.exists():
        bail(f"File not found: {in_path}")

    out_path = in_path.with_suffix(".txt")

    with wave.open(str(in_path), "rb") as w:
        if w.getnchannels() != 1:
            bail("Stereo is not supported. Use mono.")
        if w.getsampwidth() != 2:
            bail("Only 16‑bit PCM is supported.")
        if w.getcomptype() != "NONE":
            bail("Compressed WAV is not supported.")

        rate = w.getframerate()
        frames = min(rate * MAX_SECONDS, w.getnframes())  # up to 20 seconds
        raw_bytes = w.readframes(frames)

    # Build comma‑separated 0x?? string
    hex_line = ",".join(f"0x{b:02X}" for b in raw_bytes)
    out_path.write_text(hex_line)

    messagebox.showinfo(
        "Done",
        f"Wrote {len(raw_bytes)} bytes ({len(hex_line)} characters) to {out_path.name}"
    )


def main() -> None:
    in_paths = pick_files()

    if not in_paths:
        sys.exit("Cancelled by user")

    if len(in_paths) > MAX_FILES:
        bail(f"Too many files selected ({len(in_paths)}). The limit is {MAX_FILES}.")

    for p in in_paths:
        process_file(p)


if __name__ == "__main__":
    main()
