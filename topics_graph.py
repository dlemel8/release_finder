import asyncio
import time

from neo4j.v1 import GraphDatabase

from common import get_request, REPOS

START = time.time()

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
    topics_futures = [get_topics(r) for r in REPOS]
    done, _ = await asyncio.wait(topics_futures)
    assert len(done) == len(topics_futures)
    results = [x.result() for x in done]
    print(results)

    driver = GraphDatabase.driver('bolt://localhost:7687')
    with driver.session() as session:
        for i in range(len(REPOS)):
            merge_information(session, REPOS[i], results[i])

    print("Process took: {:.2f} seconds".format(time.time() - START))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
