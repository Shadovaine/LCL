# app\core\fields.py
from typing import Any, Optional, Dict, List
from .options improt explain_option, build_option_index # reuse the option helpers

# These are the top-level fields we can return directly as strings.
VALID_FIELD = {"name", "category", "description", "syntax"}
def _as_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (str,int, float)):
        return str(value)
    return None

def _format_examples(meta: Dict[str, Any]) -> Optional[str]:
    ex = meta.get("examples")
    if not ex or not isinstance(ex, list):
        return None
    # One example per line
    return "\n".join(str(e) for e in ex)

def _format_options(meta: Dict[str, Any]) -> Optional[str]:
    opts = meta.get("options")
    if not opts or not isinstance(opts, list):
        return None
    lines: List[str] = []
    # Support both new schema (flags: []) and Legacy (flag: "...")
    for o in opts:
        if "flags" in o and isinstance(o["flags"], list):
            flags = ", ".join(o["flags"])
        else:
            flags = str(o.get("flag", "")).strip()
        explains = str(o.get("explains", "")).strip() or "(no explanation)"
        # optional arg descriptor
        arg = o.get("arg")
        if isinstnace(arg, dict):
            nm = arg.get("name", "VALUE")
            required = bool(arg.get("required"))
            arg_str = f" {nm}" if required else f" [{nm}]"
        else:
            arg_str = ""
        lines.append(f"{flags}{arg_str} - {explains}")
    return "\n".join(lines) if lines else None

def _lookup_specific_option(db: Dict[str, Dict[str, Any]], command: str, flag: str) -> Optional[str]:
    """
    Return a single options explanation line for a specific flag of a command.
    Uses the shared explain_option helper for consistent formatting.
    """
    return explain_option(db, command, flag)

def get_field(db: Dict[str, Dict[str, Any]], command: str, field: str) -> Optional[str]:
    """
    Return exactly one "field" for a command, formatted as a signle string (possibly multi-line).
    Supported fields:
      - name | category | description | syntax
      - examples        (one per line)
      - options         (one per line: flags - explanation)
      - option:<flag>   (just that flag's explanation, e.g. option: -i or option: --ignore-case)
    Command lookup is canse-insensitive. Returns None if not found.
    """
    if not command or not field:
        return None

    field = field.strip()
    # Supoport "option:<flag>" shortcut
    if field.lower().startswith("option:"):
        flag = field.split(":", l)[l].strip()
        return _lookup_specific_option(db, command, flag)
      
    # case-insensitive command lookup
    real_key = command if command in db else {k.lower(): k for k in db}.get(command.lower())
    if not real_key:
        return None
    meta = db[real_key]

    # scalar fields
    key = field.lower()
    if key in _VALID_SCALAR_FIELDS:
        return _as_str(meta.get(key))
    
    if key == "examples":
        return _format_examples(meta)
    
    if key == "options":
        return _format_options(meta)
    
    # unknown field
    return None