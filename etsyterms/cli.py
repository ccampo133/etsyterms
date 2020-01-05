import argparse
from typing import Dict, List

from tabulate import tabulate

from etsyterms import utils, text_analysis
from etsyterms.etsy import EtsyClient


def main():
    parser = argparse.ArgumentParser(description='Get the top NUM_TERMS terms from the listings of an Etsy shop (or '
                                                 'shops).')
    parser.add_argument('-a', '--api-key', action='store', required=True, help='An Etsy API key')
    parser.add_argument('-s', '--shop-ids', nargs='+', type=str,
                        help='The list of Etsy shop IDs to analyze, e.g. ModParty. If -f/--file is not '
                             'supplied, at least one shop ID is required.')
    parser.add_argument('-f', '--file', type=str,
                        help='A file of shop IDs, one per line. Either this or the -s/--shop-ids argument must be '
                             'provided.')
    parser.add_argument('-n', '--num-terms', type=int, action='store', default=text_analysis.DEFAULT_NUM_TERMS,
                        help='The number of top terms to return (default: 5)')
    parser.add_argument('--log-level', type=str, action='store', help='Set the log level (DEBUG, INFO, WARNING, '
                                                                      'CRITICAL, ERROR; default: ERROR)')

    args = parser.parse_args()

    if not (args.shop_ids or args.file):
        parser.error('No shop IDs provided. Please add -s/--shop_ids or -f/--file')

    if args.file and not args.shop_ids:
        with open(args.file) as f:
            shop_ids = [line.rstrip('\n') for line in f]
    else:
        shop_ids = args.shop_ids

    utils.setup_logging(args.log_level)

    etsy = EtsyClient(args.api_key)

    terms_by_shop = _get_top_terms_by_shop(shop_ids, args.num_terms, etsy)
    _pretty_print(terms_by_shop)


def _get_top_terms_by_shop(shop_ids: List[str], num_terms: int, etsy: EtsyClient) -> Dict[str, List[str]]:
    terms_by_shop = {}
    for shop_id in shop_ids:
        listings = etsy.get_shop_listings(shop_id)
        docs = [f'{listing.title} {listing.description}' for listing in listings]
        # Testing revealed that the shop ID consistently appeared in the top terms, so we add it to the stop_words to
        # filter it out for each shop.
        terms = text_analysis.get_top_terms(docs=docs, n_terms=num_terms, additional_stop_words=[shop_id])
        terms_by_shop[shop_id] = terms
    return terms_by_shop


def _pretty_print(terms_by_shop: Dict[str, List[str]]):
    headers = ['Shop ID', 'Top Terms']
    data = [(shop_id, ', '.join(terms)) for shop_id, terms in terms_by_shop.items()]
    print(tabulate(data, headers=headers))
