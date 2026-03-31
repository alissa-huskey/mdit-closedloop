"""Rules for @contexts, +projects, and #areas.

Known issues:
    - Will probably break email addresses
    - No way to escape
    - Areas will currently catch text like #55
"""

from re import Pattern
from re import compile as re_compile

from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.rules_inline.state_inline import StateInline

bp = breakpoint

# pattern for labels (following the prefix character)
# for now they're all the same, though that may change later
_FINDER = r"[A-Za-z0-9:._-]+[a-zA-Z0-9]"


def _rule_maker(prefix: str, token_type: str, finder: Pattern):
    """Return a rule function for label entities.

    A label entity is a piece of metadata made up of a specific character
    followed by an identifier.

    Args
        prefix (str): Single character that denotes the start of the entity
        finder (pattern): Regex pattern that matches the entire label
        token (str): Token type to add to the dom.
    """
    def _rule(state: StateInline, silent: bool = False) -> Token | bool:
        f"""Add token to the DOM for matching text.

        Find entities that start with ``{prefix}`` and matches
        ``{finder.pattern}`` regex pattern.

        Return false if no entity is found.
        """
        start = state.pos
        length = len(state.src)

        # must start with the prefix
        if state.src[start] != prefix:
            return False

        # must be at the beginning or after whitespace
        if not (start == 0 or state.src[start - 1].isspace()):
            return False

        # must match the pattern
        if not (found := finder.match(state.src[start:])):
            return False

        text = found.group(0)
        stop = start + len(text)

        # must be at the end or followed by whitespace
        if not (stop == length or state.src[stop].isspace()):
            return False

        # move the state position forward
        state.pos += len(text)

        # add the token
        token = state.push(token_type, "", 0)
        token.content = text
        token.meta = {"identifier": text[1:]}

        # normally rule functions do not return anything
        # but this makes it way easier to test
        return token
    return _rule


# NOTE: using re_compile here instead of constructing the regex pattern text
#       in the rule function for preformance (re.compile is much faster than
#       re.match when you use the same regex pattern many times)
context_rule = _rule_maker("@", "context_reference", re_compile(f"^[@]{_FINDER}"))
project_rule = _rule_maker("+", "project_reference", re_compile(f"^[+]{_FINDER}"))
area_rule = _rule_maker("#", "area_reference", re_compile(f"^[#]{_FINDER}"))


def labels_plugin(md: MarkdownIt) -> None:
    """Parse inline @contexts, +projects, and #areas.

    This is intended for metadata on todo items, but could be used in other
    contexts for things like mentions and tags.

    Examples

        * [ ] go grocery shopping @errands
        * [ ] call the handyman @phone #repairs
        * [ ] bake a cake +billys-birthday @home

    Syntax

        - Preceeded by whitespace or at the beginning of the inline text
        - Start with the prefix character:
            - contexts: ``@``
            - projects: ``+``
            - areas: ``#``
        - Made up of alphanumeric characters and the special characters: ``:-_.``
        - End with an alphanumeric character
        - Followed by whitespace or at the end of the inline token
    """
    md.inline.ruler.push("context_reference", context_rule)
    md.inline.ruler.push("project_reference", project_rule)
    md.inline.ruler.push("area_reference", area_rule)
