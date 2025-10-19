#=========================================================
# Command Application (Textual TUI) - Fixed Version
#=========================================================

from __future__ import annotations

# ---------------- Standard Library ----------------
from typing import Any, Dict, List, Optional
import sys
import traceback
from pathlib import Path

# ---------------- Third-Party ----------------
# Textual UI
from textual.app import App, ComposeResult
from textual.widgets import Input, Static, DataTable, Footer, Label, Button
from textual.containers import Horizontal, Vertical

# ---------------- Local Imports ----------------
from .models import STRICT_CATEGORIES, ALLOWED_CATEGORIES
from .screens.menu import MenuScreen

#=========================================================
# Configuration
#=========================================================
SEARCH_PLACEHOLDER = "Search by name, category, description, or option…"

#=========================================================
# Main TUI Application
#=========================================================
class CommandApp(App):
    """Textual application for the Linux Command Library."""
    
    # Force blue accent colors
    CSS = """
    Screen {
        layout: vertical;
    }

    #top_bar {
        height: 3;
        padding: 0 1;
        content-align: left middle;
    }
    #search_input {
        width: 1fr;
    }
    #results_section {
        width: 50%;
        layout: vertical;
        border: round #0178d4;  /* Force blue border */
        padding: 1;
        height: 1fr;
    }
    #results_title {
        height: 1;
        content-align: center middle;
        text-style: bold;
    }
    #results {
        height: 1fr;
    }
    #body {
        height: 1fr;
        width: 100%;
        layout: horizontal;
    }
    #details_section {
        width: 50%;
        layout: vertical;
        border: round #0178d4;  /* Force blue border */
        padding: 1;
        height: 1fr;
    }
    #details_title {
        height: 1;
        content-align: center middle;
        text-style: bold;
    }
    #details_content {
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    .detail_box {
        border: round #0178d4;  /* Force blue border */
        padding: 1;
        margin: 0 0 1 0;
    }
    .detail_box_compact {
        border: round #0178d4;  /* Force blue border */
        padding: 1;
        margin: 0 0 1 0;
        height: 8;
    }
    .detail_box_large {
        border: round #0178d4;  /* Force blue border */
        padding: 1;
        margin: 0 0 1 0;
        height: 12;
        overflow-y: auto;
    }
    .detail_header {
        background: #0178d4;    /* Force blue header background */
        color: white;
        text-style: bold;
        height: 1;
        content-align: left middle;
        padding: 0 1;
    }
    .detail_content {
        height: auto;
        padding: 1;
        background: $surface;
    }

    /* Focus styles for tab navigation */
    .detail_content:focus {
        border: thick #0178d4;     /* Force blue focus border */
        background: #0178d4 20%;   /* Force blue focus background */
    }

    #search_input:focus {
        border: thick #0178d4;     /* Force blue focus border */
    }

    #results:focus {
        border: thick #0178d4;     /* Force blue focus border */
    }
    """
    
    BINDINGS = [
        ("m", "open_menu", "m: MENU"),      # lowercase m, uppercase MENU
        ("r", "reload_data", "r: RELOAD"),  # lowercase r, uppercase RELOAD  
        ("q", "quit", "q: QUIT"),           # lowercase q, uppercase QUIT
        ("tab", "focus_next", "tab: next"),
        ("shift+tab", "focus_previous", "shift+tab: prev"),
    ]
    
    def __init__(self) -> None:
        super().__init__()
        # Remove: self.dark = True  # DELETE THIS LINE
        self.docs: List[Dict[str, Any]] = []
        self.filtered_docs: List[Dict[str, Any]] = []
        self._search_performed: bool = False

    # --------------- Compose UI ---------------
    def compose(self) -> ComposeResult:
        with Horizontal(id="top_bar"):
            search_input = Input(
                placeholder=SEARCH_PLACEHOLDER,
            )
            search_input.id = "search_input"
            yield search_input

        with Horizontal(id="body"):
            with Vertical(id="results_section"):
                yield Label("Commands", id="results_title")
                yield DataTable(id="results")
            
            with Vertical(id="details_section"):
                yield Label("Details", id="details_title")
                with Vertical(id="details_content"):
                    yield Static("Navigate commands with arrow keys to see details.", id="initial_message")

        yield Footer()

    # --------------- Lifecycle ---------------
    def on_mount(self) -> None:
        table = self.query_one("#results", DataTable)
        table.add_columns("Name", "Category", "Description")
        self.query_one("#search_input", Input).focus()
        
        # Ensure footer bindings are visible from start
        self.refresh_bindings()
        
        self.load_data()

        # Focus first button when menu opens.
        try:
            # Focus the first button (Help)
            help_button = self.query_one("#menu_help", Button)
            help_button.focus()
        except:
            # Fallback - just ensure something is focused
            pass

    def load_data(self) -> None:
        """Load YAML data"""
        from .yamlio import load_all_commands
        self.docs = load_all_commands()
        
        if self.docs:
            table = self.query_one("#results", DataTable)
            table.clear()
            for doc in self.docs[:100]:  
                table.add_row(
                    doc.get("name", ""),
                    doc.get("category", ""),
                    doc.get("description", "")[:50] + "..." if len(doc.get("description", "")) > 50 else doc.get("description", "")
                )
            self.filtered_docs = self.docs[:100].copy()
        else:
            # If no docs loaded, show empty table
            table = self.query_one("#results", DataTable)
            table.clear()
            self.filtered_docs = []

    # --------------- Events ---------------
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search"""
        if event.input.id == "search_input":
            self._search_performed = True
            self._apply_filters_and_render()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """When row is highlighted with arrow keys"""
        if self.filtered_docs and 0 <= event.cursor_row < len(self.filtered_docs):
            doc = self.filtered_docs[event.cursor_row]
            self._update_details(doc)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """When row is selected with Enter key"""
        table = self.query_one("#results", DataTable)
        row_index = table.cursor_row
        if self.filtered_docs and 0 <= row_index < len(self.filtered_docs):
            doc = self.filtered_docs[row_index]
            self._update_details(doc)

    # Add explicit key handling for Enter
    def on_key(self, event) -> None:
        """Handle key presses"""
        if event.key == "enter":
            # Check if we're focused on the results table
            table = self.query_one("#results", DataTable)
            if self.focused == table and self.filtered_docs:
                row_index = table.cursor_row
                if 0 <= row_index < len(self.filtered_docs):
                    doc = self.filtered_docs[row_index]
                    self._update_details(doc)

    # --------------- Actions ---------------
    def action_open_menu(self) -> None:
        """Open the menu screen"""
        try:
            self.push_screen(MenuScreen())
        except Exception:
            # If menu screen fails, just continue
            pass

    def action_reload_data(self) -> None:
        """Reload data"""
        self.load_data()

    def action_focus_next(self) -> None:
        """Custom tab navigation through specific widgets"""
        # Define the focus order
        focus_order = [
            "#search_input",
            "#results", 
            "#command_name_focus",
            "#category_focus",
            "#description_focus", 
            "#options_focus",
            "#examples_focus"
        ]
        
        try:
            # Get currently focused widget
            current_focus = self.focused
            current_id = getattr(current_focus, 'id', None)
            
            # Find current position in focus order
            current_index = -1
            for i, widget_id in enumerate(focus_order):
                if current_id == widget_id.lstrip('#'):
                    current_index = i
                    break
            
            # Move to next widget (or first if at end)
            next_index = (current_index + 1) % len(focus_order)
            next_widget_id = focus_order[next_index]
            
            # Focus the next widget
            try:
                next_widget = self.query_one(next_widget_id)
                next_widget.focus()
            except:
                # Fallback to search input if widget not found
                self.query_one("#search_input").focus()
                
        except Exception:
            # Fallback to search input
            self.query_one("#search_input").focus()

    def action_focus_previous(self) -> None:
        """Reverse tab navigation"""
        focus_order = [
            "#search_input",
            "#results",
            "#command_name_focus", 
            "#category_focus",
            "#description_focus",
            "#options_focus", 
            "#examples_focus"
        ]
        
        try:
            current_focus = self.focused
            current_id = getattr(current_focus, 'id', None)
            
            current_index = -1
            for i, widget_id in enumerate(focus_order):
                if current_id == widget_id.lstrip('#'):
                    current_index = i
                    break
            
            # Move to previous widget (or last if at beginning)
            prev_index = (current_index - 1) % len(focus_order)
            prev_widget_id = focus_order[prev_index]
            
            try:
                prev_widget = self.query_one(prev_widget_id)
                prev_widget.focus()
            except:
                self.query_one("#search_input").focus()
                
        except Exception:
            self.query_one("#search_input").focus()

    # --------------- Filtering ---------------
    def _apply_filters_and_render(self) -> None:
        """Apply search filters with enhanced category, description, and options search"""
        query = self.query_one("#search_input", Input).value.strip().lower()
        
        if not query:
            self.filtered_docs = self.docs[:100].copy()
        else:
            # 1. Exact command name match (highest priority)
            exact_matches = [doc for doc in self.docs if doc.get("name", "").strip().lower() == query]
            
            if exact_matches:
                self.filtered_docs = exact_matches
            else:
                # 2. Multi-field search (name, category, description, options)
                matches = []
                
                for doc in self.docs:
                    found = False
                    
                    # Search in command name (partial match)
                    if query in doc.get("name", "").lower():
                        matches.append(doc)
                        continue
                    
                    # Search in category (exact and partial)
                    category = doc.get("category", "").lower()
                    if query == category or query in category.replace("_", " ").replace("-", " "):
                        matches.append(doc)
                        continue
                    
                    # Search in description (partial match)
                    description = doc.get("description", "").lower()
                    if query in description:
                        matches.append(doc)
                        continue
                    
                    # Search in options/flags (FIXED VERSION)
                    options = doc.get("options", [])
                    if isinstance(options, list):
                        for option in options:
                            if isinstance(option, dict):
                                # Search in flag name - handle both list and string
                                flag_data = option.get("flag", "")
                                flag_text = ""
                                
                                if isinstance(flag_data, list):
                                    # Join list of flags: ['-k', '--keep'] -> '-k --keep'
                                    flag_text = " ".join(str(f) for f in flag_data).lower()
                                else:
                                    # Single flag string
                                    flag_text = str(flag_data).lower()
                                
                                if query in flag_text:
                                    matches.append(doc)
                                    found = True
                                    break
                                
                                # Search in flag explanation
                                explains = option.get("explains", "").lower()
                                if query in explains:
                                    matches.append(doc)
                                    found = True
                                    break
                    
                    if found:
                        continue
                
                self.filtered_docs = matches[:100]  # Limit results
        
        # Update table
        table = self.query_one("#results", DataTable)
        table.clear()
        for doc in self.filtered_docs:
            description = doc.get("description", "")
            truncated_desc = description[:50] + "..." if len(description) > 50 else description
            table.add_row(
                doc.get("name", ""),
                doc.get("category", ""),
                truncated_desc
            )
        
        # Auto-focus on first result if any
        if self.filtered_docs and table.row_count > 0:
            table.move_cursor(row=0)
            # Show details for first result
            self._update_details(self.filtered_docs[0])

    # --------------- Details ---------------
    def _update_details(self, doc: Dict[str, Any]) -> None:
        """Update details panel with focusable boxes"""
        try:
            details_content = self.query_one("#details_content")
            details_content.remove_children()

            # Command Name Box (focusable)
            command_name_box = Vertical(
                Static("Command Name", classes="detail_header"),
                FocusableStatic(doc.get("name", "N/A"), classes="detail_content", id="command_name_focus"),
                classes="detail_box_compact",
                id="command_name_box",
            )
            details_content.mount(command_name_box)

            # Category Box (focusable)
            category_box = Vertical(
                Static("Category", classes="detail_header"),
                FocusableStatic(doc.get("category", "N/A"), classes="detail_content", id="category_focus"),
                classes="detail_box_compact",
                id="category_box",
            )
            details_content.mount(category_box)

            # Description Box (focusable)
            description_box = Vertical(
                Static("Description", classes="detail_header"),
                FocusableStatic(doc.get("description", "N/A"), classes="detail_content", id="description_focus"),
                classes="detail_box_compact",
                id="description_box",
            )
            details_content.mount(description_box)

            # Options Box (focusable and scrollable)
            options_content = self._format_options(doc.get("options", []))
            options_box = Vertical(
                Static("Options with Explanations", classes="detail_header"),
                FocusableStatic(options_content, classes="detail_content", id="options_focus"),
                classes="detail_box_large",
                id="options_box",
            )
            details_content.mount(options_box)

            # Examples Box (focusable and scrollable)
            examples_content = self._format_examples(doc.get("examples", []))
            examples_box = Vertical(
                Static("Examples", classes="detail_header"),
                FocusableStatic(examples_content, classes="detail_content", id="examples_focus"),
                classes="detail_box_large",
                id="examples_box",
            )
            details_content.mount(examples_box)

        except Exception as e:
            details_content = self.query_one("#details_content")
            details_content.remove_children()
            error_box = Vertical(
                Static("ERROR", classes="detail_header"),
                Static(f"Error: {str(e)}", classes="detail_content"),
                classes="detail_box"
            )
            details_content.mount(error_box)

    def _format_options(self, options: List[Dict[str, Any]]) -> str:
        """Format options into a readable string for the details pane."""
        if not options:
            return "No options documented."

        lines: List[str] = []
        # If options is a dict (sometimes), normalize to list
        if isinstance(options, dict):
            # try to iterate key/value pairs
            for k, v in options.items():
                lines.append(str(k))
                if v:
                    lines.append(f"  {v}")
            return "\n".join(lines)

        if not isinstance(options, list):
            return str(options)

        for opt in options:
            if isinstance(opt, dict):
                flag_data = opt.get("flag", "")
                explains = opt.get("explains", "") or opt.get("explain", "") or ""
                # Normalize flag(s)
                if isinstance(flag_data, list):
                    flag_text = " ".join(str(f) for f in flag_data)
                else:
                    flag_text = str(flag_data)
                flag_text = flag_text.strip()
                if flag_text:
                    lines.append(flag_text)
                if explains:
                    # Preserve multi-line explanations
                    expl_lines = str(explains).splitlines()
                    for ex in expl_lines:
                        lines.append(f"  {ex}")
                else:
                    lines.append("  (no explanation)")
            else:
                # Plain string entry
                lines.extend(str(opt).splitlines())

            # separator between options for readability
            lines.append("")

        # remove trailing empty line if present
        if lines and lines[-1] == "":
            lines.pop()

        return "\n".join(lines)

    def _format_examples(self, examples: Any) -> str:
        """Format examples into a readable string for the details pane."""
        if not examples:
            return "No examples available."
        if isinstance(examples, str):
            return examples
        if isinstance(examples, dict):
            # Join key: value pairs
            parts: List[str] = []
            for k, v in examples.items():
                parts.append(f"{k}: {v}")
            return "\n\n".join(parts)
        if isinstance(examples, list):
            parts: List[str] = []
            for ex in examples:
                if isinstance(ex, dict):
                    # Flatten dict example
                    parts.append(" ".join(f"{k}={v}" for k, v in ex.items()))
                else:
                    parts.append(str(ex))
            return "\n\n".join(parts)
        return str(examples)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        from .config import is_admin
        return is_admin()

    def reload_from_disk(self) -> None:
        """Reload commands from disk - alias for load_data."""
        self.load_data()

    async def load_commands(self) -> None:
        """Async version of load_data for compatibility."""
        self.load_data()


#=========================================================
# Focusable Static Widget
#=========================================================
class FocusableStatic(Static):
    """A Static widget that can receive focus"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make this widget focusable
        self.can_focus = True


#=========================================================
# Entry Point
#=========================================================
def main() -> None:
    """Main entry point for the application."""
    app = CommandApp()
    app.run()


if __name__ == "__main__":
    main()

#=========================================================
# Menu Screen Enhancements
#=========================================================
async def on_button_pressed(self, event: Button.Pressed) -> None:
    """Handle button presses."""
    bid = event.button.id
    app = self.app

    if bid == "menu_close":
        self.dismiss(None)
    elif bid == "menu_help":
        from .screens.help import HelpScreen
        app.push_screen(HelpScreen())
    elif bid == "menu_about":
        from .screens.about import AboutScreen
        app.push_screen(AboutScreen())
    elif bid == "menu_new":
        # Use your existing template
        self.dismiss(None)  # Close menu first
        self._open_command_template()

def _open_command_template(self) -> None:
    """Open the existing command template for editing."""
    try:
        # Path to your existing template
        template_path = Path("templates/command_template.yml")
        
        if not template_path.exists():
            self.app.notify("Template not found at templates/command_template.yml", severity="error")
            return
        
        # Create a copy for new command
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_command_path = Path(f"templates/new_command_{timestamp}.yml")
        
        # Copy template to new file
        import shutil
        shutil.copy2(template_path, new_command_path)
        
        self.app.notify(f"New command template created: {new_command_path}")
        
        # Try to open in editor
        self._open_in_editor(new_command_path)
        
    except Exception as e:
        self.app.notify(f"Error creating command template: {e}", severity="error")

def _open_in_editor(self, file_path: Path) -> None:
    """Try to open file in available text editor."""
    import subprocess
    import os
    
    # List of editors to try (in order of preference)
    editors = [
        os.getenv('EDITOR'),  # User's preferred editor
        'nano',               # Usually available on Linux
        'vim',               # Common on Linux
        'gedit',             # GUI editor
        'code',              # VS Code
        'kate',              # KDE editor
    ]
    
    for editor in editors:
        if editor is None:
            continue
            
        try:
            # Check if editor exists
            subprocess.run(['which', editor], check=True, capture_output=True)
            
            # Open the file
            subprocess.Popen([editor, str(file_path)])
            
            self.app.notify(f"Opening template in {editor}")
            return
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # If no editor found, just show the path
    self.app.notify(f"Please edit manually: {file_path}")