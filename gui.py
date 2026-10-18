import customtkinter as ctk

import degrees

ctk.set_appearance_mode("system")  # start with the OS setting
ctk.set_default_color_theme("blue")


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

    path = degrees.shortest_path(source, target)
    if path is None:
        return show("Not connected.")

    lines = [f"{len(path)} degrees of separation.\n"]
    path = [(None, source)] + path
    for i in range(len(path) - 1):
        p1 = degrees.people[path[i][1]]["name"]
        p2 = degrees.people[path[i + 1][1]]["name"]
        movie = degrees.movies[path[i + 1][0]]["title"]
        lines.append(f"{i + 1}. {p1} and {p2} starred in {movie}")
    show("\n\n".join(lines))


root = ctk.CTk()
root.title("Degrees of Separation")
root.geometry("580x560")
root.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(root, text="Degrees of Separation",
             font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(24, 4))
ctk.CTkLabel(root, text="Find how two actors are connected through movies",
             text_color="gray").grid(row=1, column=0, pady=(0, 16))

# Dark / light switch (top-right, sharing the title's grid cell)
is_dark = ctk.get_appearance_mode() == "Dark"
mode_switch = ctk.CTkSwitch(root, text="Dark" if is_dark else "Light", command=toggle_mode, width=90)
mode_switch.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ne")
if is_dark:
    mode_switch.select()

# Dataset card
card1 = ctk.CTkFrame(root, corner_radius=12)
card1.grid(row=2, column=0, padx=24, sticky="ew")
card1.grid_columnconfigure(0, weight=1)
dataset = ctk.StringVar(value="small")
ctk.CTkSegmentedButton(card1, values=["small", "large"], variable=dataset).grid(row=0, column=0, padx=16, pady=16, sticky="w")
ctk.CTkButton(card1, text="Load data", width=110, command=on_load).grid(row=0, column=1, padx=16, pady=16)

# Search card
card2 = ctk.CTkFrame(root, corner_radius=12)
card2.grid(row=3, column=0, padx=24, pady=12, sticky="ew")
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

# Results
out = ctk.CTkTextbox(root, height=180, corner_radius=12, font=ctk.CTkFont(size=14), wrap="word", state="disabled")
out.grid(row=4, column=0, padx=24, sticky="nsew")
root.grid_rowconfigure(4, weight=1)

status = ctk.CTkLabel(root, text="Load a dataset to begin.", text_color="gray")
status.grid(row=5, column=0, pady=12)

root.mainloop()