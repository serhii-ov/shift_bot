import os
from dotenv import load_dotenv
import asyncio
import logging
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

from handlers import router


load_dotenv()


async def wait_for_redis(host: str, port: int, timeout: int = 10) -> Redis:
    while True:
        try:
            redis = Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True,
            )
            await redis.ping()
            logging.info("Connected to Redis")
            return redis
        except Exception as e:
            logging.warning(f"Waiting for Redis... {e}")
            await asyncio.sleep(2)
            timeout -= 1
            if timeout <= 0:
                raise TimeoutError("Could not connect to Redis within the timeout period")


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=os.getenv("TOKEN"))
    redis = await wait_for_redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        timeout=10,
    )
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    dp.include_router(router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
