import imdb

from movielog.moviedata.extended import directors


def test_parse_excludes_invalid_credits() -> None:
    expected = [
        directors.Credit(
            person_imdb_id="nm0001031",
            name="Claude Chabrol",
            sequence=0,
            notes='(segment "L\'Homme qui vendit la Tour Eiffel")',
        ),
    ]

    movie = imdb.Movie.Movie(
        data={
            "directors": [
                imdb.Person.Person(
                    personID="0001031",
                    notes='(segment "L\'Homme qui vendit la Tour Eiffel")',
                    data={"name": "Claude Chabrol"},
                ),
                imdb.Person.Person(
                    personID="0000591",
                    notes='(segment "La Rivière de Diamants") (scenes deleted)',
                    data={"name": "Roman Polanski"},
                ),
            ]
        }
    )

    assert directors.parse(movie) == expected
