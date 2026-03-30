from mdit_closedloop.parser import Parser
from mdit_closedloop.tokens.token_view import TokenView

bp = breakpoint


def test_parser():
    assert Parser()


def test_parser_starts_with_checkbox(md):
    """
    GIVEN: A Parser object
    WHEN: .starts_with_checkbox() is called with text
    THEN: it should return True if the texts starts with "[ ]"
          with any single character between the brackets
    """
    tokens = md.parse("[-] pending task")
    parser = Parser()

    assert parser.starts_with_checkbox(TokenView(tokens[1]))


def test_parser_is_todo_token(md):
    """
    GIVEN: A Parser object
    AND: A list item that contains a checkbox
    WHEN: .is_list_token() is called with the index of the inline token
    THEN: it should return True
    """
    tokens = TokenView.from_tokens(md.parse("* [x] I did it"))
    parser = Parser()

    assert parser.is_todo_token((tokens[3]))


def test_parser_todoify(md):
    """
    GIVEN: A Parser object and an inline token
    WHEN: .todoify() is called with an inline token
    THEN: it should replace the checkbox with a marker token
    """
    tokens = md.parse("* [x] I did it")
    token = tokens[3]
    children = token.children

    parser = Parser(tokens)
    parser.todoify(token)

    assert len(children) == 4
    assert children[0].type == "checkbox_open"
    assert children[1].type == "checkbox_mark"
    assert children[2].type == "checkbox_close"
    assert children[3].type == "text"

    assert children[1].content == "x"
    assert children[3].content == "I did it"


def test_parser_begin_checkbox():
    """
    GIVEN: A Parser object
    WHEN: .begin_checkbox() is called
    THEN: it should return a checkbox_open token
    """
    parser = Parser()
    token = parser.begin_checkbox()

    assert token.type == "checkbox_open"
    assert token.content == "["


def test_parser_end_checkbox():
    """
    GIVEN: A Parser object
    WHEN: .end_checkbox() is called
    THEN: it should return a checkbox_close token
    """
    parser = Parser()
    token = parser.end_checkbox()

    assert token.type == "checkbox_close"
    assert token.content == "]"


def test_parser_parse(md):
    """
    GIVEN: A Parser object and
    AND: a list of Tokens parsed from markdown
    WHEN: .parse() is called
    THEN: it should add the class "contains-task-list" to all ordered lists
          that contain items with checkboxes
    AND: it should add the class "task-list-item" to all list items that
         contain checkboxes
    AND: it should modify the inline checkbox item to contain checkbox_open,
         checkbox_mark and checkbox_close Tokens.
    """
    tokens = md.parse("* [x] I did it")
    parser = Parser(tokens)
    parser.parse()

    assert (
        tokens[0].type == "bullet_list_open"
        and tokens[0].attrGet("class") == "contains-task-list"
    )

    assert (
        tokens[1].type == "list_item_open"
        and tokens[1].attrGet("class") == "task-list-item"
    )

    assert (
        tokens[3].type == "inline"
        and len(tokens[3].children) == 4
    )

    children = tokens[3].children
    assert children[0].type == "checkbox_open"
    assert children[1].type == "checkbox_mark"
    assert children[2].type == "checkbox_close"
    assert children[3].type == "text"

    assert children[1].content == "x"
    assert children[3].content == "I did it"


#  def test_parser_():
#      """
#      GIVEN: ...
#      WHEN: ...
#      THEN: ...
#      """
