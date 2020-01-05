class RateLimitExceededError(Exception):
    def __init__(self):
        # There's probably a smarter way to figure out how long to wait when rate limited. Some public APIs have a
        # header like X-RateLimit-Reset which contains a timestamp when the rate limit resets, however I couldn't find
        # anything like that in Etsy's API documentation (granted, I never hit the rate limit so it could exist).
        # Therefore, unfortunately this error message is a bit of a cop out.
        super(Exception, self).__init__('Etsy API rate limit exceeded. Please try again later')


class EtsyApiError(Exception):
    def __init__(self, status: int, message: str):
        super(Exception, self).__init__(f'HTTP status: {status} - {message}')
