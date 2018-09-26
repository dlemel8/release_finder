import aio_pika
import aiohttp
from aio_pika import ExchangeType

REPOS = [
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


async def get_request(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()


async def connect_rabbitmq(loop):
    return await aio_pika.connect_robust('amqp://guest:guest@127.0.0.1/', loop=loop)


async def init_exchange(channel):
    return await channel.declare_exchange('repos', ExchangeType.FANOUT)


async def init_queue(channel, exchange, queue_name):
    queue = await channel.declare_queue(queue_name)
    await queue.bind(exchange)
    return queue
