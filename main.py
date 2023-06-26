import random
import asyncio

from loguru import logger

from config import WALLETS, TIMES
from chain_to_chain import chain_to_chain
from utils.params import polygon, avalanche, bsc, usdc, usdt
from utils.utils import wallet_public_address


async def work(wallet: str) -> None:
    """Transfer cycle function. It sends USDC from Polygon Avalanche and then to BSC as USDT.
    From BSC USDT tokens are bridged to Polygon into USDC.
    It runs such cycles N times, where N - number of cycles specified if config.py

    Args:
        wallet: wallet address
    """
    counter = 0

    address = wallet_public_address(wallet)

    while counter < TIMES:

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=polygon.name,
            token=usdc.name,
            token_from_chain_contract=polygon.usdc_contract,
            to_chain_name=avalanche.name,
            from_chain_w3=polygon.w3,
            destination_chain_id=avalanche.chain_id,
            source_pool_id=usdc.stargate_pool_id,
            dest_pool_id=usdc.stargate_pool_id,
            stargate_from_chain_contract=polygon.stargate_contract,
            stargate_from_chain_address=polygon.stargate_address,
            from_chain_explorer=polygon.explorer,
            gas=polygon.gas
        )

        polygon_delay = random.randint(1200, 1500)
        logger.info(f'POLYGON DELAY | {address} | Waiting for {polygon_delay} seconds.')
        await asyncio.sleep(polygon_delay)

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=avalanche.name,
            token=usdc.name,
            token_from_chain_contract=avalanche.usdc_contract,
            to_chain_name=bsc.name,
            from_chain_w3=avalanche.w3,
            destination_chain_id=bsc.chain_id,
            source_pool_id=usdc.stargate_pool_id,
            dest_pool_id=usdt.stargate_pool_id,
            stargate_from_chain_contract=avalanche.stargate_contract,
            stargate_from_chain_address=avalanche.stargate_address,
            from_chain_explorer=avalanche.explorer,
            gas=avalanche.gas
        )

        avalanche_delay = random.randint(1200, 1500)
        logger.info(f'AVALANCHE DELAY | {address} | Waiting for {avalanche_delay} seconds.')
        await asyncio.sleep(avalanche_delay)

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=bsc.name,
            token=usdt.name,
            token_from_chain_contract=bsc.usdt_contract,
            to_chain_name=polygon.name,
            from_chain_w3=bsc.w3,
            destination_chain_id=polygon.chain_id,
            source_pool_id=usdt.stargate_pool_id,
            dest_pool_id=usdc.stargate_pool_id,
            stargate_from_chain_contract=bsc.stargate_contract,
            stargate_from_chain_address=bsc.stargate_address,
            from_chain_explorer=bsc.explorer,
            gas=bsc.gas
        )

        bsc_delay = random.randint(100, 300)
        logger.info(f'BSC DELAY | {address} | Waiting for {bsc_delay} seconds.')
        await asyncio.sleep(bsc_delay)

        counter += 1

    logger.success(f'DONE | {address}')


async def main():
    tasks = []
    for wallet in WALLETS:
        tasks.append(asyncio.create_task(work(wallet)))

    for task in tasks:
        await task

    logger.success(f'*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
