import asyncio

from common import Queue

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

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('repos', metavar='<OWNER>/<REPO>', nargs='*', default=DEFAULT_REPOS,
                        help='github repo to process, e.g. "docker/docker-ce"')
    args = parser.parse_args()

    print(f'repos are {args.repos}')
    asyncio.run(Queue.publish(*args.repos))
