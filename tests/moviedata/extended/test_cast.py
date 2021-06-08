import imdb

from movielog.moviedata.extended import cast


def test_parse_parses_cast_credits() -> None:
    expected = [
        cast.Credit(
            person_imdb_id="nm0000078",
            name="John Wayne",
            sequence=0,
            notes="",
            roles=["John T. Chance"],
        ),
        cast.Credit(
            person_imdb_id="nm0001509",
            name="Dean Martin",
            sequence=1,
            roles=["Dude"],
            notes="('Borrachón')",
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "cast": [
                imdb.Person.Person(
                    personID="0000078",
                    notes="",
                    name="John Wayne",
                    currentRole=imdb.Character.Character(name="John T. Chance"),
                ),
                imdb.Person.Person(
                    personID="0001509",
                    notes="('Borrachón')",
                    name="Dean Martin",
                    currentRole=imdb.Character.Character(name="Dude"),
                ),
            ]
        }
    )

    assert cast.parse(movie) == expected


def test_parse_handles_unknown_roles() -> None:
    expected = [
        cast.Credit(
            person_imdb_id="nm0000472",
            name="Boris Karloff",
            sequence=0,
            notes="",
            roles=[],
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "cast": [
                imdb.Person.Person(
                    personID="0000472",
                    notes="",
                    name="Boris Karloff",
                    currentRole=imdb.Character.Character(),
                ),
            ]
        }
    )

    assert cast.parse(movie) == expected


def test_parse_handles_multiple_roles() -> None:
    expected = [
        cast.Credit(
            person_imdb_id="nm0191520",
            name="Peter Cullen",
            sequence=0,
            notes="",
            roles=["Optimus Prime", "Ironhide"],
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "cast": [
                imdb.Person.Person(
                    personID="0191520",
                    notes="",
                    name="Peter Cullen",
                    currentRole=[
                        imdb.Character.Character(name="Optimus Prime"),
                        imdb.Character.Character(name="Ironhide"),
                    ],
                ),
            ]
        }
    )

    assert cast.parse(movie) == expected


def test_parse_excludes_invalid_credits() -> None:
    expected = [
        cast.Credit(
            person_imdb_id="nm0000951",
            name="Joan Blondell",
            sequence=0,
            notes="",
            roles=["Vida Fleet"],
        ),
        cast.Credit(
            person_imdb_id="nm0511599",
            name="Eric Linden",
            sequence=1,
            roles=["Bud Reeves"],
            notes="",
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "cast": [
                imdb.Person.Person(
                    personID="0000951",
                    notes="",
                    name="Joan Blondell",
                    currentRole=imdb.Character.Character(name="Vida Fleet"),
                ),
                imdb.Person.Person(
                    personID="0511599",
                    notes="",
                    name="Eric Linden",
                    currentRole=imdb.Character.Character(name="Bud Reeves"),
                ),
                imdb.Person.Person(
                    personID="0000007",
                    notes="(uncredited)",
                    name="Humphrey Bogart",
                    currentRole=imdb.Character.Character(name="Shep Adkins"),
                ),
            ]
        }
    )

    assert cast.parse(movie) == expected
