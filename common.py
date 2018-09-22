import aiohttp

REPOS = [
    # 'python/cpython',
    # # 'golang/go',
    # 'docker/docker-ce',
    'docker/compose',
    # 'linuxkit/linuxkit',
    # # 'ansible/ansible',
    # 'metacloud/molecule',
    # 'pytest-dev/pytest',
    'philpep/testinfra',
    # # 'jenkinsci/jenkins',
    # 'mysql/mysql-server',
    # 'nginx/nginx',
    # 'haproxy/haproxy',
]


async def get_request(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()
