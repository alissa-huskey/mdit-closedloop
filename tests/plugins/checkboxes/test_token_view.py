from markdown_it.token import Token

from mdit_closedloop.plugins.checkboxes.token_view import TokenView

bp = breakpoint


def test_token_view_with_args():
    """
    WHEN: A TokenView object is instantiated with non-Token arguments
    THEN: a token should be created and assigned to .token
    """
    view = TokenView("test", "", 0)

    assert view.token
    assert view.token.type == "test"


def test_token_view_with_token():
    """
    WHEN: A TokenView object is instantiated with a single arg that is a Token
    THEN: the token should be assigned to .token
    AND:
    """
    token = Token("test", "", 0)
    view = TokenView(token)

    assert view.token == token


def test_token_view_with_token_and_index():
    """
    WHEN: A TokenView object is instantiated with a Token and an int
    THEN: the token should be assigned to .token
    AND: the int should be assigned to .index
    AND:
    """
    token = Token("test", "", 0)
    view = TokenView(token, 5)

    assert view.token == token
    assert view.index == 5


def test_token_view_with_token_and_children():
    """
    WHEN: TokenView() is instantiated with a Token object that has children
    THEN: all of its children should be TokenView objects
    """
    token = Token(
        "test_token_view",
        "",
        0,
        children=[Token("child_token", "", 0)]
    )

    view = TokenView(token)

    assert view.token == token
    assert view.children and isinstance(view.children[0], TokenView)


def test_token_view_from_tokens(md):
    """
    GIVEN: A list of Token object
    WHEN: TokenView.from_tokens() is called with that list
    THEN: it should returl a list of TokenView objects
    AND: each object should have the parent set
    AND: each object should have the index set
    """
    source_tokens = md.parse("* a list item")

    tokens = TokenView.from_tokens(source_tokens)

    assert all([isinstance(t, TokenView) for t in tokens])

    assert tokens[0].index == 0
    assert tokens[1].index == 1
    assert tokens[2].index == 2
    assert tokens[3].index == 3
    assert tokens[4].index == 4
    assert tokens[5].index == 5
    assert tokens[6].index == 6

    assert tokens[0].type == "bullet_list_open" and tokens[0].parent is None
    assert tokens[1].type == "list_item_open" and tokens[1].parent == tokens[0]
    assert tokens[2].type == "paragraph_open" and tokens[2].parent == tokens[1]
    assert tokens[3].type == "inline" and tokens[3].parent == tokens[2]
    assert tokens[4].type == "paragraph_close" and tokens[4].parent == tokens[1]
    assert tokens[5].type == "list_item_close" and tokens[5].parent == tokens[0]
    assert tokens[6].type == "bullet_list_close" and tokens[6].parent is None


def test_token_view_from_tokens_complex(md):
    """
    GIVEN: A list of Token object
    WHEN: TokenView.from_tokens() is called with that list
    THEN: it should returl a list of TokenView objects
    AND: each object should have the parent set
    AND: each object should have the index set
    """
    source_tokens = md.parse("""
# title

* item A
    * subitem A.1
    * subitem A.2
    * subitem A.3
* item B
* item C
    * subitem C.1
    * subitem C.2
    * subitem C.3
    """)

    tokens = TokenView.from_tokens(source_tokens)

    # the only thing needed here is the index and parent_index
    # the rest of it is just for reference, so I can make
    # sense of this later
    mapping = {
        3: None,  # bullet_list_open -- top level list
        4: 3,     # list_item_open -- list item
        6: 5,     # inline -- innermost leaf "item A"
        8: 4,     # bullet_list_open -- sublist
        9: 8,     # list_item_open -- sublist list item "subitem A.1"
        14: 8,    # list_item_open -- sublist list item "sublist A.2"
        19: 8,    # list_item_open -- sublist list item "sublist A.3"
        24: 4,    # bullet_list_close -- end sublist
        36: 35,   # list_item_opne -- sublist list item "sublist C.1"
    }

    assert all([isinstance(t, TokenView) for t in tokens])

    for token_id, parent_index in mapping.items():
        view = tokens[token_id]

        if not parent_index:
            assert view.parent is None
            continue

        expected_parent = tokens[parent_index]
        assert view.parent == expected_parent


def test_token_view__is_type(md):
    """
    GIVEN: A TokenView object
    WHEN: ._is_type() is called
    THEN: it should return True if it is that type
    """
    view = TokenView("paragraph_open", "", 0)

    assert view._is_type("paragraph_open")


def test_token_view_is_inline(md):
    """
    GIVEN: A TokenView object
    WHEN: .is_inline() is called
    THEN: it should return True if it its type is "inline"
    """
    view = TokenView("inline", "", 0)
    assert view.is_inline()


def test_token_view_starts_with_checkbox(md):
    """
    GIVEN: A Token object with content
    WHEN: .starts_with_checkbox()
    THEN: it should return True if the texts starts with "[ ]"
          with any single character between the brackets
    """
    view = TokenView(Token("", "", 0, content="[-] pending task"))

    assert view.starts_with_checkbox()
    assert view.mark == "-"


def test_token_view_is_todo(md):
    """
    GIVEN: A TokenView object with an inline Token that contains a checkbox
    WHEN: .is_todo() is called
    THEN: it should return True
    """
    tokens = TokenView.from_tokens(md.parse("* [x] I did it"))
    token = tokens[3]

    assert token.is_todo()


#  def test_token_view_from_():
#      """
#      GIVEN: ...
#      WHEN: ...
#      THEN: ...
#      """
