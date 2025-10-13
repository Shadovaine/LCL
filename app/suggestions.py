#=================================================
# _suggestions_dir, _safe_slug, _save_suggestion
#=================================================

#--------------------Standard Library-------------
from typing import Any, Dict
from datetime import datetime
from pathlib import Path as _Path
import os
import yaml

#--------------------Local Library----------------
from .paths import _repo_root

#--------------------_suggestions_dir-------------
def _suggestions_dir() -> _Path:
    d = _repo_root() / ".inbox" / "suggestions"
    d.mkdir(parents=True, exist_ok=True)
    return d

#--------------------_safe_slug-------------------
def _safe_slug(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return "unnamed"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in s)[:60]

#--------------------_save_suggestion----------------
def _save_suggestion(payload: Dict[str, Any]) -> _Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    name = _safe_slug(str(payload.get("name") or payload.get("command") or "suggestion"))
    out = _suggestions_dir() / f"{ts}-{name}.yml"
    payload = dict(payload)  # shallow copy
    # attach meta
    payload["_meta"] = {
        "type": "suggestion",
        "created_at": ts,
        "user": os.getenv("USER") or os.getenv("USERNAME") or "",
        "host": os.uname().nodename if hasattr(os, "uname") else "",
    }
    out.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return out