from pathlib import Path
import yaml

def load_all(root: str = "data/commands"):
    """
    Recursively load all command YAMLs from subfolders.
    Keys = command names, Values = full YAML dict.
    Ensures each entry has a 'category' (falls back to folder name if missing).
    """

    out: dict[str, dict] = {}
    for p in Path(root).rglob("**/*.yml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        # Ensure category exists; fallback to parent folder name
        if "category" not in d or not d["category"]:
            d["category"] = p.parent.name
        out[d["name"]] = d
    return out

def list_categories(db: dict[str, dict]) -> list[str]:
    return sorted({meta.get("category","uncategorized") for meta in db.values()})