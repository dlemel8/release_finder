import requests

X = 'docker/docker-ce'
URL = f'https://api.github.com/repos/{X}/releases'

r = requests.get(URL)
released = [x for x in r.json() if not x['prerelease']]
latest = max(released, key=lambda x: x['published_at'])
print(latest['name'])
print(latest['published_at'])
print(latest['body'])
