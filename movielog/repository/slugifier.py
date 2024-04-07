from slugify import slugify


def slugify_title(title: str) -> str:
    return slugify(
        title,
        replacements=[("'", ""), ("&", "and"), ("(", ""), (")", "")],
    )


def slugify_name(name: str) -> str:
    return slugify(
        name,
        replacements=[("'", ""), ("&", "and"), ("(", ""), (")", "")],
    )
