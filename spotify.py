import requests

class SpotifyException(Exception):
    pass

class Spotify:
    ApiBaseUrl = 'https://api.spotify.com'
    AccountsBaseUrl = 'https://accounts.spotify.com'

    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.refresh_token = refresh_token.strip()
        self.__access_token = None

        # get an auth token
        self.__obtain_access_token()

    def __obtain_access_token(self):
        url = '{}/api/token'.format(Spotify.AccountsBaseUrl)
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

        r = requests.post(url, data=data, auth=(self.client_id, self.client_secret))

        if not r.raise_for_status():
            parsed = r.json()
            self.__access_token = parsed['access_token']

    def __bearer_auth_header(self):
        return {
            'Authorization': 'Bearer {}'.format(self.__access_token)
        }

    def search_track(self, query):
        url = '{}/v1/search'.format(Spotify.ApiBaseUrl)

        params = {
            'q': query,
            'type': 'track',
            'limit': 1
        }

        r = requests.get(url, headers=self.__bearer_auth_header(), params=params)

        if not r.raise_for_status():
            parsed = r.json()
            tracks = parsed['tracks']
            if tracks['total'] == 0:
                raise SpotifyException('No search results found for query: "{}"'.format(query))

            return tracks['items'][0]['uri']
