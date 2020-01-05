from typing import List, Generic, TypeVar

T = TypeVar('T')


class Pagination:
    """
    A representation of the Etsy API pagination data

    See: https://www.etsy.com/developers/documentation/getting_started/api_basics#section_pagination
    """
    def __init__(
            self,
            effective_limit: int,
            effective_offset: int,
            next_offset: int,
            effective_page: int,
            next_page: int
    ):
        """
        Create a new pagination instance

        :param effective_limit: The effective page limit
        :param effective_offset: The effective page offset
        :param next_offset: The next page offset
        :param effective_page: The effective page number
        :param next_page: The next page number
        """
        self.effective_limit = effective_limit
        self.effective_offset = effective_offset
        self.next_offset = next_offset
        self.effective_page = effective_page
        self.next_page = next_page

    @classmethod
    def from_json(cls, json):
        """
        Create a new pagination instance from Etsy's JSON representation

        See: https://www.etsy.com/developers/documentation/getting_started/api_basics#section_pagination

        :param json: A JSON representation of Etsy's pagination data
        :return: A new pagination instance
        """
        return cls(
            effective_limit=json['effective_limit'],
            effective_offset=json['effective_offset'],
            next_offset=json['next_offset'],
            effective_page=json['effective_page'],
            next_page=json['next_page']
        )


class Page(Generic[T]):
    """
    A generic page class, which contains a list of results, a total count, and pagination information
    """
    def __init__(self, count: int, results: List[T], pagination: Pagination):
        """
        Create a new page instance.

        :param count: The total number of results in the data set
        :param results: The list of results in the page
        :param pagination: The page's pagination information
        """
        self.count = count
        self.results = results
        self.pagination = pagination
