from slugify import slugify


def slugify_title(title: str) -> str:
    return slugify(
        title,
        replacements=[("'", ""), ("&", "and"), ("(", ""), (")", "")],
    )
