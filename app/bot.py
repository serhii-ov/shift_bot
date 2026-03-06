import os
from dotenv import load_dotenv
from urllib.parse import quote
import asyncio
import logging
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

from handlers import router


load_dotenv()


async def wait_for_redis(timeout: int = 10) -> Redis:

    password = quote(os.getenv("REDIS_PASSWORD"))
    redis_url = f"redis://:{password}@redis:6379/0"

    for _ in range(timeout):
        try:
            redis = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            await redis.ping()
            logging.info("Connected to Redis")
            return redis

        except Exception as e:
            logging.warning(f"Waiting for Redis... {e}")
            await asyncio.sleep(2)

    raise TimeoutError("Could not connect to Redis")


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=os.getenv("TOKEN"))
    
    redis = await wait_for_redis()
    
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    dp.include_router(router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
