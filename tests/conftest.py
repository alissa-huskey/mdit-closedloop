import pytest
from markdown_it import MarkdownIt


@pytest.fixture
def md() -> MarkdownIt:
    """Return a MarkdownIt parser object."""
    return MarkdownIt()
