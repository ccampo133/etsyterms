import html
import json

import responses

from etsyterms import utils
from etsyterms.etsy import EtsyClient, ETSY_API_BASE_URL


@responses.activate
def test_get_shop_listings():
    api_key = 'DUMMY'
    shop_id = 'StrayHeadcovers'

    with open('tests/test_listings.json', 'r') as file:
        listings_json_resp = json.loads(file.read())

    responses.add(
        method=responses.GET,
        url=f'{ETSY_API_BASE_URL}/shops/{shop_id}/listings/active?api_key={api_key}&limit=100&offset=0',
        json=listings_json_resp,
        status=200
    )

    etsy = EtsyClient(api_key)
    result = etsy.get_shop_listings(shop_id)
    assert len(responses.calls) == 1
    assert len(result) == 17

    for i, listing in enumerate(result):
        assert listing.title == html.unescape(listings_json_resp['results'][i]['title'])
        assert listing.description == html.unescape(listings_json_resp['results'][i]['description'])


@responses.activate
def test_get_shop_listing_active_count():
    api_key = 'DUMMY'
    shop_id = 'StrayHeadcovers'

    with open('tests/test_shop.json', 'r') as file:
        shop_json_resp = json.loads(file.read())

    responses.add(
        method=responses.GET,
        url=f'{ETSY_API_BASE_URL}/shops/{shop_id}?api_key={api_key}',
        json=shop_json_resp,
        status=200
    )

    etsy = EtsyClient(api_key)
    result = etsy.get_shop_listing_active_count(shop_id)
    assert len(responses.calls) == 1
    assert result == shop_json_resp['results'][0]['listing_active_count']


@responses.activate
def test_get_shop_listing_active_count_backoff_retry_once():
    utils.setup_logging('DEBUG')

    api_key = 'DUMMY'
    shop_id = 'StrayHeadcovers'

    with open('tests/test_shop.json', 'r') as file:
        shop_json_resp = json.loads(file.read())

    responses.add(
        method=responses.GET,
        url=f'{ETSY_API_BASE_URL}/shops/{shop_id}?api_key={api_key}',
        status=400,
        headers={'X-Error-Detail': 'You have exceeded your quota'}
    )

    responses.add(
        method=responses.GET,
        url=f'{ETSY_API_BASE_URL}/shops/{shop_id}?api_key={api_key}',
        status=200,
        json=shop_json_resp
    )

    etsy = EtsyClient(api_key)
    result = etsy.get_shop_listing_active_count(shop_id)
    assert len(responses.calls) == 2
    assert result == shop_json_resp['results'][0]['listing_active_count']
