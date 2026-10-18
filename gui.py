import json
import os
from datetime import datetime

import customtkinter as ctk

import degrees

ctk.set_appearance_mode("system")  # start with the OS setting
ctk.set_default_color_theme("blue")

MAX_HISTORY = 10
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")


def load_history():
    """Read saved searches from disk; return [] if missing or unreadable."""
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            data = json.load(f)
        keys = {"a", "b", "summary", "result", "dataset", "time"}
        return [e for e in data if isinstance(e, dict) and keys <= e.keys()][-MAX_HISTORY:]
    except (OSError, ValueError, TypeError):
        return []


def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError:
        pass  # if saving fails, the app still works for this session


history = load_history()  # oldest first, newest last


def load(directory):
    # degrees.load_data fills module-level dicts, so clear them first
    degrees.names.clear()
    degrees.people.clear()
    degrees.movies.clear()
    degrees.load_data(directory)


def toggle_mode():
    ctk.set_appearance_mode("dark" if mode_switch.get() else "light")
    mode_switch.configure(text="Dark" if mode_switch.get() else "Light")


def choose_person(name):
    """Return a person_id for a name, asking the user if several match."""
    ids = list(degrees.names.get(name.strip().lower(), set()))
    if not ids:
        return None
    if len(ids) == 1:
        return ids[0]

    win = ctk.CTkToplevel(root)
    win.title(f"Which {name}?")
    win.geometry("440x340")
    win.transient(root)
    win.after(100, win.grab_set)

    ctk.CTkLabel(win, text=f"Which '{name}'?", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(16, 8))
    frame = ctk.CTkScrollableFrame(win)
    frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    choice = []

    def pick(person_id):
        choice.append(person_id)
        win.destroy()

    for i in ids:
        p = degrees.people[i]
        ctk.CTkButton(frame, text=f"{p['name']}  ·  born {p['birth']}  ·  ID {i}",
                      anchor="w", command=lambda i=i: pick(i)).pack(fill="x", pady=3)

    root.wait_window(win)
    return choice[0] if choice else None


def show(text):
    out.configure(state="normal")
    out.delete("1.0", "end")
    out.insert("end", text)
    out.configure(state="disabled")


def refresh_history():
    for w in hist_frame.winfo_children():
        w.destroy()
    if not history:
        ctk.CTkLabel(hist_frame, text="No searches yet.", text_color="gray").pack(pady=20)
        return
    for e in reversed(history):  # newest first
        ctk.CTkButton(
            hist_frame, height=54, anchor="w",
            text=f"{e['a']}  →  {e['b']}\n{e['summary']}  ·  {e['dataset']}  ·  {e['time']}",
            command=lambda e=e: open_entry(e),
        ).pack(fill="x", pady=3)


def clear_history():
    history.clear()
    save_history()
    refresh_history()


def open_entry(e):
    name1.set(e["a"])
    name2.set(e["b"])
    show(e["result"])
    tabview.set("Search")


def add_history(a, b, summary, result):
    history.append({
        "a": a, "b": b, "summary": summary, "result": result,
        "dataset": dataset.get(), "time": datetime.now().strftime("%d/%m %H:%M"),
    })
    del history[:-MAX_HISTORY]  # keep only the newest 10
    save_history()
    refresh_history()


def on_load():
    status.configure(text="Loading data...")
    root.update_idletasks()
    load(dataset.get())
    status.configure(text=f"Loaded '{dataset.get()}' dataset.")
    search_btn.configure(state="normal")


def on_search(event=None):
    if search_btn.cget("state") == "disabled":
        return
    source = choose_person(name1.get())
    if source is None:
        return show(f"'{name1.get()}' not found.")
    target = choose_person(name2.get())
    if target is None:
        return show(f"'{name2.get()}' not found.")

    a = degrees.people[source]["name"]
    b = degrees.people[target]["name"]

    path = degrees.shortest_path(source, target)
    if path is None:
        show("Not connected.")
        return add_history(a, b, "Not connected", "Not connected.")

    lines = [f"{len(path)} degrees of separation.\n"]
    steps = [(None, source)] + path
    for i in range(len(steps) - 1):
        p1 = degrees.people[steps[i][1]]["name"]
        p2 = degrees.people[steps[i + 1][1]]["name"]
        movie = degrees.movies[steps[i + 1][0]]["title"]
        lines.append(f"{i + 1}. {p1} and {p2} starred in {movie}")
    result = "\n\n".join(lines)
    show(result)
    add_history(a, b, f"{len(path)} degree{'s' if len(path) != 1 else ''}", result)


root = ctk.CTk()
root.title("Degrees of Separation")
root.geometry("600x640")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(2, weight=1)

ctk.CTkLabel(root, text="Degrees of Separation",
             font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(24, 4))
ctk.CTkLabel(root, text="Find how two actors are connected through movies",
             text_color="gray").grid(row=1, column=0, pady=(0, 8))

# Dark / light switch (top-right, sharing the title's grid cell)
is_dark = ctk.get_appearance_mode() == "Dark"
mode_switch = ctk.CTkSwitch(root, text="Dark" if is_dark else "Light", command=toggle_mode, width=90)
mode_switch.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ne")
if is_dark:
    mode_switch.select()

# Tabs
tabview = ctk.CTkTabview(root)
tabview.grid(row=2, column=0, padx=16, pady=(0, 4), sticky="nsew")
tab_search = tabview.add("Search")
tab_history = tabview.add("History")

# --- Search tab ---
tab_search.grid_columnconfigure(0, weight=1)
tab_search.grid_rowconfigure(2, weight=1)

card1 = ctk.CTkFrame(tab_search, corner_radius=12)
card1.grid(row=0, column=0, padx=8, pady=(8, 0), sticky="ew")
card1.grid_columnconfigure(0, weight=1)
dataset = ctk.StringVar(value="small")
ctk.CTkSegmentedButton(card1, values=["small", "large"], variable=dataset).grid(row=0, column=0, padx=16, pady=16, sticky="w")
ctk.CTkButton(card1, text="Load data", width=110, command=on_load).grid(row=0, column=1, padx=16, pady=16)

card2 = ctk.CTkFrame(tab_search, corner_radius=12)
card2.grid(row=1, column=0, padx=8, pady=12, sticky="ew")
card2.grid_columnconfigure((0, 1), weight=1)
name1 = ctk.StringVar()
name2 = ctk.StringVar()
e1 = ctk.CTkEntry(card2, textvariable=name1, placeholder_text="Person 1  (e.g. Kevin Bacon)", height=38)
e1.grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="ew")
e2 = ctk.CTkEntry(card2, textvariable=name2, placeholder_text="Person 2  (e.g. Tom Cruise)", height=38)
e2.grid(row=0, column=1, padx=(8, 16), pady=(16, 8), sticky="ew")
e1.bind("<Return>", on_search)
e2.bind("<Return>", on_search)
search_btn = ctk.CTkButton(card2, text="Find connection", height=40, state="disabled", command=on_search)
search_btn.grid(row=1, column=0, columnspan=2, padx=16, pady=(8, 16), sticky="ew")

out = ctk.CTkTextbox(tab_search, height=160, corner_radius=12, font=ctk.CTkFont(size=14), wrap="word", state="disabled")
out.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="nsew")

# --- History tab ---
tab_history.grid_columnconfigure(0, weight=1)
tab_history.grid_rowconfigure(1, weight=1)

header = ctk.CTkFrame(tab_history, fg_color="transparent")
header.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="ew")
header.grid_columnconfigure(0, weight=1)
ctk.CTkLabel(header, text=f"Last {MAX_HISTORY} searches (saved between sessions)", text_color="gray").grid(row=0, column=0, sticky="w")
ctk.CTkButton(header, text="Clear history", width=110, fg_color="gray40", hover_color="gray30",
              command=clear_history).grid(row=0, column=1)

hist_frame = ctk.CTkScrollableFrame(tab_history)
hist_frame.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")
refresh_history()

status = ctk.CTkLabel(root, text="Load a dataset to begin.", text_color="gray")
status.grid(row=3, column=0, pady=8)

root.mainloop()