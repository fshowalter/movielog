def add_wildcards(query: str) -> str:
    start_wildcard = "%"
    end_wildcard = "%"

    if query.startswith("^"):
        query = query[1:]
        start_wildcard = ""
    if query.endswith("$"):
        query = query[:-1]
        end_wildcard = ""

    return f"{start_wildcard}{query}{end_wildcard}"
