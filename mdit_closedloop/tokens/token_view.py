"""Provides the TokenView class."""

from functools import partialmethod

from attr import attr, hasattrs
from markdown_it.token import Token

from mdit_closedloop.object import Object
from mdit_closedloop.partialproperty import partialproperty

bp = breakpoint


@hasattrs
class TokenView(Object):
    """Token wrapper."""

    parent: Token = None
    index: int = None
    children: list = None

    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> list["Token"]:
        """Convert a list of Token objects to Token objects.

        Also assign the index and parent attributes.
        """
        stack: list[Token] = []
        result: list[Token] = []

        for i, token in enumerate(tokens):
            # create the new view object
            view = cls(token, i)

            # close token -- pop the open token off of the stack
            if view.nesting == -1:
                if not stack:
                    raise ValueError(f"Unexpected closing token: {token.type}")
                open_token = stack.pop()

                # checks to see that open_token is `type`_open and this token
                # is `type`_closed
                if (expected := open_token.type[:-5]) != view.type[:-6]:
                    raise ValueError(
                        f"Mismatched closing token: got {view.type}, "
                        f"expected {expected}_close"
                    )

            view.parent = stack[-1] if stack else None

            # open token -- add the token to the stack
            if view.nesting == 1:
                stack.append(view)

            result.append(view)
        return result

    def _token_getter(self, name):
        """Get the attribute from the Token object."""
        if not self.token:
            return
        return getattr(self.token, name)

    nesting = partialproperty(_token_getter, name="nesting")
    type = partialproperty(_token_getter, name="type")

    def _is_type(self, _type: str) -> bool:
        """Return True if the token is the passed type."""
        return self.token.type == _type

    is_inline = partialmethod(_is_type, _type="inline")
    is_paragraph = partialmethod(_is_type, _type="paragraph_open")
    is_list_item = partialmethod(_is_type, _type="list_item_open")

    def __init__(self, *args, **kwargs):
        """Instantiate the object."""
        token = kwargs.pop("token", None)
        index = kwargs.pop("index", None)

        if args and not token and isinstance(args[0], Token):
            token = args[0]

        if not index and len(args) == 2 and isinstance(args[1], int):
            index = args[1]

        if not token and len(args) >= 3:
            token = Token(*args)

        self.token = token
        self.index = index

    @attr(method="setter")
    def token(self, value):
        """Set the token and create children."""
        self._token = value
        if value and value.children:
            self.children = [self.__class__(c) for c in value.children]
