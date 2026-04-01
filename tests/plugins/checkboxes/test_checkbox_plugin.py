from markdown_it import MarkdownIt

from mdit_closedloop.plugins.checkboxes import checkboxes_plugin

bp = breakpoint


def test_checkboxes_plugin():
    md = MarkdownIt().use(checkboxes_plugin)
    tokens = md.parse("* [x] completed task")

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
        and len(tokens[3].children) == 2
    )

    children = tokens[3].children
    assert children[0].type == "checkbox"
    assert children[1].type == "text"

    assert children[0].content == "[x]"
    assert children[0].meta["mark"] == "x"
    assert children[1].content == "completed task"
