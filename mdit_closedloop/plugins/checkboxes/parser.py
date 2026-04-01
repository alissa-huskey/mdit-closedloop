"""Provides the Parser class."""

from markdown_it.token import Token

from mdit_closedloop.plugins.checkboxes.token_view import TokenView

bp = breakpoint


class Parser():
    """Parse the tokens.

    This does all of the heavy lifting for the checkboxes_plugin.
    """

    def __init__(self, tokens: list[TokenView] = None):
        """Instantiate the object."""
        self.tokens = TokenView.from_tokens(tokens or [])

    def parse(self):
        """Find task list items and add/modify the relevant tokens."""
        for view in self.tokens[2:-1]:
            if view.is_todo():
                self.todoify_list_item(view)
                self.classify_ancestors(view)

    def todoify_list_item(self, view: TokenView) -> None:
        """Add a checkbox token to inline token children."""
        # text token
        text = view.children[0].token

        # remove the checkbox substring from the text token content
        text.content = text.content[3:].strip()

        # add checkbox token
        view.token.children.insert(0, self.checkbox_token(view.mark))

    def classify_ancestors(self, view: TokenView) -> None:
        """Add classes to ancestor tokens of the passed inline token."""
        li = view.parent.parent
        ul = li.parent

        li.token.attrSet("class", "task-list-item")
        ul.token.attrSet("class", "contains-task-list")

    def checkbox_token(self, mark: str) -> Token:
        """Return a checkbox Token."""
        token = Token("checkbox", "", 0)
        token.content = f"[{mark}]"
        token.meta["mark"] = mark
        return token
