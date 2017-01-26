# listentothis

A python script to update Spotify playlists with top threads from /r/listentothis

### Usage

```
usage: main.py [-h] --subreddit SUBREDDIT --period {week,all,year,day,month}
               [--limit LIMIT] --playlist-id PLAYLIST_ID --spotify-client-id
               SPOTIFY_CLIENT_ID --spotify-client-secret SPOTIFY_CLIENT_SECRET
               --refresh-token-file REFRESH_TOKEN_FILE
               [--search-threshold SEARCH_THRESHOLD] [--dry-run]

Add subreddit top tracks to a Spotify playlist

optional arguments:
  -h, --help            show this help message and exit
  --subreddit SUBREDDIT
                        The subreddit to query
  --period {week,all,year,day,month}
                        The time period for top reddit threads
  --limit LIMIT         Number of threads to retreive
  --playlist-id PLAYLIST_ID
                        ID of Spotify Playlist to add tracks to
  --spotify-client-id SPOTIFY_CLIENT_ID
                        Spotify application client ID
  --spotify-client-secret SPOTIFY_CLIENT_SECRET
                        Spotify application client secret
  --refresh-token-file REFRESH_TOKEN_FILE
                        Path to file with refresh token
  --search-threshold SEARCH_THRESHOLD
                        Fraction of reddit threads that must convert to
                        Spotify tracks in order to proceed
  --dry-run             Do a dry run - Spotify playlists are not modified
  ```
  
  Example command to update a playlist with top Weekly tracks:
  
  ```
  python main.py \
    # /r/listentothis subreddit
    --subreddit listentothis \
    # weekly top threads
    --period week \
    # limit search results to top 50 threads
    --limit 50 \
    # Spotify playlist id
    --playlist-id 2f1Ioxhg8evQ6TGVVVPT6j \
    # Spotify app Client ID
    --spotify-client-id d16c968bff5c4ba4909d6a083e355ff9 \
    # Spotify app Client Secret
    --spotify-client-secret 3cfea8f35fe04afb98b3eb1893420ef0 \
    # Path to file containing the refresh token
    --refresh-token-file refresh_token \
    # At least 50% of reddit threads should conver to Spotify tracks
    --search-threshold 0.5
 ```
