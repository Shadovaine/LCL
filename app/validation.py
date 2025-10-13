#===============================================
# _validate_doc_minimal, _save_new_command
#===============================================

#-----------------Standard Library--------------
from typing import Any, Dict, List, Tuple
from pathlib import Path as _Path
import yaml

#-----------------Local Library-----------------
from .models import ALLOWED_CATEGORIES
from .paths import _find_commands_base

#-----------------_validate_doc_minimal-----------------
def _validate_doc_minimal(doc: Dict[str, Any]) -> list[str]:
    """Minimal synchronous validation used by the TUI form."""
    issues: list[str] = []
    def nonempty(x): return isinstance(x, str) and x.strip() != ""
    name = doc.get("name") or doc.get("command") or doc.get("title")
    if not nonempty(name):
        issues.append("Missing required 'name' (or 'command'/'title').")
    cat = str(doc.get("category") or "").strip()
    if not cat:
        issues.append("Missing 'category'.")
    elif cat not in ALLOWED_CATEGORIES:
        issues.append(f"Category '{cat}' not in allowed categories.")
    if not nonempty(doc.get("description", "")):
        issues.append("Missing or empty 'description'.")
    if not (nonempty(doc.get("usage", "")) or nonempty(doc.get("syntax", ""))):
        issues.append("Missing 'usage' or 'syntax'.")
    # soft checks
    opts = doc.get("options")
    if opts is not None and not isinstance(opts, (list, dict)):
        issues.append("'options' should be a list or mapping.")
    ex = doc.get("examples")
    if ex is not None and not (isinstance(ex, (list, str))):
        issues.append("'examples' should be a list or a string.")
    return issues

#-----------------_save_new_command-----------------
def _save_new_command(doc: Dict[str, Any]) -> tuple[bool, str]:
    """Write YAML into the proper category folder with a safe filename."""
    base = _find_commands_base()
    cat = doc["category"]
    target_dir = (base / cat)
    target_dir.mkdir(parents=True, exist_ok=True)

    # filename from name
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(doc.get("name", "")))
    if not safe:
        safe = "command"
    # avoid overwrite
    fp = target_dir / f"{safe}.yml"
    i = 2
    while fp.exists():
        fp = target_dir / f"{safe}-{i}.yml"
        i += 1

    try:
        fp.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return True, str(fp)
    except Exception as e:
        return False, f"Failed to write file: {e}"