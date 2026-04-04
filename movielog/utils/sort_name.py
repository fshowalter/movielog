def generate_sort_name(name: str) -> str:
    split_name = name.split()
    last_name = split_name[-1]
    other_names = split_name[:-1]

    return "{}, {}".format(last_name, " ".join(other_names))
