"""Provides the TokenView class."""

from functools import partialmethod
from mdit_closedloop.dict import Dict

from markdown_it.token import Token

bp = breakpoint


class TokenView(Token):
    """Modified token base class."""

    parent: Token = None
    index: int = None

    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> list["Token"]:
        """Convert a list of Token objects to Token objects.

        Also assign the index and parent attributes.
        """
        stack: list[Token] = []
        result: list[Token] = []

        for i, t in enumerate(tokens):
            # create the new token
            token = cls.from_token(t, i)

            # close token -- pop the open token off of the stack
            if token.nesting == -1:
                if not stack:
                    raise ValueError(f"Unexpected closing token: {token.type}")
                open_token = stack.pop()

                # checks to see that open_token is `type`_open and this token
                # is `type`_closed
                if (expected := open_token.type[:-5]) != token.type[:-6]:
                    raise ValueError(
                        f"Mismatched closing token: got {token.type}, "
                        f"expected {expected}_close"
                    )

            token.parent = stack[-1] if stack else None

            # open token -- add the token to the stack
            if token.nesting == 1:
                stack.append(token)

            result.append(token)
        return result

    @classmethod
    def from_token(cls, source: Token, idx: int = None) -> "Token":
        """Return an instance of this class that is a copy of source."""
        token = cls.from_dict(source.as_dict())
        token.meta = Dict(token.meta)
        token.meta.index = idx

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
