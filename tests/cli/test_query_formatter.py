from movielog.cli import query_formatter


def test_can_have_no_anchors() -> None:
    expected = "%The Final Chapter%"

    assert query_formatter.add_wildcards("The Final Chapter") == expected


def test_can_anchor_to_end() -> None:
    expected = "%The Final Chapter"

    assert query_formatter.add_wildcards("The Final Chapter$") == expected


def test_can_anchor_to_start() -> None:
    expected = "The Final Chapter%"

    assert query_formatter.add_wildcards("^The Final Chapter") == expected
