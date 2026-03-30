"""Provides the Token base class, inherited from markdown_it's Token."""

from markdown_it.token import Token as MDToken
from functools import partialmethod

bp = breakpoint


class Token(MDToken):
    """Modified token base class."""

    parent: MDToken = None
    index: int = None

    @classmethod
    def from_tokens(cls, tokens: list[MDToken]) -> list["Token"]:
        """Convert a list of MDToken objects to Token objects."""
        return [cls.from_token(t, i) for i, t in enumerate(tokens)]

    @classmethod
    def from_token(cls, source: MDToken, idx: int = None) -> "Token":
        """Return an instance of this class that is a copy of source."""
        token = cls.from_dict(source.as_dict())
        token.index = idx
        if token.children:
            for i, c in enumerate(token.children):
                child = cls.from_token(c)
                child.parent = token
                child.index = i
                token.children[i] = child
        return token

    def _is_type(self, _type: str) -> bool:
        """Return True if the token is the passed type."""
        return self.type == _type

    is_inline = partialmethod(_is_type, _type="inline")
    is_paragraph = partialmethod(_is_type, _type="paragraph_open")
    is_list_item = partialmethod(_is_type, _type="list_item_open")
