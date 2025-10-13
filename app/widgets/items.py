#===================================================
# Command List Item
#===================================================

#------------------Standard Library-------------------
from typing import Any, Dict
#------------------Textual UI-------------------
from textual.widgets import ListItem, Label

#------------------Local-------------------
from ..search import summarize_command

#------------------Command List Item-------------------
class CommandListItem(ListItem):
    """List item that renders a command summary, with optional star for pins."""
    def __init__(self, cmd: Dict[str, Any], pinned: bool = False):
        self.cmd = cmd
        label = summarize_command(cmd)
        if pinned:
            label = "★ " + label
        super().__init__(Label(label))