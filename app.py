import asyncio

import latest_release
import topics_graph
from common import Queue


async def main():
    futures = list()
    for module in [latest_release, topics_graph]:
        queue_name = getattr(module, 'QUEUE_NAME')
        process_message_func = getattr(module, 'handle_repo')
        futures.append(Queue.consume(queue_name, process_message_func))
    await asyncio.wait(futures)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
