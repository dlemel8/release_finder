import asyncio
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from common import get_request, Queue

QUEUE_NAME = 'releases'
RELEASES_URL_FORMAT = 'https://api.github.com/repos/{:s}/releases'
TAGS_URL_FORMAT = 'https://api.github.com/repos/{:s}/tags'


mongo_client = AsyncIOMotorClient()
mongo_db = mongo_client['mydb']
mongo_collection = mongo_db['repos']


async def upsert_information(name, version, **kargs):
    result = await mongo_collection.find_one_and_update({'name': name},
                                                        {'$set': {'version': version, 'time': datetime.now(), **kargs}},
                                                        upsert=True, return_document=ReturnDocument.BEFORE)
    print(f'repo {name} old record is {result}')
    if not result:
        print(f'new repo {name} to track!')
    else:
        stored_version = result['version']
        if version != stored_version:
            print(f'repo {name} was upgraded from version {stored_version} to version {version}!')


async def handle_repo(repo):
    response = await get_request(RELEASES_URL_FORMAT.format(repo))
    released = [x for x in response if not x['prerelease']]
    if released:
        print(f'repo {repo} releases are {released}')
        latest = max(released, key=lambda x: x['published_at'])
        print(f'repo {repo} latest release is {latest}')
        await upsert_information(repo, latest['name'],
                                 published_at=latest['published_at'], body=latest['body'])
    else:
        response = await get_request(TAGS_URL_FORMAT.format(repo))
        print(f'repo {repo} tags are {response}')
        latest = response[0]
        print(f'repo {repo} latest release is {latest}')
        await upsert_information(repo, latest['name'])


if __name__ == '__main__':
    # asyncio.run(consume_queue(QUEUE_NAME, handle_repo)) # TODO - why isn't this working?
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Queue.consume(QUEUE_NAME, handle_repo))
    loop.close()
