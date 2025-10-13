#==========================
# admin config
#==========================

from __future__ import annotations

#---------Standard Imports---------
import os
from pathlib import Path

#---------Admin config Flag---------
def _read_local_admin_flag() -> bool:
    # ~/.config/lcl/config.toml  ->  admin = true
    cfg = Path.home() / ".config" / "lcl" / "config.toml"
    if cfg.is_file():
        try:
            # Python 3.11+ has tomllib
            import tomllib
            data = tomllib.loads(cfg.read_text(encoding="utf-8"))
            return bool(data.get("admin", False))
        except Exception:
            pass
    return False

def is_admin() -> bool:
    # Priority: env var, then user config file
    if os.getenv("LCL_ADMIN", "").lower() in {"1", "true", "yes"}:
        return True
    return _read_local_admin_flag()
