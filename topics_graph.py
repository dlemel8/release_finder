import asyncio

from neo4j.v1 import GraphDatabase

from common import get_request, MessageQueue

QUEUE_NAME = 'topics'
TOPICS_URL_FORMAT = 'https://api.github.com/repos/{:s}/topics'


async def get_topics(repo):
    headers = {'Accept': 'application/vnd.github.mercy-preview+json'}
    response = await get_request(TOPICS_URL_FORMAT.format(repo), headers)
    topics = response['names']
    print(f'repo {repo} topics are {topics}')
    return topics


def merge_information(session, repo_full_name, topics):
    repo = repo_full_name.split('/')[-1]
    session.run("MERGE (r:Repo {name: $name})", name=repo)
    print(f'added repo {repo} to the graph')
    for t in topics:
        session.run("MERGE (t:Topic {name: $name}) RETURN id(t)", name=t)
        session.run("MATCH (r:Repo {name: $repo}), (t:Topic {name: $topic}) MERGE (t)-[:TOPIC_OF]->(r)",
                    repo=repo, topic=t)
        print(f'added topic {t} to the graph')


async def handle_repo(repo_full_name):
    topics = await get_topics(repo_full_name)
    driver = GraphDatabase.driver('bolt://localhost:7687')
    with driver.session() as session:
        merge_information(session, repo_full_name, topics)


if __name__ == '__main__':
    asyncio.run(MessageQueue.consume(QUEUE_NAME, handle_repo))
