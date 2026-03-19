# Strategy Viewer

`viewer.py` is a lightweight Python desktop tool for opening exported solver JSON files.

## Requirements

- Python 3
- `numpy`
- `tkinter`

`tkinter` is included with many standard Python installations on Windows.

## Usage

Open a file picker:

```powershell
python viewer/viewer.py
```

Open a specific file directly:

```powershell
python viewer/viewer.py --file your_result.json
```

Optional title suffix:

```powershell
python viewer/viewer.py --file your_result.json --title " - Flop Study"
```

## Notes

- This repo intentionally does not ship large sample strategy dumps by default.
- The viewer is distributed as source only in this repository.

