import requests

class RedditException(Exception):
    pass

class Reddit:
    TimePeriods = set(['day', 'week', 'month', 'year', 'all'])
    BaseUrl = 'https://www.reddit.com'
    ThreadType = "t3"

    def __init__(self, subreddit):
        self.subreddit = subreddit

    def top(self, period, limit):
        if not period in Reddit.TimePeriods:
            raise RedditException('Invalid time period string: {}. Expected one of {}'.format(period, ', '.join(Reddit.TimePeriods)))

        params = { 't': period, 'limit': limit }
        listing = self.__get('top', params)
        titles = [ l['data']['title'] for l in listing['data']['children'] if l['kind'] == Reddit.ThreadType]
        return titles

    def __get(self, dest, params):
        url = '{}/r/{}/{}.json'.format(Reddit.BaseUrl, self.subreddit, dest)

        headers = {
            'User-Agent': 'listentothis-to-spotify',
            'Accept'    : 'application/json'
        }

        r = requests.get(url, params=params, headers=headers)

        if not r.raise_for_status():
            return r.json()
