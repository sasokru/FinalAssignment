# File: data_loader.py
import json, os

def load_board(level: int):
    """
    Lädt ein Sudoku-Board für das angegebene Level aus /Assets/data/.
    Gibt None zurück, wenn Datei fehlt oder fehlerhaft ist.
    """
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, "Assets", "data", f"level_{level}.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("board")
    except FileNotFoundError:
        print(f"[WARN] Missing data file for level {level}: {path}")
        return None
    except json.JSONDecodeError:
        print(f"[ERROR] Malformed JSON for level {level}: {path}")
        return None
