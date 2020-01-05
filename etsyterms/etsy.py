import html
import logging
from typing import List

import backoff as backoff
import requests
from requests import Response

from etsyterms.exceptions import RateLimitExceededError, EtsyApiError
from etsyterms.pagination import Page, Pagination

ETSY_API_BASE_URL = 'https://openapi.etsy.com/v2'
MAX_TRIES = 5

logger = logging.getLogger(__name__)


def _on_request_giveup(details):
    message = 'Gave up calling {target} after {tries} tries'.format(**details)
    raise RuntimeError(message)


def _on_backoff(details):
    logger.info('Backing off {wait:0.1f} seconds afters {tries} tries calling function {target} with args {args} and '
                'kwargs {kwargs}'.format(**details))


def _maybe_handle_error(response: Response):
    if response.status_code != 200:
        # Etsy returns a 400 if you exceed their 10 req/sec rate limit, but there is no good way to tell if
        # the error is actually rate limiting or something else in the request (bad formatting, etc) besides
        # checking the error message :\. So we do that (ugh), and backoff/retry if that happens, otherwise
        # just bubble up the exception.
        if response.status_code == 400 \
                and response.headers['X-Error-Detail'].startswith('You have exceeded your quota'):
            raise RateLimitExceededError()
        else:
            raise EtsyApiError(response.status_code, response.headers['X-Error-Detail'])


class Listing:
    """
    Represents a simplified version of an Etsy shop listing
    """

    def __init__(self, title: str, description: str):
        """
        Create a new listing

        :param title: The listing's title
        :param description: The listing's description
        """
        # There is a lot more information for listings, but for this project we only care about title and description
        self.title = title
        self.description = description

    @classmethod
    def from_json(cls, json):
        """
        Create a new listing from Etsy's JSON representation.

        See: https://www.etsy.com/developers/documentation/reference/listing

        :param json: The JSON format of the listing, expected to be from Etsy's API
        """
        # Etsy's API returns values as HTML-encoded, so we handle that here.
        return cls(title=html.unescape(json['title']), description=html.unescape(json['description']))


class EtsyClient:
    """
    A simple client for interfacing with a few select Etsy API endpoints
    """

    def __init__(self, api_key: str):
        """
        Create a new Etsy client

        :param api_key: Your Etsy API key
        """
        self.api_key = api_key

    @backoff.on_exception(backoff.expo, RateLimitExceededError, max_tries=MAX_TRIES, on_giveup=_on_request_giveup,
                          on_backoff=_on_backoff)
    def get_shop_listings_page(self, shop_id: str, limit: int = 100, offset: int = 0) -> Page[Listing]:
        """
        Get a single page of shop listings

        :param shop_id: The Etsy shop ID
        :param limit: The number of listings to return (useful for pagination, default: 100)
        :param offset: The offset of listings from zero (useful for pagination, default: 0)
        :return: A page of Etsy listings with size `limit`
        """
        params = {'api_key': self.api_key, 'limit': limit, 'offset': offset}
        response = requests.get(f'{ETSY_API_BASE_URL}/shops/{shop_id}/listings/active', params=params)

        _maybe_handle_error(response)

        json = response.json()
        listings = [Listing.from_json(result_json) for result_json in json['results']]
        pagination = Pagination.from_json(json['pagination'])
        return Page(json['count'], listings, pagination)

    @backoff.on_exception(backoff.expo, RateLimitExceededError, max_tries=MAX_TRIES, on_giveup=_on_request_giveup,
                          on_backoff=_on_backoff)
    def get_shop_listing_active_count(self, shop_id: str) -> int:
        """
        Get the active listing count for a shop

        :param shop_id: The shop to get the number of active listings for
        :return: The number of active listings for the shop
        """
        params = {'api_key': self.api_key}
        response = requests.get(f'{ETSY_API_BASE_URL}/shops/{shop_id}', params=params)
        _maybe_handle_error(response)
        json = response.json()
        return json['results'][0]['listing_active_count']

    def get_shop_listings(self, shop_id: str) -> List[Listing]:
        """
        Get all the active listings for a shop

        :param shop_id: The Etsy shop ID
        :return: A list of all the active listings for the specified shop
        """

        def _get_all_shop_listings(limit: int = 100, offset: int = 0, pages=None) -> List[Page[Listing]]:
            # No mutable default arguments. See:
            # https://docs.quantifiedcode.com/python-anti-patterns/correctness/mutable_default_value_as_argument.html
            if pages is None:
                pages = []

            page = self.get_shop_listings_page(shop_id, limit, offset)
            pages.append(page)

            if page.pagination.next_offset is not None:
                _get_all_shop_listings(limit, page.pagination.next_offset, pages)

            return pages

        if logger.isEnabledFor(logging.INFO):
            listing_active_count = self.get_shop_listing_active_count(shop_id)
            logger.info(f'Retrieving {listing_active_count} active listings for shop {shop_id}.')

        listing_pages = _get_all_shop_listings()

        return [listing for page in listing_pages for listing in page.results]
