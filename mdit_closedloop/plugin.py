"""Builds task/todo lists out of markdown lists with items starting with [ ] or [x]"""

from __future__ import annotations

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore

from mdit_closedloop.parser import Parser


def closedloop_plugin(md: MarkdownIt) -> None:
    """Plugin for parsing task/todo metadata out of markdown lists.

    For example::
       - [ ] An item that needs doing
       - [.] An pending item
       - [x] An item that is complete
    """

    def handler(state: StateCore) -> None:
        tokens = state.tokens
        parser = Parser(tokens)
        parser.parse()

    md.core.ruler.after("inline", "closedloop", handler)
