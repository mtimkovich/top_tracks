#!/usr/bin/env python3
import argparse
import json
from mako.template import Template
import re
import soundcloud
import yaml


class Track:
    def __init__(self, track, client):
        self.plays = getattr(track, 'playback_count', 0)
        self.downloads = getattr(track, 'download_count', 0)
        self.title = track.title
        self.url = track.permalink_url
        self.stream = track.stream_url

        self.favorites = getattr(track, 'favoritings_count', 0)
        self.uri = track.uri

        self.client = client

    def get_oembed(self):
        embed = self.client.get('/oembed',
                                url=self.url,
                                maxheight=175,
                                maxwidth=500,
                                download='false',
                                show_playcount='true',
                                show_comments='false')
        # This is super hacky
        player = embed.html.replace('visual=true', 'visual=false')
        player = re.sub('&client_id=[^&]*', '', player)
        player += '<br>'

        return player

    def get_stream_url(self):
        stream_url = self.client.get(self.stream, allow_redirects=False)
        return stream_url.location

    def __lt__(self, other):
        return self.plays < other.plays

parser = argparse.ArgumentParser()
parser.add_argument('artist', help='SoundCloud artist')
args = parser.parse_args()

with open('soundcloud.yml') as f:
    config = yaml.load(f)

client = soundcloud.Client(client_id=config['client_id'])
songs = []

user_id = client.get('/resolve', url='http://soundcloud.com/' + args.artist).id
next_href = '/users/{}/tracks'.format(user_id)
while True:
    tracks = client.get(next_href, limit=200, linked_partitioning=1)
    for track in tracks.collection:
        songs.append(Track(track, client))

    try:
        next_href = tracks.next_href
    except AttributeError:
        break

songs = sorted(songs, reverse=True)

template = Template(filename='template.html')
print(template.render(artist=args.artist,
                      songs=songs[:20]))
