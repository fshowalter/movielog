from movielog import imdb_s3_orchestrator, watchlist
from movielog.cli import confirm, radio_list


def prompt() -> None:
    options = [
        (None, "Go back"),
        (update_titles_and_people, "<cyan>Update titles and people</cyan>"),
        (
            update_watchlist_person_credits,
            "<cyan>Update watchlist person credits</cyan>",
        ),
    ]

    option_function = radio_list.prompt(
        title="IMDb:",
        options=options,
    )

    if option_function:
        option_function()
        prompt()


def update_titles_and_people() -> None:
    if confirm.prompt("<cyan>Download and update IMDb titles and people?</cyan>"):
        imdb_s3_orchestrator.orchestrate_update()


def update_watchlist_person_credits() -> None:
    prompt_text = (
        "<cyan>This will update any non-frozen credits from the IMDb. Continue?</cyan>"
    )
    if confirm.prompt(prompt_text):
        watchlist.refresh_credits()
