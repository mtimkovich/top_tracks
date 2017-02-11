#!/usr/bin/env python3
import cgi
from mako.template import Template
import requests
import soundcloud
import sys
import yaml

print('Content-Type: text/html')
print()


class Track:
    def __init__(self, track, client):
        self.id = track.id
        self.title = track.title
        self.plays = getattr(track, 'playback_count', 0)

        self.client = client

    def get_stream_url(self):
        stream_url = self.client.get(self.stream, allow_redirects=False)
        return stream_url.location

    def __lt__(self, other):
        return self.plays < other.plays

form = cgi.FieldStorage()
artist = form.getvalue('artist', '')
template = Template(filename='template.html')
title = 'Top Tracks'

if not artist:
    print(template.render())
    sys.exit()

with open('/home/protected/soundcloud.yml') as f:
    config = yaml.load(f)

client = soundcloud.Client(client_id=config['client_id'])
songs = []

try:
    user_id = client.get('/resolve', url='http://soundcloud.com/' + artist).id
except requests.exceptions.HTTPError:
    error = 'User "{}" not found'.format(artist)
    print(template.render(artist=artist,
                          error=error))
    sys.exit()

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

print(template.render(artist=artist,
                      songs=songs[:20]))
