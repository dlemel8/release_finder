import asyncio

import aio_pika
import aiohttp
from aio_pika import ExchangeType


async def get_request(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.json()


class Queue(object):
    @classmethod
    async def consume(cls, queue_name, process_message_func):
        connection = await cls._connect_rabbitmq()
        async with connection:
            channel = await connection.channel()
            exchange = await cls._init_exchange(channel)
            queue = await cls._init_queue(channel, exchange, queue_name)
            async for message in queue:
                with message.process():
                    body = message.body.decode("utf-8")
                    print(f'got from queue: {body}')
                    await process_message_func(body)

    @classmethod
    async def publish(cls, *messages):
        connection = await cls._connect_rabbitmq()
        async with connection:
            channel = await connection.channel()
            exchange = await cls._init_exchange(channel)

            for m in messages:
                print(f'publish to queue: {m}')
                await exchange.publish(aio_pika.Message(body=f'{m}'.encode()), routing_key='ignored')

    @staticmethod
    async def _connect_rabbitmq():
        return await aio_pika.connect_robust('amqp://guest:guest@127.0.0.1/', loop=asyncio.get_running_loop())

    @staticmethod
    async def _init_exchange(channel):
        return await channel.declare_exchange('repos', ExchangeType.FANOUT)

    @staticmethod
    async def _init_queue(channel, exchange, queue_name):
        queue = await channel.declare_queue(queue_name)
        await queue.bind(exchange)
        return queue
