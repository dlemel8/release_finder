import asyncio

from common import get_request, Queue

DEFAULT_REPOS = [
    'python/cpython',
    # 'golang/go',
    'docker/docker-ce',
    'docker/compose',
    'linuxkit/linuxkit',
    # 'ansible/ansible',
    'metacloud/molecule',
    'pytest-dev/pytest',
    'philpep/testinfra',
    # 'jenkinsci/jenkins',
    'mysql/mysql-server',
    'nginx/nginx',
    'haproxy/haproxy',
]

URL_FORMAT = 'https://api.github.com/repos/{:s}'


async def verify(repos):
    requests = [get_request(URL_FORMAT.format(r)) for r in repos]
    responses = await asyncio.gather(*requests, loop=asyncio.get_running_loop(), return_exceptions=True)
    return [x['full_name'] for x in responses if 'full_name' in x]


async def main(repos):
    print(f'repos are {repos}')

    verified = await verify(repos)
    print(f'verified repos are {verified}')

    await Queue.publish(*verified)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('repos', metavar='<OWNER>/<REPO>', nargs='*', default=DEFAULT_REPOS,
                        help='github repo to process, e.g. "docker/docker-ce"')
    args = parser.parse_args()
    asyncio.run(main(args.repos))
