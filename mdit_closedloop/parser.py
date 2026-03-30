"""Provides the Parser class."""

import re

from mdit_closedloop.tokens.token_view import TokenView

bp = breakpoint


class Parser():
    """Parse the tokens."""

    _GFM_WHITESPACE_RE = r"[ \t\n\v\f\r]"

    def __init__(self, tokens: list[TokenView] = None):
        """Instantiate the object."""
        self._tokens = tokens
        self.tokens = TokenView.from_tokens(tokens or [])

    def parse(self):
        """Do the thing."""
        for token in self.tokens[2:-1]:
            if self.is_todo_token(token):
                self.todoify(self._tokens[token.meta.index])
                li = token.parent.parent
                ul = li.parent

                self._tokens[li.meta.index].attrSet(
                    "class",
                    "task-list-item"
                )
                self._tokens[ul.meta.index].attrSet(
                    "class", "contains-task-list"
                )

    def todoify(self, token: TokenView) -> None:
        """Add checkbox tokens to token children."""
        assert token.children is not None

        # text token
        text = token.children[0]

        # extract the mark character
        char = re.match(r'\[(.)]', text.content).group(1)

        # remove the checkbox from the text token
        text.content = text.content[3:].strip()

        # add tokens for "[", mark, and "]"
        token.children.insert(0, self.begin_checkbox())
        token.children.insert(1, self.checkbox_mark(char))
        token.children.insert(2, self.end_checkbox())

    def is_todo_token(self, token: TokenView) -> bool:
        """Return True if this is a todo item."""
        return (
            token.is_inline()
            and token.parent.is_paragraph()
            and token.parent.parent.is_list_item()
            and self.starts_with_checkbox(token)
        )

    def starts_with_checkbox(self, token: TokenView) -> bool:
        """Return True if the token text content stars with a checkbox."""
        return re.match(rf"\[.]{self._GFM_WHITESPACE_RE}+", token.content) is not None

    def begin_checkbox(self) -> TokenView:
        """Return a checkbox_open TokenView."""
        token = TokenView("checkbox_open", "", 0)
        token.content = "["
        return token

    def checkbox_mark(self, mark: str) -> TokenView:
        """Return a checkbox_mark TokenView."""
        token = TokenView("checkbox_mark", "", 0)
        token.content = mark
        return token

    def end_checkbox(self) -> TokenView:
        """Return a checkbox_close TokenView."""
        token = TokenView("checkbox_close", "", 0)
        token.content = "]"
        return token
