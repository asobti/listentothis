#!/usr/bin/env python

import argparse
from reddit import Reddit
from spotify import Spotify
import sys


class Entity:
    def __init__(self, reddit_title):
        self.reddit_title = reddit_title
        self.search_term = None
        self.spotify_track = None

    def __str__(self):
        return '{} | {} | {}'.format(
                    self.reddit_title.encode('utf-8') if self.reddit_title else 'None',
                    self.search_term.encode('utf-8') if self.search_term else 'None',
                    self.spotify_track
                )


def info(msg):
    print '[INFO ] {}'.format(str(msg).encode('utf-8'))


def error(msg):
    print '[ERROR] {}'.format(str(msg).encode('utf-8'))


def parse_args():
    parser = argparse.ArgumentParser(description='Add subreddit top tracks to a Spotify playlist')

    parser.add_argument('--subreddit', dest='subreddit', required=True,
                        help='The subreddit to query')
    parser.add_argument('--period', dest='period', choices=Reddit.TimePeriods, required=True,
                        help='The time period for top reddit threads')
    parser.add_argument('--limit', dest='limit', type=int, default=25,
                        help='Number of threads to retreive')
    parser.add_argument('--playlist-id', dest='playlist_id', required=True,
                        help='ID of Spotify Playlist to add tracks to')
    parser.add_argument('--spotify-client-id', dest='spotify_client_id', required=True,
                        help='Spotify application client ID')
    parser.add_argument('--spotify-client-secret', dest='spotify_client_secret', required=True,
                        help='Spotify application client secret')
    parser.add_argument('--refresh-token-file', dest='refresh_token_file', required=True,
                        help='Path to file with refresh token')
    parser.add_argument('--search-threshold', dest='search_threshold', type=float, default=0.5,
                        help='Fraction of reddit threads that must convert to Spotify tracks in order to proceed')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', default=False,
                        help='Do a dry run - Spotify playlists are not modified')

    return parser.parse_args()


# Convert a Reddit title to a Spotify search term
# TODO: This could be improved by using a regular expression
# /r/listentothis title format:
# artistName -- trackName [genre tags] (year) comment
def search_term_from_title(title):
    # find where '[' appears
    # Throws exception if not found
    index = title.index('[')

    # take substring from 0 to index
    substring = title[:index]

    # remove any hyphens
    no_hyphen_substr = substring.replace('-', '')

    # trim whitespaces
    # Done by splitting on whitespace, and then joining back
    trimmed = ' '.join(no_hyphen_substr.split())

    # if everything looks fine, this is our search string
    if trimmed and len(trimmed) > 0:
        return trimmed
    else:
        raise Exception('search_term_conversion_fail exception')


def read_refresh_token(path):
    with open(path, 'r') as f:
        return f.read()


def main():
    options = parse_args()

    r = Reddit(options.subreddit)

    info('Fecthing threads from Reddit')
    top_titles = r.top(options.period, options.limit)
    entities = [Entity(title) for title in top_titles]
    info('Found {} threads'.format(len(entities)))
    
    for entity in entities:
        try:
            entity.search_term = search_term_from_title(entity.reddit_title)
        except Exception:
            error('Failed to convert Reddit title "{}" to a search term'.format(title))

    refresh_token = read_refresh_token(options.refresh_token_file)

    try:
        s = Spotify(options.spotify_client_id, options.spotify_client_secret, refresh_token)
    except Exception as e:
        error('Failed to create Spotify agent')
        error(e)
        return 1

    info('Searching Spotify for tracks')
    for entity in entities:
        try:
            entity.spotify_track = s.search_track(entity.search_term)
        except Exception as e:
            error(e)
            error('Skipping...')

    # list to Set to list - done to dedupe
    tracks_found = list(set([entity.spotify_track for entity in entities if entity.spotify_track is not None]))
    info('Found {} Spotify tracks'.format(len(tracks_found)))

    if not (float(len(tracks_found)) / len(entities)) > options.search_threshold:
        error('Search of Spotify tracks under threshold of {}'.format(options.search_threshold))
        return 1

    if not options.dry_run:
        try:
            info('Removing existing tracks from playlist')
            s.clear_playlist(options.playlist_id)
            info('Adding {} new tracks to playlist'.format(len(tracks_found)))
            s.add_tracks_to_playlist(options.playlist_id, tracks_found)
        except Exception as e:
            error(e)
            return 1

    info('Run completed successfully')
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
