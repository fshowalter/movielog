from dataclasses import dataclass

from movielog.repository import api as repository_api


@dataclass
class RepositoryData(object):
    viewings: list[repository_api.Viewing]
    titles: list[repository_api.Title]
    reviews: list[repository_api.Review]
