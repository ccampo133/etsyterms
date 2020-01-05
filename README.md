# etsyterms

[![](https://github.com/ccampo133/etsyterms/workflows/Build%20master/badge.svg)](https://github.com/{owner}/{repo}/actions) 

A small Python application to analyze the top terms used by Etsy shops.

# Requirements

Python 3.7

# Usage

I recommend using a [virtualenv](https://docs.python.org/3/library/venv.html):
                    
    python3 -m venv venv  
    # ...or just 'python', assuming that points to a Python 3.7 installation

Then activate it:

    source venv/bin/activate

Next, install from source:
    
    python setup.py install

Then you can use the application as follows:

    usage: etsyterms [-h] -a API_KEY [-s SHOP_IDS [SHOP_IDS ...]] [-f FILE]
                     [-n NUM_TERMS] [--log-level LOG_LEVEL]
    
    Get the top NUM_TERMS terms from the listings of an Etsy shop (or shops).
    
    optional arguments:
      -h, --help            show this help message and exit
      -a API_KEY, --api-key API_KEY
                            An Etsy API key
      -s SHOP_IDS [SHOP_IDS ...], --shop-ids SHOP_IDS [SHOP_IDS ...]
                            The list of Etsy shop IDs to analyze, e.g. ModParty.
                            If -f/--file is not supplied, at least one shop ID is
                            required.
      -f FILE, --file FILE  A file of shop IDs, one per line. Either this or the
                            -s/--shop-ids argument must be provided.
      -n NUM_TERMS, --num-terms NUM_TERMS
                            The number of top terms to return (default: 5)
      --log-level LOG_LEVEL
                            Set the log level (DEBUG, INFO, WARNING, CRITICAL,
                            ERROR; default: ERROR)
      
An example usage is below:
    
    $ etsyterms -a DUMMY_API_KEY -f test_shop_ids.txt --log-level INFO
     
    2020-01-04 18:50:16,003 etsyterms.etsy INFO     Retrieving 330 active listings for shop CaitlynMinimalist.
    2020-01-04 18:50:30,239 etsyterms.etsy INFO     Retrieving 316 active listings for shop MignonandMignon.
    2020-01-04 18:50:43,211 etsyterms.etsy INFO     Retrieving 277 active listings for shop GracePersonalized.
    2020-01-04 18:50:53,578 etsyterms.etsy INFO     Retrieving 48 active listings for shop SoGoodSoWood.
    2020-01-04 18:50:56,088 etsyterms.etsy INFO     Retrieving 115 active listings for shop NorthwindSupply.
    2020-01-04 18:51:00,026 etsyterms.etsy INFO     Retrieving 194 active listings for shop Factory4me.
    2020-01-04 18:51:05,921 etsyterms.etsy INFO     Retrieving 33 active listings for shop VintageStudio717.
    2020-01-04 18:51:07,717 etsyterms.etsy INFO     Retrieving 38 active listings for shop StudYourEars.
    2020-01-04 18:51:09,563 etsyterms.etsy INFO     Retrieving 24 active listings for shop Zenwaii.
    2020-01-04 18:51:11,096 etsyterms.etsy INFO     Retrieving 11 active listings for shop corvidopolis.
    
    Shop ID            Top Terms
    -----------------  ---------------------------------------------
    CaitlynMinimalist  custom, design, handwriting, name, necklace
    MignonandMignon    date, gift, jewelry, necklace, special
    GracePersonalized  gold, jewelry, polished, shop, vermeil
    SoGoodSoWood       best, leather, name, order, personalized
    NorthwindSupply    contact, custom, gift, leather, usa
    Factory4me         curtains, panels, pet, room, window
    VintageStudio717   digital, download, files, images, paper
    StudYourEars       earrings, nickel, pair, products, recommended
    Zenwaii            gift, meditation, mug, print, yoga
    corvidopolis       ink, mushroom, mushrooms, printed, tee

# Methodology

Full disclosure - this sort of data analysis was new to me, so I did some research on analyzing word importance in a 
collection of text. Naturally, I stumbled upon the 
[term frequency–inverse document frequency (tf-idf)](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) statistic, which 
seems to be the ideal fit for this particular problem.

Therefore, my overall approach to the problem is as follows:

1. Retrieve the data set from Etsy's API in full (while observing their rate limits and usage guidelines).
2. Compute the tf-idf statistic for each term in the data set (on a per-shop basis).
3. Rank the terms by weight (according to their tf-idf) and then return the top five for that shop.

In this implementation, the heavy lifting is largely handled by 
[scikit-learn's feature extraction APIs](https://scikit-learn.org/stable/modules/feature_extraction.html#stop-words).

## Selected Shops

I used [Handmade Hunt](https://www.handmadehunt.com/shops) to select a collection of top ranked and trending shops as 
of December 30, 2019. Their ranking is calculated using the following methodology:

> We calculate how many products the shop has sold in a month, and during their lifetime on Etsy. Monthly rank is based 
> on monthly sales, lifetime rank is based on lifetime sales. 

You can read more on their ranking methodology here: https://www.handmadehunt.com/how-we-rank-etsy-shops

### Selected Top Ranked (as of 2019-12-30)

* [CaitlynMinimalist](https://www.etsy.com/shop/CaitlynMinimalist)
* [MignonandMignon](https://www.etsy.com/shop/MignonandMignon)
* [GracePersonalized](https://www.etsy.com/shop/GracePersonalized)
* [SoGoodSoWood](https://www.etsy.com/shop/SoGoodSoWood)
* [NorthwindSupply](https://www.etsy.com/shop/NorthwindSupply)

### Selected Trending (as of 2019-12-30)

* [Factory4me](https://www.etsy.com/shop/Factory4me)
* [VintageStudio717](https://www.etsy.com/shop/VintageStudio717)
* [StudYourEars](https://www.etsy.com/shop/StudYourEars)
* [Zenwaii](https://www.etsy.com/shop/Zenwaii)
* [corvidopolis](https://www.etsy.com/shop/corvidopolis)

## Discussion

This code is fine as-is for a general proof of concept, but if this were an actual production application I would look 
into improving a few areas.

First and foremost, I would look into implementing some sort of cache to sit in front of Etsy's 
API. The API is pretty aggressively rate-limited, relatively slow (~4 seconds to retrieve a page of 100 listings), and
consumes a decent amount of bandwidth (a page of 100 listings is a few hundred KB on average). Having a cache here would
cut down on the total runtime and bandwidth usage of the application significantly. It would also conserve API requests,
playing a little nicer with Etsy's conservative rate limit. Additionally, once the top terms are calculated, so long
as the data that was used to calculate them is cached, the terms can be cached as well.

Next, I'd like to take another look at the "stop words" used. I adopted them from a list provided in one of the
references below, with some of my own additions, but I'm not sure if they fit the domain here appropriately. There is 
some literature that takes about analyzing your data set and producing your own stop words using the "document 
frequency" statistic, which I think is worth looking into.

Finally, while I think Python is a fine language and it is my go-to for this type of PoC work, in a production scenario
I'd probably gravitate towards using a language I feel is more server-friendly such as Kotlin/Java or Go, especially if
this was intended to scale in a multi-tenant environment. The algorithm itself would probably benefit from 
ahead-of-time compilation as well, rather than relying on the Python interpreter. I know NumPy and SciPy both use 
Python's C API to compile their more performace-critical APIs (arrays, for example), and I'm not sure how much 
`scikit-learn` makes use of these in the `TfidfVectorizer` class, but it's an area worthy of further investigation in 
any case.

## References

* https://towardsdatascience.com/tfidf-for-piece-of-text-in-python-43feccaa74f8
* https://kavita-ganesan.com/extracting-keywords-from-text-tfidf/
* http://www.tfidf.com/
* https://en.wikipedia.org/wiki/Tf%E2%80%93idf

# Development

First, set up a [virtualenv](https://docs.python.org/3/library/venv.html)

    python3 -m venv venv

Then activate it:

    source venv/bin/activate
    
## Build

To build/install the application for development:

    python setup.py develop
    
When done, deactivate the virtualenv and enjoy your day:

    deactivate

There's a `clean.sh` script in the root directory which cleans up some of the cruft left behind during the setup. Feel 
free to run this if you deem it necessary.  

## Tests

Running unit tests:

    pip install -r tests/requirements.txt
    pytest

## CI/CD

This project is built by [GitHub Actions](https://github.com/features/actions). Both the `master` branch and any pull 
request branches are built by default. There is no deployment at the moment but if warranted, this same mechanism would
be used to deploy the package to [PyPI](https://pypi.org/). 

You can view all the recent actions [here](https://github.com/ccampo133/etsyterms/actions).
