#==========================================================
# summarize_command, detail_text, cmd_search_blob
#==========================================================

#------------------Standard Library-------------------
from typing import Any, Dict, List, Optional
from pathlib import Path as _Path

#------------------Local Library-------------------
from .models import CommandDoc

#------------------Summarize Command-------------------
def summarize_command(cmd: CommandDoc) -> str:
    name = str(cmd.get("name", "")).strip() or "<unnamed>"
    cat = str(cmd.get("category", ""))
    desc = str(cmd.get("description", "")).strip().replace("\n", " ")
    if len(desc) > 120:
        desc = desc[:117] + "..."
    return f"{name}  [{cat}] — {desc}" if desc else f"{name}  [{cat}]"

#------------------Detail Text-------------------
def detail_text(cmd: CommandDoc) -> str:
    lines = []

    def add(label: str, val: Optional[str]):
        if val:
            lines.append(f"[b]{label}[/b]\n{val}\n")

    add("Name", str(cmd.get("name", "")))
    add("Category", str(cmd.get("category", "")))
    add("Description", str(cmd.get("description", "")))
    examples = cmd.get("examples")
    if isinstance(examples, list):
        lines.append("[b]Examples[/b]\n" + "\n".join(f"- {e}" for e in examples) + "\n")
    elif isinstance(examples, str):
        add("Examples", examples)
    usage = cmd.get("usage") or cmd.get("syntax")
    add("Usage", str(usage) if usage else None)
    source = str(cmd.get("_source_path", ""))
    if source:
        lines.append(f"[dim]{source}[/dim]")
    return "\n".join(lines) if lines else "(no details available)"

#------------------Command Search Blob-------------------
def _cmd_search_blob(cmd: CommandDoc) -> str:
    parts: List[str] = [
        str(cmd.get("name", "")),
        str(cmd.get("category", "")),
        str(cmd.get("description", "")),
        str(cmd.get("usage", "")),
        str(cmd.get("syntax", "")),
    ]
    opts = cmd.get("options")
    if isinstance(opts, list):
        for o in opts:
            if isinstance(o, dict):
                parts.append(str(o.get("flag", "")))
                parts.append(str(o.get("description", "")))
            else:
                parts.append(str(o))
    elif isinstance(opts, dict):
        for k, v in opts.items():
            parts.append(str(k))
            parts.append(str(v))
    return " ".join(parts).lower()