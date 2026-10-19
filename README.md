# Degrees of Separation

Find how two actors are connected through the movies they have starred in, using the IMDb-style CSV datasets provided with the assignment. The project has two parts:

- **`degrees.py`**: the command-line program, where `shortest_path` is implemented with breadth-first search (BFS).
- **`gui.py`**: a modern desktop interface built with CustomTkinter, with dark/light mode and a saved search history.

## Features

- Shortest path between any two actors (fewest movies in between)
- Command-line and graphical interfaces
- Dark / light mode switch
- History tab that keeps your last 10 searches between sessions
- Disambiguation popup when several people share the same name

## Project structure

```
.
├── degrees.py      # Data loading + shortest_path (BFS) + terminal interface
├── util.py         # Node, StackFrontier, QueueFrontier
├── gui.py          # Desktop interface
├── history.json    # Created automatically by gui.py
├── small/          # Small dataset (for testing)
│   ├── people.csv
│   ├── movies.csv
│   └── stars.csv
└── large/          # Full dataset
    ├── people.csv
    ├── movies.csv
    └── stars.csv
```

## Requirements

- Python 3.8 or newer
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (GUI only)

```
pip install customtkinter
```

Tkinter, which CustomTkinter builds on, ships with the standard Python installers. The terminal version needs no extra packages.

## Usage

### Terminal

```
python degrees.py small
python degrees.py large
```

If no directory is given, `large` is used. You will be asked for two names, and the program prints each step of the shortest chain:

```
Name: Kevin Bacon
Name: Tom Cruise
1 degrees of separation.
1: Kevin Bacon and Tom Cruise starred in A Few Good Men
```

### Graphical interface

```
python gui.py
```

1. Choose **small** or **large** and click **Load data** (`large` can take a few seconds, and the window may appear frozen while it loads or searches).
2. Type two actor names and click **Find connection** (or press Enter).
3. If a name matches several people, pick the right one from the popup. Check the birth year and ID to tell them apart.
4. Open the **History** tab to revisit recent searches. Click an entry to reopen its result, or use **Clear history** to empty the list.
5. Use the switch in the top-right corner to change between dark and light mode.

## How it works

The data is treated as a graph:

- **Nodes** are people, identified by their IMDb `person_id`.
- **Edges** connect two people who starred in the same movie, labelled with the `movie_id`.

`shortest_path(source, target)` runs BFS:

1. Start with the source in a `QueueFrontier` (first in, first out).
2. Keep a `seen` set of every person already discovered, so nobody is processed twice.
3. For each person removed from the frontier, look at their co-stars with `neighbors_for_person`.
4. Check each new co-star against the target **as soon as it is discovered**. If it matches, follow the `parent` pointers back to the source and return the path.
5. If the frontier becomes empty, the two people are not connected and the function returns `None`.

Because BFS explores people one step away, then two steps away, and so on, the first path it finds is guaranteed to be a shortest one.

The function returns a list of `(movie_id, person_id)` tuples, where each pair says "reached this person through this movie". If source and target are the same person, it returns an empty list.

## Notes

- **Duplicate names are normal.** IMDb has different people with the same name, and birth year is optional, so some entries have none. For example, searching "Kevin Bacon" on `large` offers two matches; the one born in 1958 (ID 102) is the actor from *A Few Good Men*.
- **History file:** `history.json` is created next to `gui.py`. It stores the last 10 searches and can be deleted at any time to reset the history.
- **Datasets are separate.** Many pairs that connect in `large` will show "Not connected" in `small`, because `small` is only a slice of the data.

## Assignment constraint

For the course submission, only the `shortest_path` function in `degrees.py` was changed. `gui.py` is a separate file that imports `degrees.py` and does not modify it.

## Acknowledgments

AI tools were used as support while building this project:

- **Claude AI (Anthropic):** help with parts of the UI structure and with debugging.
- **Gemini AI (Google):** help with this README file.

All code was reviewed, tested and adapted by the project author, who is responsible for the final result.