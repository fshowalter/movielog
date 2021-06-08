import imdb

from movielog.moviedata.extended import writers


def test_parse_handles_groups() -> None:
    expected = [
        writers.Credit(
            person_imdb_id="nm0299154",
            name="Jules Furthman",
            group=0,
            sequence=0,
            notes="(screenplay)",
        ),
        writers.Credit(
            person_imdb_id="nm0102824",
            name="Leigh Brackett",
            group=0,
            sequence=1,
            notes="(screenplay)",
        ),
        writers.Credit(
            person_imdb_id="nm0564800",
            name="B.H. McCampbell",
            group=1,
            sequence=0,
            notes="(short story) (as B. H. McCampbell)",
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "writers": [
                imdb.Person.Person(
                    personID="0299154",
                    notes="(screenplay)",
                    data={"name": "Jules Furthman"},
                ),
                imdb.Person.Person(
                    personID="0102824",
                    notes="(screenplay)",
                    data={"name": "Leigh Brackett"},
                ),
                imdb.Person.Person(),
                imdb.Person.Person(
                    personID="0564800",
                    notes="(short story) (as B. H. McCampbell)",
                    data={"name": "B.H. McCampbell"},
                ),
            ]
        }
    )

    assert expected == writers.parse(movie)


def test_parse_excludes_invalid_credits() -> None:
    expected = [
        writers.Credit(
            person_imdb_id="nm1321655",
            name="Christopher Markus",
            group=0,
            sequence=0,
            notes="(screenplay by)",
        ),
        writers.Credit(
            person_imdb_id="nm1321656",
            name="Stephen McFeely",
            group=0,
            sequence=1,
            notes="(screenplay by)",
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "writers": [
                imdb.Person.Person(
                    personID="1321655",
                    notes="(screenplay by)",
                    data={"name": "Christopher Markus"},
                ),
                imdb.Person.Person(
                    personID="1321656",
                    notes="(screenplay by)",
                    data={"name": "Stephen McFeely"},
                ),
                imdb.Person.Person(),
                imdb.Person.Person(
                    personID="0498278",
                    notes="(based on the Marvel comics by)",
                    data={"name": "Stan Lee"},
                ),
                imdb.Person.Person(
                    personID="0456158",
                    notes="(based on the Marvel comics by)",
                    data={"name": "Jack Kirby"},
                ),
            ]
        }
    )

    assert expected == writers.parse(movie)
