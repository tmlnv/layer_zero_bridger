import random
import asyncio

from tqdm import tqdm

from config import PRIVATE_KEYS, TIMES
from modules.chain_to_chain import chain_to_chain
from modules.tokens import usdc, usdt
from modules.chains import polygon, avalanche, bsc
from modules.utils import wallet_public_address
from modules.balance_checker import get_balances
from modules.custom_logger import logger


async def draw_tqdm(delay: int, desc: str) -> None:
    """Draw a CLI progress bar"""
    with tqdm(total=delay, desc=desc, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        for _ in range(delay):
            await asyncio.sleep(1)
            pbar.update(1)


async def work(wallet: str) -> None:
    """Transfer cycle function. It sends USDC from Polygon to Avalanche and then to BSC as USDT.
    From BSC USDT tokens are bridged to Polygon into USDC.
    It runs such cycle N times, where N - number of cycles specified if config.py

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
            from_chain=polygon,
            destination_chain_id=avalanche.layer_zero_chain_id,
            source_pool_id=usdc.stargate_pool_id,
            dest_pool_id=usdc.stargate_pool_id,
            stargate_from_chain_contract=polygon.stargate_contract,
            stargate_from_chain_address=polygon.stargate_router_address,
            from_chain_explorer=polygon.explorer,
            gas=polygon.gas
        )

        polygon_delay = random.randint(1200, 1500)
        logger.info(f'POLYGON DELAY | {address} | Waiting for {polygon_delay} seconds.')
        await draw_tqdm(delay=polygon_delay, desc=f"Waiting POLYGON DELAY | {address}")

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=avalanche.name,
            token=usdc.name,
            token_from_chain_contract=avalanche.usdc_contract,
            to_chain_name=bsc.name,
            from_chain=avalanche,
            destination_chain_id=bsc.layer_zero_chain_id,
            source_pool_id=usdc.stargate_pool_id,
            dest_pool_id=usdt.stargate_pool_id,
            stargate_from_chain_contract=avalanche.stargate_contract,
            stargate_from_chain_address=avalanche.stargate_router_address,
            from_chain_explorer=avalanche.explorer,
            gas=avalanche.gas
        )

        avalanche_delay = random.randint(1200, 1500)
        logger.info(f'AVALANCHE DELAY | {address} | Waiting for {avalanche_delay} seconds.')
        await draw_tqdm(delay=polygon_delay, desc=f"Waiting AVALANCHE DELAY | {address}")

        await chain_to_chain(
            wallet=wallet,
            from_chain_name=bsc.name,
            token=usdt.name,
            token_from_chain_contract=bsc.usdt_contract,
            to_chain_name=polygon.name,
            from_chain=bsc,
            destination_chain_id=polygon.layer_zero_chain_id,
            source_pool_id=usdt.stargate_pool_id,
            dest_pool_id=usdc.stargate_pool_id,
            stargate_from_chain_contract=bsc.stargate_contract,
            stargate_from_chain_address=bsc.stargate_router_address,
            from_chain_explorer=bsc.explorer,
            gas=bsc.gas
        )

        bsc_delay = random.randint(100, 300)
        logger.info(f'BSC DELAY | {address} | Waiting for {bsc_delay} seconds.')
        await draw_tqdm(delay=polygon_delay, desc=f"Waiting BSC DELAY | {address}",)

        counter += 1

    logger.success(f'DONE | {address}')


async def main():
    await get_balances()
    await asyncio.gather(*[work(wallet) for wallet in PRIVATE_KEYS], return_exceptions=True)

    logger.success('*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
