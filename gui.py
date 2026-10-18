import tkinter as tk
from tkinter import ttk, messagebox

import degrees


def load(directory):
    # degrees.load_data fills module-level dicts, so clear them first
    degrees.names.clear()
    degrees.people.clear()
    degrees.movies.clear()
    degrees.load_data(directory)


def choose_person(name):
    """Return a person_id for a name, asking the user if several match."""
    ids = list(degrees.names.get(name.strip().lower(), set()))
    if not ids:
        return None
    if len(ids) == 1:
        return ids[0]

    win = tk.Toplevel(root)
    win.title(f"Which {name}?")
    win.grab_set()
    lb = tk.Listbox(win, width=55, height=min(len(ids), 10))
    for i in ids:
        p = degrees.people[i]
        lb.insert(tk.END, f"{p['name']} (born {p['birth']}) - ID {i}")
    lb.pack(padx=10, pady=10)

    choice = []

    def ok():
        sel = lb.curselection()
        if sel:
            choice.append(ids[sel[0]])
            win.destroy()

    ttk.Button(win, text="Select", command=ok).pack(pady=(0, 10))
    root.wait_window(win)
    return choice[0] if choice else None


def show(text):
    out.config(state="normal")
    out.delete("1.0", tk.END)
    out.insert(tk.END, text)
    out.config(state="disabled")


def on_load():
    status.set("Loading data...")
    root.update_idletasks()
    load(dataset.get())
    status.set(f"Loaded '{dataset.get()}' dataset.")
    search_btn.config(state="normal")


def on_search():
    source = choose_person(name1.get())
    if source is None:
        return messagebox.showerror("Error", f"'{name1.get()}' not found.")
    target = choose_person(name2.get())
    if target is None:
        return messagebox.showerror("Error", f"'{name2.get()}' not found.")

    path = degrees.shortest_path(source, target)
    if path is None:
        return show("Not connected.")

    lines = [f"{len(path)} degrees of separation.\n"]
    path = [(None, source)] + path
    for i in range(len(path) - 1):
        p1 = degrees.people[path[i][1]]["name"]
        p2 = degrees.people[path[i + 1][1]]["name"]
        movie = degrees.movies[path[i + 1][0]]["title"]
        lines.append(f"{i + 1}: {p1} and {p2} starred in {movie}")
    show("\n".join(lines))


root = tk.Tk()
root.title("Degrees of Separation")

dataset = tk.StringVar(value="small")
name1, name2, status = tk.StringVar(), tk.StringVar(), tk.StringVar(value="Load a dataset to begin.")

ttk.Label(root, text="Dataset:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
ttk.Combobox(root, textvariable=dataset, values=["small", "large"], state="readonly", width=10).grid(row=0, column=1, sticky="w")
ttk.Button(root, text="Load data", command=on_load).grid(row=0, column=2, padx=8)

ttk.Label(root, text="Person 1:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
ttk.Entry(root, textvariable=name1, width=30).grid(row=1, column=1, columnspan=2, sticky="w")

ttk.Label(root, text="Person 2:").grid(row=2, column=0, padx=8, pady=6, sticky="e")
ttk.Entry(root, textvariable=name2, width=30).grid(row=2, column=1, columnspan=2, sticky="w")

search_btn = ttk.Button(root, text="Find connection", command=on_search, state="disabled")
search_btn.grid(row=3, column=1, pady=8, sticky="w")

out = tk.Text(root, width=60, height=10, state="disabled", wrap="word")
out.grid(row=4, column=0, columnspan=3, padx=8, pady=4)

ttk.Label(root, textvariable=status).grid(row=5, column=0, columnspan=3, pady=(0, 8))

root.mainloop()