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
SEARCH_PLACEHOLDER = "Search by name, category, or option..."

#=========================================================
# Focusable Static Widget
#=========================================================
class FocusableStatic(Static):
    """A Static widget that can receive focus"""
    
    def __init__(self, *args, **kwargs):
        # Disable markup by default to prevent parsing errors
        kwargs.setdefault('markup', False)
        super().__init__(*args, **kwargs)
        # Make this widget focusable
        self.can_focus = True


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
        border: round;
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
        border: round;
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
        border: round;
        padding: 1;
        margin: 0 0 1 0;
    }
    .detail_box_compact {
        border: round;
        padding: 1;
        margin: 0 0 1 0;
        height: 8;
    }
    .detail_box_large {
        border: round;
        padding: 1;
        margin: 0 0 1 0;
        height: 12;
        overflow-y: auto;
    }
    .detail_header {
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
        border: thick;
        background: $accent 20%;
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
                        initial = Static()
                        initial.id = "initial_message"
                        initial.update("Navigate commands with arrow keys to see details.")
                        yield initial

        yield Footer()

    # --------------- Lifecycle ---------------
    def on_mount(self) -> None:
        table = self.query_one("#results", DataTable)
        table.add_columns("Name", "Category", "Description")
        
        # FORCE UPDATE THE PLACEHOLDER TEXT
        search_input = self.query_one("#search_input", Input)
        search_input.placeholder = "Search by name, category, or option..."
        
        search_input.focus()
        
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
            # Don't limit to first 100 - let _apply_filters_and_render handle it
            self._apply_filters_and_render()
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
        # Define the focus order - only include widgets that always exist
        focus_order = [
            "#search_input",
            "#results"
        ]
        
        # Add detail widgets only if they exist
        detail_widgets = [
            "#command_name_focus",
            "#category_focus", 
            "#description_focus",
            "#options_focus",
            "#examples_focus"
        ]
        
        try:
            # Check which detail widgets actually exist
            existing_details = []
            for widget_id in detail_widgets:
                try:
                    self.query_one(widget_id)
                    existing_details.append(widget_id)
                except:
                    pass  # Widget doesn't exist, skip it
            
            # Combine focus order
            full_focus_order = focus_order + existing_details
            
            # Get currently focused widget
            current_focus = self.focused
            current_id = getattr(current_focus, 'id', None)
            
            # Find current position in focus order
            current_index = -1
            for i, widget_id in enumerate(full_focus_order):
                if current_id == widget_id.lstrip('#'):
                    current_index = i
                    break
            
            # Move to next widget (or first if at end)
            next_index = (current_index + 1) % len(full_focus_order)
            next_widget_id = full_focus_order[next_index]
            
            # Focus the next widget
            try:
                next_widget = self.query_one(next_widget_id)
                next_widget.focus()
            except:
                # Fallback to search input if widget not found
                self.query_one("#search_input").focus()
                
        except Exception as e:
            self.log(f"Error in focus_next: {e}")
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
        """Apply search filters and update the display."""
        try:
            search_text = self.query_one("#search_input", Input).value.strip().lower()
            
            if not search_text:
                # Show ALL commands organized by category on startup
                self.filtered_docs = self._get_all_commands_by_category()
            else:
                # Search logic with EXACT MATCH PRIORITY
                self.filtered_docs = []
                exact_matches = []
                partial_matches = []
                
                for doc in self.docs:
                    try:
                        name = str(doc.get("name", "")).lower()
                        category_raw = str(doc.get("category", ""))
                        category = category_raw.lower()
                        category_normalized = category.replace("_", " ")
                        options_text = self._extract_options_text(doc)
                        
                        # 1. EXACT NAME MATCH (highest priority)
                        if search_text == name:
                            exact_matches.append(doc)
                            continue
                        
                        # 2. PARTIAL MATCHES (lower priority)
                        search_words = search_text.split()
                        matches = False
                        
                        for search_word in search_words:
                            if (search_word in name or 
                                search_word in category or 
                                search_word in category_normalized or
                                search_word in options_text):
                                matches = True
                                break
                        
                        # SPECIAL CASE: "networking" should match "network"
                        if "networking" in search_text and ("network" in category or "network" in category_normalized):
                            matches = True
                        
                        if matches:
                            partial_matches.append(doc)
                            
                    except Exception as e:
                        self.log(f"Error processing document {doc.get('name', 'unknown')}: {e}")
                        continue
                
                # PRIORITIZE: If exact matches exist, show only those. Otherwise show partial matches.
                if exact_matches:
                    self.filtered_docs = exact_matches
                else:
                    self.filtered_docs = partial_matches[:50]  # Limit partial matches to 50
            
            # Update table safely
            self._update_results_table()
            
        except Exception as e:
            self.log(f"Error in search: {e}")
            # Fallback - show all commands by category
            self.filtered_docs = self._get_all_commands_by_category()
            self._update_results_table()

    def _update_results_table(self) -> None:
        """Refresh the DataTable '#results' from self.filtered_docs safely."""
        try:
            table = self.query_one("#results", DataTable)
            table.clear()
            
            current_category = None
            
            for doc in (self.filtered_docs or []):
                name = doc.get("name", "")
                category = doc.get("category", "")
                desc = doc.get("description", "") or ""
                short_desc = desc[:50] + "..." if len(desc) > 50 else desc
                
                # Add visual separator for new categories (optional)
                if current_category != category:
                    current_category = category
                    # You could add a separator row here if desired
                    # table.add_row(f"━━━ {category} ━━━", "", "")
                
                table.add_row(name, category, short_desc)
                
        except Exception as e:
            # Log but do not raise to keep UI responsive
            self.log(f"Error updating results table: {e}")

    def _extract_options_text(self, doc: dict) -> str:
        """Safely extract searchable text from options."""
        try:
            options = doc.get("options", [])
            if not options:
                return ""
            
            options_text_parts = []
            
            # Handle different option formats
            if isinstance(options, list):
                for option in options:
                    try:
                        if isinstance(option, dict):
                            # Handle dict format: {"flag": ["-a", "--all"], "explains": "..."}
                            flag = option.get("flag", "")
                            if isinstance(flag, list):
                                # Clean each flag item and skip malformed ones
                                for f in flag:
                                    f_str = str(f).strip()
                                    # Skip entries with malformed syntax
                                    if f_str and not ("']: " in f_str or "']:" in f_str):
                                        options_text_parts.append(f_str.lower())
                            else:
                                f_str = str(flag).strip()
                                # Skip malformed flag entries
                                if f_str and not ("']: " in f_str or "']:" in f_str):
                                    options_text_parts.append(f_str.lower())
                            
                            # Add explanation text too (with safety check)
                            explains = option.get("explains", "")
                            if explains:
                                explains_str = str(explains).strip()
                                # Skip malformed explanations
                                if explains_str and not ("']: " in explains_str or "']:" in explains_str):
                                    options_text_parts.append(explains_str.lower())
                        
                        elif isinstance(option, str):
                            # Handle simple string options
                            option_str = str(option).strip()
                            # Skip malformed string options
                            if option_str and not ("']: " in option_str or "']:" in option_str):
                                options_text_parts.append(option_str.lower())
                        else:
                            # Fallback for unexpected types
                            option_str = str(option).strip()
                            if option_str and not ("']: " in option_str or "']:" in option_str):
                                options_text_parts.append(option_str.lower())
                    except Exception as e:
                        # Log error but continue with next option
                        self.log(f"Error processing option {option}: {e}")
                        continue
                
            elif isinstance(options, dict):
                # Some docs may store options as a dict; include keys and string values
                for k, v in options.items():
                    try:
                        key = str(k).strip()
                        if key and not ("']: " in key or "']:" in key):
                            options_text_parts.append(key.lower())
                        if isinstance(v, str):
                            val = v.strip()
                            if val and not ("']: " in val or "']:" in val):
                                options_text_parts.append(val.lower())
                    except Exception as e:
                        self.log(f"Error processing option entry {k}: {e}")
                        continue
            else:
                # Fallback to string representation
                opts_str = str(options).strip()
                if opts_str and not ("']: " in opts_str or "']:" in opts_str):
                    options_text_parts.append(opts_str.lower())

            return " ".join(options_text_parts)
            
        except Exception as e:
            self.log(f"Error extracting options text: {e}")
            return ""

    # --------------- Details ---------------
    def _update_details(self, doc: Dict[str, Any]) -> None:
        """Update details panel with focusable boxes"""
        try:
            details_content = self.query_one("#details_content")
            details_content.remove_children()

            # Command Name Box (with markup=False)
            command_name_box = Vertical(
                Static("Command Name", classes="detail_header", markup=False),
                FocusableStatic(doc.get("name", "N/A"), classes="detail_content", id="command_name_focus", markup=False),
                classes="detail_box_compact",
                id="command_name_box",
            )
            details_content.mount(command_name_box)

            # Category Box (focusable)
            category_box = Vertical(
                Static("Category", classes="detail_header", markup=False),
                FocusableStatic(doc.get("category", "N/A"), classes="detail_content", id="category_focus", markup=False),
                classes="detail_box_compact",
                id="category_box",
            )
            details_content.mount(category_box)

            # Description Box (focusable)
            description_box = Vertical(
                Static("Description", classes="detail_header", markup=False),
                FocusableStatic(doc.get("description", "N/A"), classes="detail_content", id="description_focus", markup=False),
                classes="detail_box_compact",
                id="description_box",
            )
            details_content.mount(description_box)

            # Options Box (focusable and scrollable) - ADD markup=False HERE
            options_content = self._format_options(doc.get("options", []))
            options_box = Vertical(
                Static("Options with Explanations", classes="detail_header", markup=False),  # ADD THIS
                FocusableStatic(options_content, classes="detail_content", id="options_focus", markup=False),  # ADD THIS
                classes="detail_box_large",
                id="options_box",
            )
            details_content.mount(options_box)

            # Examples Box (focusable and scrollable) - ADD markup=False HERE
            examples_content = self._format_examples(doc.get("examples", []))
            examples_box = Vertical(
                Static("Examples", classes="detail_header", markup=False),  # ADD THIS
                FocusableStatic(examples_content, classes="detail_content", id="examples_focus", markup=False),  # ADD THIS
                classes="detail_box_large",
                id="examples_box",
            )
            details_content.mount(examples_box)

        except Exception as e:
            details_content = self.query_one("#details_content")
            details_content.remove_children()
            error_box = Vertical(
                Static("ERROR", classes="detail_header", markup=False),  # ADD THIS TOO
                Static(f"Error: {str(e)}", classes="detail_content", markup=False),  # ADD THIS TOO
                classes="detail_box"
            )
            details_content.mount(error_box)

    def _format_options(self, options: List[Dict[str, Any]]) -> str:
        """Format options into a readable string for the details pane."""
        try:
            if not options:
                return "No options documented."

            lines: List[str] = []
            
            for option in options:
                if isinstance(option, dict):
                    flag = option.get("flag", "")
                    explains = option.get("explains", "")
                    
                    # Debug: Print problematic content
                    if "']: Use archive file" in str(flag) or "']: Use archive file" in str(explains):
                        print(f"DEBUG: Found problematic content: flag={flag}, explains={explains}")
                    
                    # Format the flag part
                    if isinstance(flag, list):
                        flag_str = ", ".join(str(f) for f in flag)
                    else:
                        flag_str = str(flag)
                    
                    # Format the complete line
                    if explains:
                        lines.append(f"{flag_str}: {explains}")
                    else:
                        lines.append(flag_str)
                        
                elif isinstance(option, str):
                    lines.append(option)
                
            return "\n\n".join(lines)
            
        except Exception as e:
            self.log(f"Error formatting options: {e}")
            return "Error formatting options"

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

    def show_command_details(self, doc: dict) -> None:
        """Display command details in the right panel."""
        try:
            details_content = self.query_one("#details_content", Vertical)
            details_content.remove_children()  # Clear existing content
            
            # Command Name with UNIQUE ID
            name_box = Vertical(
                Static("Command", classes="detail_header"),
                FocusableStatic(doc.get("name", "N/A"), classes="detail_content", id=f"name_focus_{doc.get('name', 'unknown')}", markup=False),
                classes="detail_box_compact",
                id=f"name_box_{doc.get('name', 'unknown')}",
            )
            details_content.mount(name_box)

            # Category with UNIQUE ID
            category_box = Vertical(
                Static("Category", classes="detail_header"),
                FocusableStatic(doc.get("category", "N/A"), classes="detail_content", id=f"category_focus_{doc.get('name', 'unknown')}", markup=False),
                classes="detail_box_compact",
                id=f"category_box_{doc.get('name', 'unknown')}",
            )
            details_content.mount(category_box)

            # Description with UNIQUE ID
            description_box = Vertical(
                Static("Description", classes="detail_header"),
                FocusableStatic(doc.get("description", "N/A"), classes="detail_content", id=f"description_focus_{doc.get('name', 'unknown')}", markup=False),
                classes="detail_box",
                id=f"description_box_{doc.get('name', 'unknown')}",
            )
            details_content.mount(description_box)

            # Options with UNIQUE ID
            options = doc.get("options", [])
            if options:
                options_box = self._render_options_section(options, doc.get('name', 'unknown'))
                details_content.mount(options_box)

            # Examples with UNIQUE ID
            examples = doc.get("examples", [])
            if examples:
                examples_box = self._render_examples_section(examples, doc.get('name', 'unknown'))
                details_content.mount(examples_box)

        except Exception as e:
            self.log(f"Error showing command details: {e}")
            # Show error in details panel
            try:
                details_content = self.query_one("#details_content", Vertical)
                details_content.remove_children()
                error_box = Vertical(
                    Static("Error", classes="detail_header"),
                    Static(f"Failed to load details: {e}", classes="detail_content"),
                    classes="detail_box",
                    id="error_box",
                )
                details_content.mount(error_box)
            except Exception:
                pass

    def _render_options_section(self, options: list, command_name: str) -> Vertical:
        """Render the options section with unique IDs."""
        try:
            options_content = []
            
            for i, option in enumerate(options):
                if isinstance(option, dict):
                    flag = option.get("flag", "")
                    explains = option.get("explains", "")
                    
                    if flag and explains:
                        flag_str = ", ".join(flag) if isinstance(flag, list) else str(flag)
                        option_text = f"{flag_str}: {explains}"
                        options_content.append(option_text)
            
            content_text = "\n".join(options_content) if options_content else "No options available"
            
            return Vertical(
                Static("Options", classes="detail_header"),
                FocusableStatic(content_text, classes="detail_content", id=f"options_focus_{command_name}_{hash(content_text) % 10000}", markup=False),
                classes="detail_box_large",
                id=f"options_box_{command_name}",
            )
            
        except Exception as e:
            return Vertical(
                Static("Options", classes="detail_header"),
                Static(f"Error loading options: {e}", classes="detail_content"),
                classes="detail_box",
                id=f"options_error_{command_name}",
            )

    def _render_examples_section(self, examples: list, command_name: str) -> Vertical:
        """Render the examples section with unique IDs."""
        try:
            examples_text = "\n\n".join(str(ex) for ex in examples if ex)
            
            return Vertical(
                Static("Examples", classes="detail_header"),
                FocusableStatic(examples_text, classes="detail_content", id=f"examples_focus_{command_name}_{hash(examples_text) % 10000}", markup=False),
                classes="detail_box_large",
                id=f"examples_box_{command_name}",
            )
            
        except Exception as e:
            return Vertical(
                Static("Examples", classes="detail_header"),
                Static(f"Error loading examples: {e}", classes="detail_content"),
                classes="detail_box",
                id=f"examples_error_{command_name}",
            )

    def _get_all_commands_by_category(self) -> list:
        """Return all commands organized by category."""
        try:
            # Group commands by category
            category_groups = {}
            
            for doc in self.docs:
                category = doc.get("category", "Unknown")
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(doc)
            
            # Sort categories alphabetically and combine all commands
            organized_commands = []
            
            for category in sorted(category_groups.keys()):
                # Sort commands within each category by name
                commands_in_category = sorted(category_groups[category], 
                                            key=lambda x: x.get("name", "").lower())
                organized_commands.extend(commands_in_category)
            
            return organized_commands
            
        except Exception as e:
            self.log(f"Error organizing commands by category: {e}")
            # Fallback to original order
            return self.docs.copy()


#=========================================================
# Entry Point
#=========================================================
def main() -> None:
    """Main entry point for the application."""
    app = CommandApp()
    app.run()


if __name__ == "__main__":
    main()