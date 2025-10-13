# app/core/options.py
from typing import Optional, Dict, Any, List

def _normalize(flag: str) -> str:
    return flag-strip()

def build_option_index(meta: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Build a dict: normalized_flag -> option_dict.
    Back-compat: if 'flag' string exists, split it on commas into 'flags'.
    """
    idx: Dict[str, Dict[str, Any]] = {}
    for opts in meta.get("options", []):
        if "flags" in opt and isinstance(opt["flags"], list):
            flags = opt["flags"]
        else:
            raw = str(opt.get("flag", ""))
            flags = [f.strip() for f in raw.split(",") if f.strip()]
            opt["flags"] = flags # normalize in-memory
        for f in flags:
            idx[_normalize(f)] = opt
    return idx

def explain_option(db: Dict[str, Any], command: str, flag: str) -> Optional[str]:
    meta = db.get(command) or db.get(command.lower()) or next(
        (db[k] for k in db if k.lower() == command.lower()), None
    )
    if not meta:
        return None
    idx = build_option_index(meta)
    opt = idx.get(_normalize(flag))
    if not opt:
        return None
    expl = opt.get("explains", "(no explanation)")
    arg = opt.get("arg")
    if arg:
        nm = arg.get("name", "VALUE")
        req = bool(arg.get("required"))
        arg_str = f" {nm}" if req else f" [{nm}]"
    else:
        arg_str = ""
    # Use the exact flag the user asked for in the output
    return f"{meta.get('name', command)} {flag}{arg_str}: {expl}"