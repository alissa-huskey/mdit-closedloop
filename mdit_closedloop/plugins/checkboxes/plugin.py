"""Rule to process inline items that contain checkboxes."""

from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore

from mdit_closedloop.plugins.checkboxes.parser import Parser


def checkboxes_plugin(md: MarkdownIt) -> None:
    """Parse task/todo checkboxes in list items.

    The behavior of this plugin is almost exactly like the
    mdit-py-plugins/tasklists plugin, except it will find checkboxes that
    contain any single character (not just " " and "x"), and instead of
    creating tokens with HTML "<input>" content, it creates checkbox tokens and
    leaves the content alone.

    - Adds the class "contains-task-list" to the bulleted or numbered list
    - Adds the class "task-list-item" to the list item
    - Remove the checkbox from the inline token content
    - Adds three children to the inline token
        - type: "begin_checkbox"
        - type: "checkbox_mark"
        _ type: "end_checkbox"

    Example

       - [ ] An item that needs doing
       - [.] An pending item
       - [x] An item that is complete

    Syntax

        - Must be in a list item
        - Must start with ``[n]``, where ``n`` is any single character.
    """

    def rule(state: StateCore) -> None:
        """Parse tokens and modify the inline tokens that contain checkboxes."""
        tokens = state.tokens
        parser = Parser(tokens)
        parser.parse()

    md.core.ruler.after("inline", "checkboxes", rule)
