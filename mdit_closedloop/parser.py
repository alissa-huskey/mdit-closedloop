"""Provides the Parser class."""

import re
from functools import partialmethod

from more_itertools import first

from mdit_closedloop.tokens.token import Token

bp = breakpoint


class Parser():
    """Parse the tokens."""

    _GFM_WHITESPACE_RE = r"[ \t\n\v\f\r]"

    def __init__(self, tokens: list[Token] = None):
        """Instantiate the object."""
        self._tokens = tokens
        self.tokens = Token.from_tokens(tokens or [])

    def _is_token_type(self, token: Token, _type: str) -> bool:
        """Return True if the token is the passed type."""
        return token.type == _type

    is_inline = partialmethod(_is_token_type, _type="inline")
    is_paragraph = partialmethod(_is_token_type, _type="paragraph_open")
    is_list_item = partialmethod(_is_token_type, _type="list_item_open")

    def parse(self):
        """Do the thing."""
        for i, token in enumerate(self.tokens[2:-1], 2):
            if self.is_todo_token(i):
                self.todoify(self._tokens[i])
                self._tokens[i - 2].attrSet(
                    "class",
                    "task-list-item"
                )
                self._tokens[self.ancestor(i - 2).index].attrSet(
                    "class", "contains-task-list"
                )

    def todoify(self, token: Token) -> None:
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

    def ancestor(self, index: int, levels: int = -1) -> Token:
        """Return the ancestor the specified number of levels up."""
        target = self.tokens[index].level + levels
        return first(
            [
                token
                for i in range(1, index + 1)
                if (token := self.tokens[index - i]).level == target
            ],
            -1
        )

    def is_todo_token(self, index: int) -> bool:
        """Return True if this is a todo item."""
        token = self.tokens[index]
        return (
            self.is_inline(token)
            and self.is_paragraph(self.ancestor(index))
            and self.is_list_item(self.ancestor(index, -2))
            and self.starts_with_checkbox(token)
        )

    def starts_with_checkbox(self, token: Token) -> bool:
        """Return True if the token text content stars with a checkbox."""
        return re.match(rf"\[.]{self._GFM_WHITESPACE_RE}+", token.content) is not None

    def begin_checkbox(self) -> Token:
        """Return a checkbox_open Token."""
        token = Token("checkbox_open", "", 0)
        token.content = "["
        return token

    def checkbox_mark(self, mark: str) -> Token:
        """Return a checkbox_mark Token."""
        token = Token("checkbox_mark", "", 0)
        token.content = mark
        return token

    def end_checkbox(self) -> Token:
        """Return a checkbox_close Token."""
        token = Token("checkbox_close", "", 0)
        token.content = "]"
        return token
