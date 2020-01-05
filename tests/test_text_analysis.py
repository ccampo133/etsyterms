from etsyterms import text_analysis


def test_top_five_terms():
    docs = [
        'The quick brown fox jumps over the lazy dog',
        'The lazy dog jumps over the quick brown fox'
    ]

    terms = text_analysis.get_top_terms(docs)

    assert terms == ['brown', 'dog', 'fox', 'jumps', 'lazy']


def test_top_three_terms():
    docs = [
        'The quick brown fox jumps over the lazy dog',
        'The lazy dog jumps over the quick brown fox'
    ]

    terms = text_analysis.get_top_terms(docs, 3)

    assert terms == ['brown', 'dog', 'fox']


def test_top_three_terms_additional_stop_word():
    docs = [
        'The quick brown fox jumps over the lazy dog',
        'The lazy dog jumps over the quick brown fox'
    ]

    terms = text_analysis.get_top_terms(docs, 3, ['brown'])

    assert terms == ['dog', 'fox', 'jumps']
