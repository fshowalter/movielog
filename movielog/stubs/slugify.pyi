from typing import Iterable, Optional, Tuple

def slugify(
    text: str,
    entities: bool = ...,
    decimal: bool = ...,
    hexadecimal: bool = ...,
    max_length: int = ...,
    word_boundary: bool = ...,
    separator: str = ...,
    save_order: bool = ...,
    stopwords: Iterable[str] = ...,
    regex_pattern: Optional[str] = ...,
    lowercase: bool = ...,
    replacements: Iterable[Tuple[str, str]] = ...,
) -> str: ...
