#!/usr/bin/env python3
import argparse
import json
import re
import soundcloud
import yaml

class Track:
    def __init__(self, track):
        self.plays = getattr(track, 'playback_count', 0)
        self.downloads = getattr(track, 'download_count', 0)
        self.favorites = getattr(track, 'favoritings_count', 0)
        self.title = track.title
        self.url = track.permalink_url
        self.uri = track.uri
        self.stream = track.stream_url

    def get_oembed(self, client):
        embed = client.get('/oembed', 
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

    def get_stream_url(self, client):
        stream_url = client.get(self.stream, allow_redirects=False)
        return stream_url.location

    # Sort by favorites, because playback_count is returning incorrect numbers
    def __lt__(self, other):
        return self.plays < other.plays
        # return self.favorites < other.favorites

    def dict(self):
        return {'title': self.title, 'plays': self.plays, 'url': self.url}

    def audio_tag(self, client):
        return '<audio controls src="{}"></audio>'.format(self.get_stream_url(client))

    def html(self):
        return '''    <b>{}</b><br>
Plays:  {:,}<br>
URL:    {:}<br>
Stream: {}<br>'''.format(self.title, self.plays, self.url, self.stream)

    def __str__(self):
        return '''    {}
Plays:  {:,}
URL:    {:}
Stream: {}'''.format(self.title, self.plays, self.url, self.stream)


parser = argparse.ArgumentParser()
parser.add_argument('artist', help='soundcloud artist')
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
        songs.append(Track(track))

    try:
        next_href = tracks.next_href
    except AttributeError:
        break

songs = sorted(songs, reverse=True)

# TODO: Use Mako
print('''<html>
<head>
<title>{}</title>
</head>
<body>
'''.format(args.artist))

for i, song in enumerate(songs[:20]):
    print('{:>2}. {}\n'.format(i+1, song.html()))
    print(song.audio_tag(client))
    print('<br>')
    # print(song.get_stream_url(client))
    # print()
    # print(song.get_oembed(client))

print('''</body>
</html>''')
