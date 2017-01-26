import requests

class SpotifyException(Exception):
    pass

class Spotify:
    ApiBaseUrl = 'https://api.spotify.com'
    ApiVersion = 'v1'
    AccountsBaseUrl = 'https://accounts.spotify.com'

    def __init__(self, client_id, client_secret, refresh_token):
        self.client_id = client_id.strip()
        self.client_secret = client_secret.strip()
        self.refresh_token = refresh_token.strip()
        self.user_id = None
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

    def __get_user_id(self):
        if self.user_id is None:
            resp = self.__get('me', {})
            self.user_id = resp['id']

        return self.user_id

    def __bearer_auth_header(self):
        return {
            'Authorization': 'Bearer {}'.format(self.__access_token)
        }

    def search_track(self, query):
        params = {
            'q': query.encode('utf-8'),
            'type': 'track',
            'limit': 1
        }

        resp = self.__get('search', params)

        tracks = resp['tracks']

        if tracks['total'] == 0:
            raise SpotifyException('No search results found for query: "{}"'.format(query))

        return tracks['items'][0]['uri']

    def get_playlist_tracks(self, playlist_id):
        user_id = self.__get_user_id()
        endpoint = 'users/{}/playlists/{}/tracks'.format(user_id, playlist_id)

        resp = self.__get(endpoint, {})
        items = resp['items']
        uris = [item['track']['uri'] for item in items]
        return uris

    def clear_playlist(self, playlist_id):
        current_playlist_track_uris = self.get_playlist_tracks(playlist_id)

        if len(current_playlist_track_uris) == 0:
            return

        tracks = [ { "uri": track_uri } for track_uri in current_playlist_track_uris ]
        payload = { 'tracks': tracks }

        user_id = self.__get_user_id()
        endpoint = 'users/{}/playlists/{}/tracks'.format(user_id, playlist_id)
        url = '{}/{}/{}'.format(Spotify.ApiBaseUrl, Spotify.ApiVersion, endpoint)

        r = requests.delete(url, headers=self.__bearer_auth_header(), json=payload)
        r.raise_for_status()

    def add_tracks_to_playlist(self, playlist_id, uris):
        if len(uris) == 0:
            raise SpotifyException('No tracks to add to playlist')

        payload = { 'uris': uris }

        user_id = self.__get_user_id()
        endpoint = 'users/{}/playlists/{}/tracks'.format(user_id, playlist_id)
        url = '{}/{}/{}'.format(Spotify.ApiBaseUrl, Spotify.ApiVersion, endpoint)

        r = requests.post(url, headers=self.__bearer_auth_header(), json=payload)
        r.raise_for_status()

    def __get(self, endpoint, params):
        url = '{}/{}/{}'.format(Spotify.ApiBaseUrl, Spotify.ApiVersion, endpoint)

        r = requests.get(url, headers=self.__bearer_auth_header(), params=params)
        if not r.raise_for_status():
            return r.json()
