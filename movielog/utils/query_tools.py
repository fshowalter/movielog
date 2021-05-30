def exclude_person_ids_query_clause() -> str:
    ids_to_exclude = [
        "nm0498278",  # Stan Lee
        "nm0456158",  # Jack Kirby
        "nm4160687",  # Jim Starlin
        "nm0800209",  # Joe Simon
        "nm1293367",  # Larry Lieber
        "nm1921680",  # Steve Englehart
        "nm3238648",  # Steve Gan
        "nm2757098",  # Bill Mantlo
        "nm0317493",  # Keith Giffen
        "nm1411347",  # Don Heck
        "nm4022192",  # Steve McNiven
        "nm2092839",  # Mark Millar
        "nm0831290",  # Bram Stoker
    ]

    exclude_strings = []

    for person_id in ids_to_exclude:
        exclude_strings.append('person_imdb_id != "{0}"'.format(person_id))

    return " AND ".join(exclude_strings)
