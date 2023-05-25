import random
import asyncio

from loguru import logger
from eth_account import Account

from config import WALLETS, TIMES
from chain_to_chain import chain_to_chain
from utils.params import polygon, fantom, avalanche


async def work(wallet: str) -> None:
    """Transfer cycle function. It sends USDC from polygon to fantom and then back.
    It runs such cycles N times, where N - number of cycles specified if config.py

    Args:
        wallet: wallet address
    """
    counter = 0

    account = Account.from_key(wallet)
    address = account.address

    while counter < TIMES:

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=polygon.name,
            usdc_from_chain_contract=polygon.usdc_contract,
            to_chain_name=fantom.name,
            from_chain_w3=polygon.w3,
            destination_chain_id=fantom.chain_id,
            stargate_from_chain_contract=polygon.stargate_contract,
            stargate_from_chain_address=polygon.stargate_address,
            from_chain_explorer=polygon.explorer,
            gas=polygon.gas
        )

        polygon_delay = random.randint(1200, 1500)
        logger.info(f'POLYGON DELAY | Waiting for {polygon_delay} seconds.')
        await asyncio.sleep(polygon_delay)

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=fantom.name,
            usdc_from_chain_contract=fantom.usdc_contract,
            to_chain_name=avalanche.name,
            from_chain_w3=fantom.w3,
            destination_chain_id=avalanche.chain_id,
            stargate_from_chain_contract=fantom.stargate_contract,
            stargate_from_chain_address=fantom.stargate_address,
            from_chain_explorer=fantom.explorer,
            gas=fantom.gas
        )

        fantom_delay = random.randint(1200, 1500)
        logger.info(f'FANTOM DELAY | Waiting for {fantom_delay} seconds.')
        await asyncio.sleep(fantom_delay)

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=avalanche.name,
            usdc_from_chain_contract=avalanche.usdc_contract,
            to_chain_name=polygon.name,
            from_chain_w3=avalanche.w3,
            destination_chain_id=polygon.chain_id,
            stargate_from_chain_contract=avalanche.stargate_contract,
            stargate_from_chain_address=avalanche.stargate_address,
            from_chain_explorer=avalanche.explorer,
            gas=avalanche.gas
        )

        avalanche_delay = random.randint(100, 300)
        logger.info(f'AVALANCHE DELAY | Waiting for {avalanche_delay} seconds.')
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
