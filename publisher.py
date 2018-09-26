import asyncio

import aio_pika

from common import REPOS, connect_rabbitmq, init_exchange


async def main():
    connection = await connect_rabbitmq(asyncio.get_running_loop())
    async with connection:
        channel = await connection.channel()
        exchange = await init_exchange(channel)

        for r in REPOS:
            print(r)
            await exchange.publish(aio_pika.Message(body=f'{r}'.encode()), routing_key='ignored')
            await asyncio.sleep(3)


asyncio.run(main())

