"""Lint the markdown content for punctuation the site's renderer takes literally.

franksmovielog.com renders this content with Satteri, which emits raw HTML verbatim and pairs
quotes with an open/close state machine. Its predecessor reparsed the HTML and chose each
quote's direction from its immediate neighbors, so typos were silently repaired. They are not
anymore, which makes these defects worth catching where the content is written.

Each test collects every offender before failing, so a whole batch can be fixed in one pass.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent

CONTENT_FOLDER_NAMES = ("reviews", "viewings")

# Frank types only ' and ", letting the renderer choose the glyph, so every one of these
# arrived by copy/paste -- and copy/paste is how an opening quote ends up where an apostrophe
# belongs (`There's`, `spring of '63`). Straight quotes render correctly in every position,
# including leading elisions, so there is no reason to write these by hand.
# Spelled as escapes because that is precisely the problem with these characters: on screen
# they are hard to tell from the ASCII quotes they should have been.
NON_STANDARD_QUOTES = frozenset(
    "\u2018\u2019\u201a\u201b"  # single: curly pair, low-9, high-reversed-9
    "\u201c\u201d\u201e\u201f"  # double: curly pair, low-9, high-reversed-9
    "\u2032\u2033\u2035\u2036"  # prime, double prime, and their reversed forms
    "\u00ab\u00bb\u2039\u203a"  # guillemets: double and single
)

# Curly doubles are folded in so this check means the same thing before and after the
# content is normalized: would these quotation marks pair up once they are all straight?
DOUBLE_QUOTE_FOLD = str.maketrans({"\u201c": '"', "\u201d": '"'})

# Space, tab and newline are the only whitespace markdown should contain. A no-break or hair
# space is invisible in review, and breaks quote pairing when it lands between quote marks.
ALLOWED_WHITESPACE = frozenset(" \t\n")
WHITESPACE_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp", "Zs"})

# `--` renders as an em dash, so a literal dash in the source arrived by copy/paste from a
# quoted passage. Unicode's dash punctuation category covers the em and en dashes this content
# has picked up, plus rarer strays like the figure dash; the ASCII hyphen is the one Frank
# types.
DASH_CATEGORY = "Pd"

ELLIPSIS = "…"

# Satteri converts exactly three dots and nothing else, so a spaced `. . .`, a four-dot run,
# and a pasted U+2026 all reach the page as typed. House style is three dots.
NON_STANDARD_ELLIPSIS = re.compile(r"…|\.(?:[ \t]*\.){2,}")

# A height is written 6'3": that inch mark is a measurement, so it has no partner and would
# read as an unbalanced quotation mark. Only the feet-and-inches shape is exempt -- a bare
# `1992"` is the closing half of a quotation, not a measurement.
INCH_MARK = re.compile(r"\b\d+'\d{1,2}\"")

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FENCED_CODE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_TAG = re.compile(r"<[^>]*>")
PARAGRAPH_BREAK = re.compile(r"(\n\s*\n)")

# The only tags in this content are <span> and <br>, and <br> is void. Satteri re-emits raw
# HTML verbatim rather than reparsing and repairing it, so a `<span>` typed where `</span>`
# belonged reaches the page as an unclosed element.
SPAN_TAG = re.compile(r"<(/?)span\b[^>]*>")


def content_files() -> Iterator[Path]:
    for folder_name in CONTENT_FOLDER_NAMES:
        yield from sorted((CONTENT_ROOT / folder_name).glob("*.md"))


def strip_frontmatter(source: str) -> str:
    """Blank out the frontmatter, keeping the line count so line numbers stay accurate."""
    match = FRONTMATTER.match(source)

    if not match:
        return source

    return "\n" * match.group().count("\n") + source[match.end() :]


def paragraphs(body: str) -> Iterator[tuple[int, str]]:
    """Yield (line number, text) for each blank-line-separated block."""
    line_number = 1

    for index, chunk in enumerate(PARAGRAPH_BREAK.split(body)):
        if index % 2 == 0:
            yield (line_number, chunk)

        line_number += chunk.count("\n")


def prose_only(paragraph: str) -> str:
    """Drop code, HTML tags and inch marks, whose quotes are not prose quotation marks."""
    return INCH_MARK.sub("", HTML_TAG.sub("", INLINE_CODE.sub("", FENCED_CODE.sub("", paragraph))))


def describe(character: str) -> str:
    return f"U+{ord(character):04X} {unicodedata.name(character, 'UNNAMED')}"


def report(offenders: list[str]) -> str:
    return "\n".join([f"{len(offenders)} offender(s):", *offenders])


def find_non_standard_quotes(source: str) -> Iterator[tuple[int, str]]:
    for line_number, line in enumerate(source.split("\n"), start=1):
        found = sorted({character for character in line if character in NON_STANDARD_QUOTES})

        if found:
            yield (line_number, ", ".join(describe(character) for character in found))


def find_unbalanced_double_quotes(source: str) -> Iterator[tuple[int, str]]:
    for line_number, paragraph in paragraphs(strip_frontmatter(source)):
        if prose_only(paragraph).translate(DOUBLE_QUOTE_FOLD).count('"') % 2:
            yield (line_number, paragraph.strip())


def find_unbalanced_spans(source: str) -> Iterator[tuple[int, str]]:
    open_line_numbers: list[int] = []
    offenders: list[tuple[int, str]] = []

    for line_number, line in enumerate(source.split("\n"), start=1):
        for match in SPAN_TAG.finditer(line):
            if not match.group(1):
                open_line_numbers.append(line_number)
            elif open_line_numbers:
                open_line_numbers.pop()
            else:
                offenders.append((line_number, f"{match.group()} closes nothing"))

    offenders.extend((line_number, "<span> is never closed") for line_number in open_line_numbers)

    yield from sorted(offenders)


def find_literal_dashes(source: str) -> Iterator[tuple[int, str]]:
    for line_number, line in enumerate(source.split("\n"), start=1):
        for column, character in enumerate(line, start=1):
            if character != "-" and unicodedata.category(character) == DASH_CATEGORY:
                yield (line_number, f"column {column}: {describe(character)}")


def find_non_standard_ellipses(source: str) -> Iterator[tuple[int, str]]:
    for line_number, line in enumerate(source.split("\n"), start=1):
        for match in NON_STANDARD_ELLIPSIS.finditer(line):
            found = match.group()

            if found == "...":
                continue

            detail = describe(found) if found == ELLIPSIS else repr(found)
            yield (line_number, f"column {match.start() + 1}: {detail} should be '...'")


def find_non_standard_whitespace(source: str) -> Iterator[tuple[int, str]]:
    for line_number, line in enumerate(source.split("\n"), start=1):
        for column, character in enumerate(line, start=1):
            if character in ALLOWED_WHITESPACE:
                continue

            if unicodedata.category(character) in WHITESPACE_CATEGORIES:
                yield (line_number, f"column {column}: {describe(character)}")


def test_flags_a_curly_apostrophe() -> None:
    assert list(find_non_standard_quotes("There\u2018s")) == [
        (1, "U+2018 LEFT SINGLE QUOTATION MARK"),
    ]


def test_allows_straight_quotes_and_apostrophes() -> None:
    assert list(find_non_standard_quotes("\"Keep 'er coming,\" he said of '63.")) == []


def test_flags_a_quotation_missing_its_closing_mark() -> None:
    assert [line for line, _ in find_unbalanced_double_quotes('> "Charley, stop it!')] == [1]


def test_allows_single_quotes_nested_inside_double_quotes() -> None:
    assert list(find_unbalanced_double_quotes("\"He said 'hello' to me.\"")) == []


def test_ignores_double_quotes_in_html_attributes() -> None:
    assert list(find_unbalanced_double_quotes('<span data-title-id="carrie">Carrie</span>')) == []


def test_ignores_double_quotes_in_code_spans() -> None:
    assert list(find_unbalanced_double_quotes('The `"` character is literal.')) == []


def test_ignores_the_inch_mark_in_a_height() -> None:
    assert list(find_unbalanced_double_quotes("At 6'3\", he towers over Mitchum.")) == []


def test_still_flags_a_lone_quote_closing_a_number() -> None:
    assert [line for line, _ in find_unbalanced_double_quotes('Aiden is very 1992".')] == [1]


def test_reports_an_unbalanced_paragraph_at_its_line_in_the_file() -> None:
    source = '---\nslug: carrie\n---\n\nA "balanced" one.\n\nAn "unbalanced one.\n'

    assert [line for line, _ in find_unbalanced_double_quotes(source)] == [7]


def test_flags_an_opening_span_typed_where_a_closing_span_belonged() -> None:
    source = '<span data-title-id="the-dead-zone">_The Dead Zone_<span>'

    assert list(find_unbalanced_spans(source)) == [
        (1, "<span> is never closed"),
        (1, "<span> is never closed"),
    ]


def test_allows_a_well_formed_span() -> None:
    assert list(find_unbalanced_spans('<span data-title-id="carrie">_Carrie_</span>')) == []


def test_flags_a_closing_span_that_closes_nothing() -> None:
    assert list(find_unbalanced_spans("plain text</span>")) == [(1, "</span> closes nothing")]


def test_ignores_void_break_tags() -> None:
    assert list(find_unbalanced_spans("one<br>two")) == []


def test_flags_a_literal_em_dash() -> None:
    assert list(find_literal_dashes("abuse\u2014the predatory nature")) == [
        (1, "column 6: U+2014 EM DASH"),
    ]


def test_flags_a_literal_en_dash() -> None:
    assert list(find_literal_dashes("passenger \u2013 a huge face")) == [
        (1, "column 11: U+2013 EN DASH"),
    ]


def test_allows_ascii_hyphens_and_double_hyphens() -> None:
    assert list(find_literal_dashes("grey-black abuse--the predatory nature")) == []


def test_flags_a_literal_ellipsis_character() -> None:
    assert list(find_non_standard_ellipses("You're… she considers")) == [
        (1, "column 7: U+2026 HORIZONTAL ELLIPSIS should be '...'"),
    ]


def test_flags_a_spaced_ellipsis() -> None:
    assert list(find_non_standard_ellipses("I, er, um, thought . . .")) == [
        (1, "column 20: '. . .' should be '...'"),
    ]


def test_flags_a_four_dot_ellipsis() -> None:
    assert list(find_non_standard_ellipses("Welcome to Fright Night....")) == [
        (1, "column 24: '....' should be '...'"),
    ]


def test_allows_three_dots_and_ordinary_sentence_stops() -> None:
    assert list(find_non_standard_ellipses("See you Charlie... soon. He left. She stayed.")) == []


def test_flags_a_no_break_space() -> None:
    assert list(find_non_standard_whitespace("a\u00a0b")) == [
        (1, "column 2: U+00A0 NO-BREAK SPACE"),
    ]


def test_allows_spaces_tabs_and_newlines() -> None:
    assert list(find_non_standard_whitespace("a b\tc\nd")) == []


def test_no_non_standard_quotes() -> None:
    offenders = [
        f"{path.parent.name}/{path.name}:{line_number}  {detail}"
        for path in content_files()
        for line_number, detail in find_non_standard_quotes(path.read_text(encoding="utf8"))
    ]

    assert not offenders, report(offenders)


def test_double_quotes_balance_within_each_paragraph() -> None:
    offenders = [
        f"{path.parent.name}/{path.name}:{line_number}  {detail[:160]}"
        for path in content_files()
        for line_number, detail in find_unbalanced_double_quotes(path.read_text(encoding="utf8"))
    ]

    assert not offenders, report(offenders)


def test_no_unbalanced_spans() -> None:
    offenders = [
        f"{path.parent.name}/{path.name}:{line_number}  {detail}"
        for path in content_files()
        for line_number, detail in find_unbalanced_spans(path.read_text(encoding="utf8"))
    ]

    assert not offenders, report(offenders)


def test_no_literal_dashes() -> None:
    offenders = [
        f"{path.parent.name}/{path.name}:{line_number}  {detail}"
        for path in content_files()
        for line_number, detail in find_literal_dashes(path.read_text(encoding="utf8"))
    ]

    assert not offenders, report(offenders)


def test_no_non_standard_ellipses() -> None:
    offenders = [
        f"{path.parent.name}/{path.name}:{line_number}  {detail}"
        for path in content_files()
        for line_number, detail in find_non_standard_ellipses(path.read_text(encoding="utf8"))
    ]

    assert not offenders, report(offenders)


def test_no_non_standard_whitespace() -> None:
    offenders = [
        f"{path.parent.name}/{path.name}:{line_number}  {detail}"
        for path in content_files()
        for line_number, detail in find_non_standard_whitespace(path.read_text(encoding="utf8"))
    ]

    assert not offenders, report(offenders)
