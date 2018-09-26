import asyncio

from neo4j.v1 import GraphDatabase

from common import connect_rabbitmq, init_queue, init_exchange, get_request

QUEUE_NAME = 'topics'
TOPICS_URL_FORMAT = 'https://api.github.com/repos/{:s}/topics'


async def get_topics(repo):
    headers = {'Accept': 'application/vnd.github.mercy-preview+json'}
    response = await get_request(TOPICS_URL_FORMAT.format(repo), headers)
    return response['names']


def merge_information(session, repo_full_name, topics):
    repo = repo_full_name.split('/')[-1]
    print(session.run("MERGE (r:Repo {name: $name}) RETURN id(r)", name=repo).single().value())
    for t in topics:
        print(session.run("MERGE (t:Topic {name: $name}) RETURN id(t)", name=t).single().value())
        print(session.run("MATCH (r:Repo {name: $repo}), (t:Topic {name: $topic}) MERGE (t)-[:TOPIC_OF]->(r)",
                          repo=repo, topic=t))


async def main():
    connection = await connect_rabbitmq(asyncio.get_running_loop())
    async with connection:
        channel = await connection.channel()
        exchange = await init_exchange(channel)
        queue = await init_queue(channel, exchange, QUEUE_NAME)
        async for message in queue:
            with message.process():
                repo_full_name = message.body.decode("utf-8")
                print(f'got for queue: {repo_full_name}')
                topics = await get_topics(repo_full_name)
                driver = GraphDatabase.driver('bolt://localhost:7687')
                with driver.session() as session:
                    merge_information(session, repo_full_name, topics)


asyncio.run(main())
