import asyncio
import time
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from common import REPOS, get_request

START = time.time()

RELEASES_URL_FORMAT = 'https://api.github.com/repos/{:s}/releases'
TAGS_URL_FORMAT = 'https://api.github.com/repos/{:s}/tags'


async def upsert_information(collection, name, version, **kargs):
    result = await collection.find_one_and_update({'name': name},
                                                  {'$set': {'version': version, 'time': datetime.now(), **kargs}},
                                                  upsert=True, return_document=ReturnDocument.AFTER)
    print('result %s' % repr(result))


async def latest_release(repo, collection):
    response = await get_request(RELEASES_URL_FORMAT.format(repo))
    released = [x for x in response if not x['prerelease']]
    if released:
        latest = max(released, key=lambda x: x['published_at'])
        await upsert_information(collection, repo, latest['name'],
                                 published_at=latest['published_at'], body=latest['body'])
    else:
        response = await get_request(TAGS_URL_FORMAT.format(repo))
        latest = response[0]
        await upsert_information(collection, repo, latest['name'])


async def main():
    client = AsyncIOMotorClient()
    db = client['mydb']
    collection = db['repos']

    release_futures = [latest_release(r, collection) for r in REPOS]
    done, _ = await asyncio.wait(release_futures)
    assert len(done) == len(release_futures)
    print("Process took: {:.2f} seconds".format(time.time() - START))


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
