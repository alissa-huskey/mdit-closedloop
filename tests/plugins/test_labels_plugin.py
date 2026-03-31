import pytest
from markdown_it import MarkdownIt
from markdown_it.token import Token

from mdit_closedloop.object import Object as Stub
from mdit_closedloop.plugins.labels.plugin import (area_rule, context_rule,
                                                   labels_plugin, project_rule)

bp = breakpoint


@pytest.mark.parametrize(["position", "text", "expected"], [
    # matching
    (0, "@home", "@home"),
    (0, "@Work", "@Work"),
    (0, "@grocery-shopping", "@grocery-shopping"),
    (0, "@coding_class", "@coding_class"),
    (0, "@school:science", "@school:science"),
    (0, "@school.math", "@school.math"),
    (0, "@errands Go grocery shopping", "@errands"),
    (12, "Bake a cake @home +billys-birthday", "@home"),

    # nonmatching
    (0, "@school_", False),
    (0, "@school:@science", False),
    (0, "@school+english", False),
    (0, "@school.@math", False),
    (3, "joe@example.com", False)
])
def test_context_rule(position, text, expected):
    state = Stub(pos=position, src=text, push=Token)
    token = context_rule(state)

    # non-matching
    if expected is False:
        assert token is False
        return

    # matching
    assert token is not False
    assert token.content == expected
    assert token.meta["identifier"] == expected[1:]


@pytest.mark.parametrize(["position", "text", "expected"], [
    (0, "+project", "+project"),
    (0, "a+b=c", False),
])
def test_project_rule(position, text, expected):
    state = Stub(pos=position, src=text, push=Token)
    token = project_rule(state)

    if expected is False:
        assert token is False
        return

    assert token is not False
    assert token.content == expected
    assert token.meta["identifier"] == expected[1:]


@pytest.mark.parametrize(["position", "text", "expected"], [
    (0, "#adulting", "#adulting"),
    (13, "[links with](#anchors)", False),
    #  (0, "#15", False)     # TODO: need to implement
])
def test_area_rule(position, text, expected):
    state = Stub(pos=position, src=text, push=Token)
    token = area_rule(state)

    if expected is False:
        assert token is False
        return

    assert token is not False
    assert token.content == expected
    assert token.meta["identifier"] == expected[1:]


def test_labels_plugin():
    # NOTE: This markdown does not include any checkboxes, since test is
    #       just for labels.
    #       The metadata like due:YYYY-MM-DD is ignored for this test.
    markdown = """
# My Awesome Task List

## Work @work

### Urgent & Important

- Finalize Q2 report @work #finance
- Prepare presentation for client meeting +website-redesign @client:acme

### Project: Website Redesign +website-redesign #webdev

- Draft new homepage mockups #design due:2025-06-10
- Develop new navigation component #coding #frontend due:2025-06-15
- Write content for "About Us" page #content due:2025-06-20

## Home #personal

- Buy groceries @errands
  - Milk
  - Eggs
  - Bread
- Book dentist appointment @phone
- Plan weekend trip #fun +vacation due:2025-07-01

## Studying #learning

- Read chapter #3 of "Advanced TypeScript" #typescript #programming
- Watch lecture #5 in +next.js-course series #webdev
    """

    # tokens that include labels
    # mapping of: index: (content, [(child.type, child.content)...])
    expected = {
        4: (
            'Work @work', [
                ('text', 'Work '),
                ('context_reference', '@work'),
            ],
        ),
        12: (
            'Finalize Q2 report @work #finance', [
                ('text', 'Finalize Q2 report '),
                ('context_reference', '@work'),
                ('text', ' '),
                ('area_reference', '#finance'),
            ],
        ),
        17: (
            'Prepare presentation for client meeting +website-redesign @client:acme',
            [
                ('text', 'Prepare presentation for client meeting '),
                ('project_reference', '+website-redesign'),
                ('text', ' '),
                ('context_reference', '@client:acme'),
            ],
        ),
        22: (
            'Project: Website Redesign +website-redesign #webdev', [
                ('text', 'Project: Website Redesign '),
                ('project_reference', '+website-redesign'),
                ('text', ' '),
                ('area_reference', '#webdev'),
            ],
        ),
        27: (
            'Draft new homepage mockups #design due:2025-06-10', [
                ('text', 'Draft new homepage mockups '),
                ('area_reference', '#design'),
                ('text', ' due:2025-06-10'),
            ],
        ),
        32: (
            'Develop new navigation component #coding #frontend due:2025-06-15', [
                ('text', 'Develop new navigation component '),
                ('area_reference', '#coding'),
                ('text', ' '),
                ('area_reference', '#frontend'),
                ('text', ' due:2025-06-15'),
            ],
        ),
        37: (
            'Write content for "About Us" page #content due:2025-06-20', [
                ('text', 'Write content for "About Us" page '),
                ('area_reference', '#content'),
                ('text', ' due:2025-06-20'),
            ],
        ),
        42: (
            'Home #personal', [
                ('text', 'Home '),
                ('area_reference', '#personal'),
            ],
        ),
        47: (
            'Buy groceries @errands', [
                ('text', 'Buy groceries '),
                ('context_reference', '@errands'),
            ],
        ),
        69: (
            'Book dentist appointment @phone', [
                ('text', 'Book dentist appointment '),
                ('context_reference', '@phone'),
            ],
        ),
        74: (
            'Plan weekend trip #fun +vacation due:2025-07-01',
            [
                ('text', 'Plan weekend trip '),
                ('area_reference', '#fun'),
                ('text', ' '),
                ('project_reference', '+vacation'),
                ('text', ' due:2025-07-01'),
            ],
        ),
        79: (
            'Studying #learning', [
                ('text', 'Studying '),
                ('area_reference', '#learning'),
            ],
        ),
        84: (
            'Read chapter #3 of "Advanced TypeScript" #typescript #programming',
            [
                ('text', 'Read chapter #3 of "Advanced TypeScript" '),
                ('area_reference', '#typescript'),
                ('text', ' '),
                ('area_reference', '#programming'),
            ],
        ),
        89: (
            'Watch lecture #5 in +next.js-course series #webdev',
            [
                ('text', 'Watch lecture #5 in '),
                ('project_reference', '+next.js-course'),
                ('text', ' series '),
                ('area_reference', '#webdev'),
            ],
        ),
    }

    # parse the markdown
    md = MarkdownIt().use(labels_plugin)
    tokens = md.parse(markdown)

    # gather all of the tokens with children that are any of the label types
    # and put them in the same format as expected
    label_types = ["project_reference", "area_reference", "context_reference"]
    actual = {
        i: (t.content, [(c.type, c.content) for c in t.children])
        for i, t in enumerate(tokens)
        if t.children and any([c.type in label_types for c in t.children])
    }

    assert actual == expected
