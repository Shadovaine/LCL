#============================================
# PINS_PATH, _load_pins, _save_pins
#============================================

#----------------Standard Library----------------
from pathlib import Path as _Path
import json

#----------------PINS_PATH----------------
PINS_PATH = _Path(".pins.json")

#----------------_load_pins----------------
def _load_pins() -> set[str]:
    try:
        if PINS_PATH.exists():
            return set(json.loads(PINS_PATH.read_text()))
    except Exception:
        pass
    return set()

#----------------_save_pins----------------
def _save_pins(pins: set[str]):
    PINS_PATH.write_text(json.dumps(sorted(pins), indent=2))