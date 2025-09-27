
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from pathlib import Path
from rapidfuzz import fuzz
import yaml
import textwrap

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "commands"

def _infer_category(yml_paht: Path) -> str:
    rel = yml_path.relative_to(DATA_DIR)
    return re.parts[0] if len(rel.parts) > 1 else "Misc"

def load_yaml_commands():
    items = []
    for yml in DATA_DIR.rglob("*.yml"):
        with open(yml, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        doc.setdefault("category", _infer_category(yml))
        doc["_path"] = str(yml)
        items.append(doc)
    return items

class CommandDetail(Static):
    def show(self, c: dict | None):
        if not c:
            self.update("No command selected."); return
        parts = []
        title = f"# {c.get('command')} - {c.get('summary','')}"
        if c.get("risk") == "dangerous":
            title += "\n\n[bold red] Dangerous: review before running[/bold red]"
        parts.append(title)
        parts.append(f"\n**Syntax**\n\n`{c.get('syntax','')}`")
        opts = c.get("options", [])
        if opts:
            parts.append("\n**Options**")
            for o in opts:
                parts.append(f"- `{o.get('flag','')}` - {o.get('meaning','')}")
        exs = c.get("Examples", [])
        if exs:
            parts.append("\n**Examples**")
            for e in exs:
                parts.append(f"- {e.get('description','')}\n\n  ```bash\n  {e.get('cmd','')}\n  ```")
                if isinstance(e.get("explain"), list) and e["explain"]:
                    for line in e["explain"]:
                        part.append(f"     -  {line}")
        notes = c.get("notes", [])
        if notes:
            parts.append("\n**Notes**")
            for n in notes:
                parts.append(f"- {n}")
        tags = c.get("tags", [])
        if tags:
            parts.append(f"\n[dim]tags:  {', '.join(tags)}[/dim]")
        self.update("\n".join(parts))

class LibraryApp(App):
    CSS = """
    Screen { layout: vertical; }
   #top { layout: horizontal; height: 3; }
    #main { layout: horizontal; }
    #left { width: 36; overflow: auto; border: solid $primary; }
    #right { overflow: auto; padding: 1; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("c", "copy_example", "Copy Example"),
        ("r", "reload", "Reload"),
        ("d", "toggle_dangerous", "Show/Hide Dangerous"),
    ]

    search = reactive("")
    show_dangerous = reactive(True)
    commands: list[dict] = []
    filtered: list[dict]  = []
    selected: dict | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="top"):
            yield Input(placeholder="Type / to search (name, tags, summary)…", id="search")
        with Horizontal(id="main"):
            with Vertical(id="left"):
                self.list = ListView(id="cmd_list")
                yield self.list
            self.detail = CommandDetail(id="right")
            yield self.detail
        yield Footer()

    def on_mount(self):
        self.load()
        self.refresh_list()

    def load(self):
        self.commands = load_yaml_commands()
        self.filtered = self.commands

    def refresh_list(self):
        self.list.clear()
	# group by category; insert non-interactive headers
        by_cat = {}
        for c in self.filtered:
            by_cat.setdefault(c.get("category","Misc"), []).append(c)

        for cat in sorted(by_cat.keys(), key=str.lower):
	    # category header (disabled ListItem)
            header = ListItem(Label(f"[b]{cat}[/b]"))
            header = disabled = True
            self.list.append(header)
            for c in sorted(self._apply_filter(by_cat[cat]), key=lambda x: x.get("command","")):
                label = c.get("command","<cmd>")
                if c.get("risk") == "dangerous":
                    label += " [red]⁂[/red]"
                item = ListItem(Label(label))
                # stash the command dict on the item for retrieval
                item.data = c # Textual attaches arbitrary attrs cleanly
                self.list.append(item)

    def action_focus_search(self):
        self.query_one("#search", Input).focus()

    def action_reload(self):
        self.load(); self.refresh_list()

    def action_toggle_dangerous(self):
        self.show_dangerous = not self.show_dangerous
        self.refresh_list()
        self.toast("Showing dangerous" if self.show_dangerous else "Hiding dangerous")

    def on_input_changed(self, event: Input.Changed):
        q = event.value.lower().strip()
        if not q:
            self.filtered = self.commands
        else:
            def key(c):
                return " ".join([
                    c.get("command",""),
                    c.get("summary",""),
                    c.get("category",""),
                    " ".join(c.get("tags",[]))
                ]).lower()
            scored = [(fuzz.partial_ratio(q, key(c)), c) for c in self.commands]
            self.filtered = [c for s,c in scored if s > 30]
        self.refresh_list()

    # Fires when you press Enter on a ListItem or click it
    def on_list_view__selected(self, event: ListView.Selected):
        if hasattr(event.item, "data") and isinstance(event.item.data, dict):
            self.selected = event.item.data
            self.detail.show(self.selected)
        else:
           # ignore clicks on disabled category headers
           pass

    def action_copy_example(self):
        # Copies the first example to clipboard (Textual has clipboard support on many terminals)
        if self.selected and self.selected.get("examples"):
            cmd = self.selected["examples"][0].get("cmd","")
            if cmd:
                try:
                    self.copy(cmd)
                    self.toast(f"Copied example: {cmd[:64]}…")
                except Exception:
                    self.toast("Clipboard not available in this terminal.")
                return

if __name__ == "__main__":
    LibraryApp().run()
