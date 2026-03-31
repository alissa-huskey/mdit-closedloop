"""Provides the Parser class."""

from markdown_it.token import Token

from mdit_closedloop.plugins.checkboxes.token_view import TokenView

bp = breakpoint


class Parser():
    """Parse the tokens.

    This does all of the heavy lifting for the checkbox_plugin.
    """

    def __init__(self, tokens: list[TokenView] = None):
        """Instantiate the object."""
        self.tokens = TokenView.from_tokens(tokens or [])

    def parse(self):
        """Do the thing."""
        for view in self.tokens[2:-1]:
            if view.is_todo():
                self.todoify(view)

                li = view.parent.parent
                ul = li.parent

                li.token.attrSet(
                    "class",
                    "task-list-item"
                )
                ul.token.attrSet(
                    "class", "contains-task-list"
                )

    def todoify(self, view: TokenView) -> None:
        """Add checkbox tokens to token children."""
        assert view.children is not None

        # text token
        text = view.children[0].token

        # remove the checkbox from the text token
        text.content = text.content[3:].strip()

        # add tokens for "[", mark, and "]"
        view.token.children.insert(0, self.begin_checkbox())
        view.token.children.insert(1, self.checkbox_mark(view.mark))
        view.token.children.insert(2, self.end_checkbox())

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
