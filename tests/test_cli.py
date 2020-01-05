import json

import responses

from etsyterms import cli
from etsyterms.etsy import ETSY_API_BASE_URL, EtsyClient


@responses.activate
def test_get_top_terms_for_shop():
    shop_id = 'StrayHeadcovers'
    api_key = 'DUMMY'

    with open('tests/test_listings.json', 'r') as file:
        json_resp = json.loads(file.read())

    responses.add(
        method=responses.GET,
        url=f'{ETSY_API_BASE_URL}/shops/{shop_id}/listings/active?api_key={api_key}&limit=100&offset=0',
        json=json_resp,
        status=200,
        match_querystring=True
    )

    top_terms = cli._get_top_terms_by_shop([shop_id], 5, EtsyClient(api_key))

    assert top_terms == {shop_id: ['driver', 'headcover', 'morty', 'pickle', 'rick']}


# Not a real test... just used to debug pretty print output
def test_pretty_print():
    terms_by_shop = {
        'Foo': ['a', 'b', 'c', 'd', 'e'],
        'Bar': ['1', '2', '3', '4', '5'],
        'Baz': ['A', 'B', 'C', '1', '2']
    }

    print()
    cli._pretty_print(terms_by_shop)
