from markdown_it.token import Token as MDToken

from mdit_closedloop.tokens.token import Token


def test_token():
    assert Token("test", "", 0)


def test_token_from_token():
    """
    GIVEN: A MDToken object
    WHEN: Token.from_token() is called with that token
    THEN: A Token object is created with all of the values of the MDToken
    """
    source = MDToken(
        "test_token",
        "",
        0,
        children=[MDToken("child_token", "", 0)]
    )

    token = Token.from_token(source)
    assert token.as_dict() == source.as_dict()
    assert token.children[0].parent == token


def test_token__is_type(md):
    """
    GIVEN: A Token object
    WHEN: ._is_type() is called
    THEN: it should return True if it is that type
    """
    token = Token("paragraph_open", "", 0)

    assert token._is_type("paragraph_open")


def test_token_is_inline(md):
    """
    GIVEN: A Token object
    WHEN: .is_inline() is called
    THEN: it should return True if it its type is "inline"
    """
    token = Token("inline", "", 0)
    assert token.is_inline()


#  def test_token_from_():
#      """
#      GIVEN: ...
#      WHEN: ...
#      THEN: ...
#      """
