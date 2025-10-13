#=========================================================
# _to_markdown
#=========================================================

#-----------------Standard Library-------------------
from typing import Any, Dict, List

#-----------------_to_Markdown-------------------
def _to_markdown(cmd: dict) -> str:
    lines = [f"# {cmd.get('name') or cmd.get('command') or ''}", cmd.get("description", "") or ""]
    usage = cmd.get("usage") or cmd.get("syntax")
    if usage:
        lines += ["", "## Usage", f"```bash\n{usage}\n```"]
    opts = cmd.get("options")
    if isinstance(opts, list) and opts:
        lines += ["", "## Options"]
        for o in opts:
            if isinstance(o, dict):
                lines.append(f"- `{o.get('flag','')}` — {o.get('description', o.get('meaning',''))}")
            else:
                lines.append(f"- {o}")
    exs = cmd.get("examples")
    if exs:
        lines += ["", "## Examples"]
        if isinstance(exs, list):
            for e in exs:
                if isinstance(e, dict):
                    if e.get("description"):
                        lines.append(f"**{e['description']}**")
                    if e.get("cmd"):
                        lines.append(f"```bash\n{e['cmd']}\n```")                    
                else:
                    lines.append(f"- {e}")
        elif isinstance(exs, str):
            lines.append(exs)
    tags = cmd.get("tags")
    if tags:
        lines += ["", f"*tags:* {', '.join(tags)}"]
    src = cmd.get("_source_path")
    if src:
        lines += ["", f"[source]({src})"]
    return "\n".join(lines)