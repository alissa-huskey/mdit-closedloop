from markdown_it.token import Token

from mdit_closedloop.tokens.token_view import TokenView

bp = breakpoint


def test_token():
    assert TokenView("test", "", 0)


def test_token_from_token():
    """
    GIVEN: A Token object
    WHEN: TokenView.from_token() is called with that token
    THEN: A TokenView object is created with all of the values of the Token
    """
    token = Token(
        "test_token",
        "",
        0,
        children=[Token("child_token", "", 0)]
    )

    view = TokenView.from_token(token)

    # make sure the index key was added to meta
    assert "index" in view.meta
    assert "index" in view.children[0].meta

    # but now remove it so we can compare the tokens
    view.meta = {}
    view.children[0].meta = {}

    assert view.as_dict() == token.as_dict()
    assert view.children[0].parent == view


def test_token_from_tokens(md):
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

    assert tokens[0].meta.index == 0
    assert tokens[1].meta.index == 1
    assert tokens[2].meta.index == 2
    assert tokens[3].meta.index == 3
    assert tokens[4].meta.index == 4
    assert tokens[5].meta.index == 5
    assert tokens[6].meta.index == 6

    assert tokens[0].type == "bullet_list_open" and tokens[0].parent is None
    assert tokens[1].type == "list_item_open" and tokens[1].parent == tokens[0]
    assert tokens[2].type == "paragraph_open" and tokens[2].parent == tokens[1]
    assert tokens[3].type == "inline" and tokens[3].parent == tokens[2]
    assert tokens[4].type == "paragraph_close" and tokens[4].parent == tokens[1]
    assert tokens[5].type == "list_item_close" and tokens[5].parent == tokens[0]
    assert tokens[6].type == "bullet_list_close" and tokens[6].parent is None


def test_token_from_tokens_complex(md):
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


def test_token__is_type(md):
    """
    GIVEN: A TokenView object
    WHEN: ._is_type() is called
    THEN: it should return True if it is that type
    """
    view = TokenView("paragraph_open", "", 0)

    assert view._is_type("paragraph_open")


def test_token_is_inline(md):
    """
    GIVEN: A TokenView object
    WHEN: .is_inline() is called
    THEN: it should return True if it its type is "inline"
    """
    view = TokenView("inline", "", 0)
    assert view.is_inline()


#  def test_token_from_():
#      """
#      GIVEN: ...
#      WHEN: ...
#      THEN: ...
#      """
