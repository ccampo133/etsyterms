import logging
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer

from etsyterms.stop_words import STOP_WORDS

DEFAULT_NUM_TERMS = 5

logger = logging.getLogger(__name__)


def get_top_terms(docs: List[str], n_terms: int = DEFAULT_NUM_TERMS, additional_stop_words: List[str] = None):
    """
    Compute the top terms in a set of documents weighted by their term frequency

    :param docs: The list of documents (strings) to analyze terms from
    :param n_terms: The number of top terms to return
    :param additional_stop_words: Any additional 'stop words' to included in the analysis. These are words you want to
    ignore

    :return: a list of the top `n_terms` terms
    """
    stop_words = STOP_WORDS + [w.lower() for w in additional_stop_words] if additional_stop_words else STOP_WORDS

    vectorizer = TfidfVectorizer(
        max_features=n_terms,
        analyzer='word',
        token_pattern=r'\w{3,}',  # We only care about words >= 3 letters in length
        strip_accents='ascii',
        lowercase=True,
        # Words with a document frequency of 0.1 (meaning they appear in 10% or less of the documents) or lower are
        # probably too rare to include in the analysis. TODO: is 0.1 too aggressive? -ccampo 2019-12-31
        min_df=0.1,
        # In general, scikit doesn't recommend using 'english' for stop words, so we use our own list.
        # See: https://scikit-learn.org/stable/modules/feature_extraction.html#stop-words
        stop_words=stop_words
    )

    response = vectorizer.fit_transform(docs)

    # According to the scikit-learn docs, the feature names (terms) are ordered by their term frequency when the
    # `max_terms` argument is set in TfidfVectorizer.
    terms = vectorizer.get_feature_names()

    if logger.isEnabledFor(logging.DEBUG):
        for i in response.nonzero()[1]:
            logger.debug(f'{terms[i]}:  {response[0, i]}')

    return terms
