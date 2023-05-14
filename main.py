import random
import asyncio

from loguru import logger
from eth_account import Account

from config import WALLETS, TIMES
from chain_to_chain import chain_to_chain
from utils.params import (
    polygon_w3,
    fantom_w3,
    avalanche_w3,
    stargate_polygon_contract,
    stargate_fantom_contract,
    stargate_avalanche_contract,
    stargate_polygon_address,
    stargate_fantom_address,
    stargate_avalanche_address,
    usdc_polygon_contract,
    usdc_fantom_contract,
    usdc_avalanche_contract,
    POLYGON_CHAIN_ID,
    FANTOM_CHAIN_ID,
    AVALANCHE_CHAIN_ID,
)


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

        await chain_to_chain(
            wallet=wallet,
            from_chain_name='POLYGON',
            usdc_from_chain_contract=usdc_polygon_contract,
            to_chain_name='FANTOM',
            from_chain_w3=polygon_w3,
            destination_chain_id=FANTOM_CHAIN_ID,
            stargate_from_chain_contract=stargate_polygon_contract,
            stargate_from_chain_address=stargate_polygon_address,
            from_chain_explorer='polygonscan.com',
            gas=500_000
        )

        polygon_delay = random.randint(1200, 1500)
        logger.info(f'POLYGON DELAY | Waiting for {polygon_delay} seconds.')
        await asyncio.sleep(polygon_delay)

        await chain_to_chain(
            wallet=wallet,
            from_chain_name='FANTOM',
            usdc_from_chain_contract=usdc_fantom_contract,
            to_chain_name='AVALANCHE',
            from_chain_w3=fantom_w3,
            destination_chain_id=AVALANCHE_CHAIN_ID,
            stargate_from_chain_contract=stargate_fantom_contract,
            stargate_from_chain_address=stargate_fantom_address,
            from_chain_explorer='ftmscan.com',
            gas=600_000
        )

        fantom_delay = random.randint(1200, 1500)
        logger.info(f'FANTOM DELAY | Waiting for {fantom_delay} seconds.')
        await asyncio.sleep(fantom_delay)

        await chain_to_chain(
            wallet=wallet,
            from_chain_name='AVALANCHE',
            usdc_from_chain_contract=usdc_avalanche_contract,
            to_chain_name='POLYGON',
            from_chain_w3=avalanche_w3,
            destination_chain_id=POLYGON_CHAIN_ID,
            stargate_from_chain_contract=stargate_avalanche_contract,
            stargate_from_chain_address=stargate_avalanche_address,
            from_chain_explorer='snowtrace.io',
            gas=500_000
        )

        avalanche_delay = random.randint(100, 300)
        logger.info(f'AVALANCE DELAY | Waiting for {avalanche_delay} seconds.')
        await asyncio.sleep(fantom_delay)

        counter += 1

    logger.success(f'DONE | Wallet: {address}')


async def main():
    tasks = []
    for wallet in WALLETS:
        tasks.append(asyncio.create_task(work(wallet)))

    for task in tasks:
        await task

    logger.success(f'*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
