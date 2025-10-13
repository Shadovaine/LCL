#!/usr/bin/env python3
# app.py — Unified TUI + YAML loader for Linux Command Library (data/commands aware)

from __future__ import annotations

# ---------- Standard libs ----------
from pathlib import Path as _Path
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import os, json, subprocess, shlex
import yaml

# ---------- Optional fuzzy search ----------
try:
    from rapidfuzz import process, fuzz
    HAVE_FUZZ = True
except Exception:
    HAVE_FUZZ = False

# ---------- Textual UI ----------
from textual.app import App, ComposeResult
from textual.widgets import Input, Static, ListView, ListItem, Label, Button, MarkdownViewer
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen  # portable modal

# Optional multi-line editor (newer Textual). Falls back to Input if missing.
try:
    from textual.widgets import TextArea
    HAVE_TEXTAREA = True
except Exception:
    HAVE_TEXTAREA = False
    TextArea = None  # type: ignore

# Hot-Reload
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAVE_WATCHDOG = True
except Exception:
    HAVE_WATCHDOG = False

# ======================================================================================
# CATEGORY WHITELIST
# ======================================================================================
STRICT_CATEGORIES = False
ALLOWED_CATEGORIES = {
    "Archive_Compression_Mgmt",
    "File_Directory_Mgmt",
    "Hardware_Kernel_Tools",
    "Linux_Directory_System",
    "Networking_Tools",
    "Package_Management",
    "Permission_and_Ownership",
    "Process_Management",
    "Searching_and_Filtering_Management",
    "System_Administration",
    "System_Information_and_Monitoring_Management",
    "TroubleShooting_Management",
    "User_and_Group_Management",
    "Viewing_and_Editing_Management",
    "WildCards",
}

# ======================================================================================
# YAML LOADER
# ======================================================================================
CommandDoc = Dict[str, Any]


def _expand(p: str | _Path) -> _Path:
    return _Path(str(p)).expanduser().resolve()


def _candidate_paths_for_commands() -> List[_Path]:
    here = _Path(__file__).resolve()
    cwd = _Path.cwd().resolve()
    override = os.getenv("CMD_DIR")
    if override:
        return [_expand(override)]
    candidates: List[_Path] = []
    for root in (cwd, here.parent, *here.parents):
        candidates.append(_expand(root / "data" / "commands"))
        candidates.append(_expand(root / "commands"))
    seen = set()
    ordered: List[_Path] = []
    for p in candidates:
        if p not in seen:
            ordered.append(p)
            seen.add(p)
    return ordered

def _find_commands_base() -> _Path:
    for cand in _candidate_paths_for_commands():
        if cand.is_dir():
            return cand
    raise RuntimeError(
        "Could not locate a 'data/commands' or 'commands' directory.\n"
        "Set CMD_DIR=/absolute/path/to/.../data/commands or run from your repo."
    )

def _iter_category_yaml(commands_base: _Path):
    for cat in sorted(ALLOWED_CATEGORIES):
        cat_dir = commands_base / cat
        if not cat_dir.is_dir():
            print(f"[warn] Missing category folder: {cat_dir}")
            continue
        yield from cat_dir.rglob("*.yml")
        yield from cat_dir.rglob("*.yaml")

def _iter_all_yaml(commands_base: _Path):
    yield from commands_base.rglob("*.yml")
    yield from commands_base.rglob("*.yaml")

def _infer_category_from_path(yml_path: _Path, commands_base: _Path) -> str:
    try:
        rel = yml_path.relative_to(commands_base)
        cat = rel.parts[0] if rel.parts else "uncategorized"
        return cat if (cat in ALLOWED_CATEGORIES or not STRICT_CATEGORIES) else "uncategorized"
    except ValueError:
        return "uncategorized"

def _load_yaml_file(fp: _Path) -> Any:
    raw = fp.read_text(encoding="utf-8")
    if not raw.strip():
        print(f"[warn] empty YAML: {fp}")
        return None
    try:
        return yaml.safe_load(raw)
    except Exception as e:
        print(f"[warn] failed to parse YAML {fp}: {e}")
        return None

def load_all_commands() -> List[CommandDoc]:
    base = _find_commands_base()
    print(f"[debug] commands base: {base}")

    files = list((_iter_category_yaml if STRICT_CATEGORIES else _iter_all_yaml)(base))
    print(
        f"[debug] found {len(files)} YAML files under {'whitelisted' if STRICT_CATEGORIES else 'ALL'} categories"
    )

    commands: List[CommandDoc] = []
    per_cat_count: Dict[str, int] = defaultdict(int)

    def _attach_meta(obj: Dict[str, Any], cat: str, fp: _Path):
        obj.setdefault("category", cat)
        obj.setdefault("_source_path", str(fp.resolve()))
        if "name" not in obj or not obj.get("name"):
            obj["name"] = fp.stem

    for fp in files:
        data = _load_yaml_file(fp)
        if data is None:
            continue
        cat = _infer_category_from_path(fp, base)
        if isinstance(data, dict):
            _attach_meta(data, cat, fp)
            commands.append(data)
            per_cat_count[data["category"]] += 1
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    _attach_meta(item, cat, fp)
                    commands.append(item)
                    per_cat_count[item["category"]] += 1
                else:
                    print(f"[warn] non-dict list item skipped in {fp}: {type(item).__name__}")
        else:
            print(f"[warn] unsupported YAML top-level type in {fp}: {type(data).__name__}")

    loaded_total = sum(per_cat_count.values())
    print(f"[debug] loaded {loaded_total} command docs")
    if loaded_total == 0:
        print("WARNING: 0 commands loaded. Tip: set CMD_DIR=~/linux-command-library-dev/data/commands")
    else:
        for cat, n in sorted(per_cat_count.items()):
            print(f"  - {cat}: {n}")
    return commands

def init_command_library() -> List[CommandDoc]:
    return load_all_commands()

# ======================================================================================
# SEARCH HELPERS
# ======================================================================================
def summarize_command(cmd: CommandDoc) -> str:
    name = str(cmd.get("name", "")).strip() or "<unnamed>"
    cat = str(cmd.get("category", ""))
    desc = str(cmd.get("description", "")).strip().replace("\n", " ")
    if len(desc) > 120:
        desc = desc[:117] + "..."
    return f"{name}  [{cat}] — {desc}" if desc else f"{name}  [{cat}]"


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

def _repo_root() -> _Path:
    """Best-effort repo root (parent of commands/ or data/commands)."""
    base = _find_commands_base()
    # .../data/commands  -> repo = .../data/..
    if base.name == "commands":
        return base.parent
    if base.name == "commands" and base.parent.name == "data":
        return base.parent.parent
    if base.parent.name == "data":
        return base.parent.parent
    return base.parent

def _is_admin() -> bool:
    """
    Admin ON if:
      - LCL_ADMIN in {"1","true","yes"}  OR
      - LCL_ADMIN_TOKEN matches contents of <repo>/.lcl_admin_token
    """
    flag = os.getenv("LCL_ADMIN", "").lower()
    if flag in {"1", "true", "yes"}:
        return True
    token_env = os.getenv("LCL_ADMIN_TOKEN")
    if not token_env:
        return False
    token_file = _repo_root() / ".lcl_admin_token"
    try:
        if token_file.is_file() and token_file.read_text(encoding="utf-8").strip() == token_env.strip():
            return True
    except Exception:
        pass
    return False

def _suggestions_dir() -> _Path:
    d = _repo_root() / ".inbox" / "suggestions"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _safe_slug(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return "unnamed"
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in s)[:60]

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

# ======================================================================================
# PIN HELPERS
# ======================================================================================
PINS_PATH = _Path(".pins.json")


def _load_pins() -> set[str]:
    try:
        if PINS_PATH.exists():
            return set(json.loads(PINS_PATH.read_text()))
    except Exception:
        pass
    return set()


def _save_pins(pins: set[str]):
    PINS_PATH.write_text(json.dumps(sorted(pins), indent=2))

# ======================================================================================
# MARKDOWN EXPORT
# ======================================================================================
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
                    if isinstance(e.get("explain"), list):
                        for line in e["explain"]:
                            lines.append(f"- {line}")
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

# ======================================================================================
# INLINE VALIDATION + SAVE HELPERS (used by the New Command UI)
# ======================================================================================

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
#=====================================================================================
# DIALOG SCREENS (New Command, Menu, About, Help, Quiz, Explain, Suggest)
# ======================================================================================

#---------NEW Command Screen (admin only) ---------
class NewCommandScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    Screen { width: 90%; height: 90%; align: center middle; }
    #title    { width: 100%; content-align: center middle; margin-bottom: 1; }
    #editor   { height: 1fr; }
    #buttons  { height: auto; align: center middle; }
    #msg      { height: auto; color: yellow; padding: 0 1; }
    """
    def compose(self) -> ComposeResult:
        yield Static("New Command (Admin only)", id="title")
        # Big editor area
        if HAVE_TEXTAREA:
            self._editor = TextArea(id="editor")
        else:
            self._editor = Input(placeholder="Paste YAML here…", id="editor")  # type: ignore
        yield self._editor
        # Buttons
        with Horizontal(id="buttons"):
            yield Button("Validate", id="nc_validate")
            yield Button("Save", id="nc_save")
            yield Button("Cancel", id="nc_cancel")
        yield Static("", id="msg")

    def on_mount(self):
        # Load template if present
        tpl = self._load_template()
        self._set_text(tpl)

    def _load_template(self) -> str:
        # Try to read templates/command_templates.yml
        for root in (_Path.cwd(), _Path(__file__).resolve().parent):
            cand = root / "templates" / "command_templates.yml"
            if cand.is_file():
                try:
                    return cand.read_text(encoding="utf-8")
                except Exception:
                    pass
        # default minimal template
        return (
            "name: \n"
            "category: \n"
            "description: |\n"
            "  \n"
            "usage: \n"
            "# syntax: \n"
            "options: []  # list of {flag, description}\n"
            "examples: [] # list of strings\n"
            "related_commands: []\n"
        )

    def _get_text(self) -> str:
        return getattr(self._editor, "text", None) or getattr(self._editor, "value", "")

    def _set_text(self, text: str) -> None:
        if hasattr(self._editor, "text"):
            self._editor.text = text
        else:
            self._editor.value = text  # type: ignore

    def _set_msg(self, text: str, ok: bool = False):
        msg = self.query_one("#msg", Static)
        msg.update(("[green]✓ " if ok else "[yellow]") + text)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id or ""
        if bid == "nc_cancel":
            self.dismiss(None)
            return

        raw = self._get_text()
        try:
            data = yaml.safe_load(raw)
        except Exception as e:
            self._set_msg(f"YAML parse error: {e}")
            return

        if not isinstance(data, dict):
            self._set_msg("Top-level must be a mapping (YAML dict).")
            return

        if bid == "nc_validate":
            issues = _validate_doc_minimal(data)
            if issues:
                self._set_msg("Validation issues:\n- " + "\n- ".join(issues))
            else:
                self._set_msg("Valid ✔", ok=True)

        elif bid == "nc_save":
            issues = _validate_doc_minimal(data)
            if issues:
                self._set_msg("Fix before save:\n- " + "\n- ".join(issues))
                return
            ok, msg = _save_new_command(data)
            if ok:
                # Reload and close
                self.app.reload_from_disk()
                self._set_msg(f"Saved to {msg}", ok=True)
                self.dismiss(None)
            else:
                self._set_msg(msg)

#---------MENU Screen (all users) ---------
class MenuScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    Screen {
        width: 48;
        align: center middle;
        padding: 1 0;
    }
    .title { width: 100%; content-align: center middle; margin-bottom: 1; }
    #menu_stack { align: center middle; }
    #menu_stack > Button { width: 36; margin: 1 0; content-align: center middle; }
    """
    def compose(self) -> ComposeResult:
        yield Static("Menu", classes="title")
        with Vertical(id="menu_stack"):
            # Everyone can suggest
            yield Button("Suggest a command", id="menu_suggest")
            yield Button("Reload commands", id="menu_reload")
            yield Button("Help", id="menu_help")
            yield Button("Explain box", id="menu_explain")
            yield Button("Quiz (current selection)", id="menu_quiz")
            yield Button("About", id="menu_about")
            # Admin-only "New Command"
            if getattr(self.app, "is_admin", False):  # type: ignore
                yield Button("New Command (admin)", id="menu_new")
            yield Button("Quit", id="menu_quit")
            yield Button("Close", id="menu_close")

    def on_button_pressed(self, event: Button.Pressed):
        bid = (event.button.id or "")
        app: CommandApp = self.app  # type: ignore

        if bid == "menu_close":
            self.dismiss(None)
        elif bid == "menu_quit":
            app.exit()
        elif bid == "menu_reload":
            app.reload_from_disk(); app.status.update("Commands reloaded from disk"); self.dismiss(None)
        elif bid == "menu_help":
            app.push_screen(HelpScreen()); self.dismiss(None)
        elif bid == "menu_explain":
            app.action_open_explain(); self.dismiss(None)
        elif bid == "menu_quiz":
            app.action_open_quiz(); self.dismiss(None)
        elif bid == "menu_about":
            app.push_screen(AboutScreen()); self.dismiss(None)
        elif bid == "menu_suggest":
            app.push_screen(SuggestCommandScreen()); self.dismiss(None)
        elif bid == "menu_new":
            if app.is_admin:
                app.push_screen(NewCommandScreen()); self.dismiss(None)
            else:
                app.status.update("Admin only. Set LCL_ADMIN=1 or provide a valid LCL_ADMIN_TOKEN.")

#---------ABOUT Screen (all users) ---------
ABOUT_MD = """
# Linux Command Library — About

I built *Linux Command Library* to transform a static cheatsheet into a living, interactive way to learn Bash.
I am ShadoVaine, and my goal was to create a TUI (Text User Interface) that runs directly inside a Bash terminal.
The Library contains over 180 Linux commands, all organized by category. Users can search by name, category, description,
 or even by specific options.
As I worked to become more proficient in Linux, I wanted to create a resource that would help others learn alongside me.
My hope is that the Linux Command Library supports you on your own journey.

## What it does
- Curated commands organized by category
- Examples, usage/syntax, options (with meanings)
- Fast fuzzy search
- Add new commands with a form
- Quizzes & an Explain box (beta)

## Keys
{keys_md}

*Remain curious. Learn daily.*
"""

def _keys_markdown(app: "CommandApp") -> str:
    lines = []
    for key, action, desc in app.BINDINGS:
        if key and desc:
            lines.append(f"- `{key}` — {desc}")
    return "\n".join(lines)

class AboutScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        text = ABOUT_MD.replace("{keys_md}", _keys_markdown(self.app))
        try:
            yield MarkdownViewer(text, show_table_of_contents=False)
        except TypeError:
            # Older Textual: Markdown widget doesn’t accept show_table_of_contents
            yield MarkdownViewer(text)
        yield Button("close", id="about_close")

    def on_button_pressed(self, ev: Button.Pressed):
        if (ev.button.id or "") == "about_close":
            self.dismiss(None)

#---------HELP Screen (all users) ---------
HELP_MD = """
# Help

**Search**
- Type in the box then press **Enter** to filter
- Results grouped by category; ↑/↓ to move, Enter to show details

**Common Keys**
- `/` focus search, `m` menu, `q` quit, `esc` clear search
- `o` open the YAML in $EDITOR
- `e` export current command to Markdown
- `p` pin/unpin favorites
- `g` quiz me on the current command
- `x` explain a command I type
"""
class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        try:
            yield MarkdownViewer(HELP_MD, show_table_of_contents=False)
        except TypeError:
            # Older Textual: Markdown widget doesn’t accept show_table_of_contents
            yield MarkdownViewer(HELP_MD)
        yield Button("close", id="help_close")

    def on_button_pressed(self, ev: Button.Pressed):
        if (ev.button.id or "") == "help_close":
            self.dismiss(None)

#---------QUIZ Screen (all users) ---------
class QuizScreen(ModalScreen[None]):
    def __init__(self, cmd: dict | None):
        super().__init__()
        self._cmd = cmd

    def compose(self) -> ComposeResult:
        name = (self._cmd.get("name") or self._cmd.get("command")) if self._cmd else "<none>"
        syntax = self._cmd.get("syntax") or self._cmd.get("usage") if self._cmd else ""
        prompt = f"# Quiz: {name}\n\nType the correct syntax and press Enter."
        yield MarkdownViewer(prompt, show_table_of_contents=False)
        yield Input(placeholder="Your answer…", id="quiz_input")
        with Horizontal():
            yield Button("Check", id="quiz_check")
            yield Button("Close", id="quiz_close")
        yield Static("", id="quiz_msg")

    def on_button_pressed(self, ev: Button.Pressed):
        bid = ev.button.id or ""
        if bid == "quiz_close":
            self.dismiss(None)
            return
        if bid == "quiz_check":
            user = self.query_one("#quiz_input", Input).value.strip()
            msg = self.query_one("#quiz_msg", Static)
            syntax = (self._cmd.get("syntax") or self._cmd.get("usage") or "") if self._cmd else ""
            if not syntax:
                msg.update("[yellow]No reference syntax in YAML to check against.[/yellow]")
                return
            ok = user and user in syntax
            if ok:
                msg.update("[green]✔ Looks good![/green]")
            else:
                msg.update(
                    f"[red]✘ Not quite.[/red]\n\n[dim]Expected contains:[/dim]\n```\n{syntax}\n```"
                )

#---------EXPLAIN Screen (all users) ---------
class ExplainScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        yield MarkdownViewer(
            "# Explain a command\nPaste or type a shell command below.", show_table_of_contents=False
        )
        yield Input(placeholder="e.g. cp -r src/ dst/", id="x_input")
        with Horizontal():
            yield Button("Explain", id="x_go")
            yield Button("Close", id="x_close")
        yield Static("", id="x_out")

    def on_button_pressed(self, ev: Button.Pressed):
        bid = ev.button.id or ""
        if bid == "x_close":
            self.dismiss(None)
            return
        if bid == "x_go":
            inp = self.query_one("#x_input", Input).value.strip()
            out = self._explain(inp)
            self.query_one("#x_out", Static).update(out)

    def _explain(self, s: str) -> str:
        if not s:
            return "[yellow]Enter a command first.[/yellow]"
        parts = shlex.split(s)
        out = [f"**Tokens:** {parts}"]
        app: CommandApp = self.app  # type: ignore
        cmd = None
        if app._filtered and app.list_view.index is not None and 0 <= app.list_view.index < len(app._filtered):
            cmd = app._filtered[app.list_view.index]
        if cmd and isinstance(cmd.get("options"), list):
            meanings = []
            for o in cmd["options"]:
                if isinstance(o, dict) and o.get("flag"):
                    for tok in parts:
                        if any(tok == f.strip() for f in str(o["flag"]).split(",")):
                            meanings.append(f"- `{tok}` — {o.get('description', o.get('meaning',''))}")
            if meanings:
                out += ["\n**Flags found:**", *meanings]
        return "\n".join(out)

#---------SUGGEST Command Screen (all users) ---------    
class SuggestCommandScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    Screen { width: 90%; height: 90%; align: center middle; }
    #title    { width: 100%; content-align: center middle; margin-bottom: 1; }
    #msg      { color: yellow; padding: 0 1; }
    #row      { layout: horizontal; height: auto; }
    #row > *  { width: 1fr; margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("Suggest a Command", id="title")
        # simple structured fields
        with Horizontal(id="row"):
            self._name = Input(placeholder="Command name (e.g., rsync)", id="sug_name")
            self._category = Input(placeholder="Category (free text OK)", id="sug_cat")
        self._usage = Input(placeholder="Usage / Syntax (e.g., rsync -av src/ dst/)", id="sug_usage")
        # multi-line description uses TextArea if available
        if HAVE_TEXTAREA:
            self._desc = TextArea(id="sug_desc")
            self._desc.text = "Describe what this command does and why it’s useful..."
        else:
            self._desc = Input(placeholder="Short description…", id="sug_desc")  # type: ignore
        yield self._name
        yield self._category
        yield self._usage
        yield self._desc
        with Horizontal():
            yield Button("Submit", id="sug_submit")
            yield Button("Cancel", id="sug_cancel")
        yield Static("", id="msg")

    def _msg(self, text: str, ok: bool = False):
        self.query_one("#msg", Static).update(("[green]✓ " if ok else "[yellow]") + text)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id or ""
        if bid == "sug_cancel":
            self.dismiss(None)
            return
        if bid == "sug_submit":
            name = self._name.value.strip()
            desc = (getattr(self._desc, "text", None) or getattr(self._desc, "value", "")).strip()
            if not name or not desc:
                self._msg("Please provide at least a name and a description.")
                return
            payload = {
                "name": name,
                "category": self._category.value.strip() or "Unsorted",
                "description": desc,
                "usage": self._usage.value.strip(),
            }
            try:
                path = _save_suggestion(payload)
                self._msg(f"Thanks! Saved to {path}", ok=True)
                self.dismiss(None)
            except Exception as e:
                self._msg(f"Failed to save: {e}")



# ======================================================================================
# ENTRY POINT (works for python, pipx, and PyInstaller)
# ======================================================================================
def main():
    docs = init_command_library()
    print(f"[ok] Loaded {len(docs)} docs total")
    app = CommandApp(docs)
    app.run()


if __name__ == "__main__":
    main()
