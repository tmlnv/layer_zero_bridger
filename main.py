import random
import asyncio

from loguru import logger
from eth_account import Account

from config import WALLETS, TIMES
from polygon_to_fantom import polygon_to_fantom
from fantom_to_polygon import fantom_to_polygon


async def work(wallet: str) -> None:
    """Transfer cycle function. It sends USDC from polygon to fantom and then back.
    It runs such cycles N times, where N - number of cycles specified if config.py

    Args:
        wallet: wallet address
    """
    counter = 0

    account = Account.from_key(wallet)
    address = account.address

    start_delay = random.randint(1, 200)
    logger.info(f'START DELAY | Waiting for {start_delay} seconds.')
    await asyncio.sleep(start_delay)

    while counter < TIMES:

        await polygon_to_fantom(wallet=wallet)

        polygon_delay = random.randint(1200, 1500)
        logger.info(f'POLYGON DELAY | Waiting for {polygon_delay} seconds.')
        await asyncio.sleep(polygon_delay)

        await fantom_to_polygon(wallet=wallet)

        fantom_delay = random.randint(100, 300)
        logger.info(f'FANTOM DELAY | Waiting for {fantom_delay} seconds.')
        await asyncio.sleep(fantom_delay)

        counter += 1

    logger.info(f'DONE | Wallet: {address}')


async def main():
    tasks = []
    for wallet in WALLETS:
        tasks.append(asyncio.create_task(work(wallet)))

    for task in tasks:
        await task

    logger.info(f'*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
