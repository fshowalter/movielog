from movielog.moviedata.extended.tables import (
    countries_table,
    directing_credits_table,
    performing_credits_table,
    release_dates_table,
    sort_titles_table,
    writing_credits_table,
)

update_countries = countries_table.update

update_directing_credits = directing_credits_table.update

update_performing_credits = performing_credits_table.update

update_writing_credits = writing_credits_table.update

update_release_dates = release_dates_table.update

update_sort_titles = sort_titles_table.update
