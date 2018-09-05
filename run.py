import asyncio
import time

import aiohttp

START = time.time()

REPOS = [
    'python/cpython',
    # 'golang/go',
    'docker/docker-ce',
    'docker/compose',
    # 'linuxkit/linuxkit',
    # # 'ansible/ansible',
    # 'metacloud/molecule',
    # 'pytest-dev/pytest',
    # # 'jenkinsci/jenkins',
    # 'mysql/mysql-server',
    # 'nginx/nginx',
    # 'haproxy/haproxy',
]

RELEASES_URL_FORMAT = 'https://api.github.com/repos/{:s}/releases'
TAGS_URL_FORMAT = 'https://api.github.com/repos/{:s}/tags'


async def get_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def latest_release(repo):
    response = await get_request(RELEASES_URL_FORMAT.format(repo))
    released = [x for x in response if not x['prerelease']]
    if released:
        latest = max(released, key=lambda x: x['published_at'])
        print(latest['name'], latest['published_at'])
        # print(latest['body'])
    else:
        response = await get_request(TAGS_URL_FORMAT.format(repo))
        latest = response[0]
        print(latest['name'])


async def main():
    release_futures = [latest_release(r) for r in REPOS]
    done, _ = await asyncio.wait(release_futures)
    assert len(done) == len(release_futures)
    print("Process took: {:.2f} seconds".format(time.time() - START))

asyncio.run(main())
