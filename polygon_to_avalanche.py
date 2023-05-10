import random
import asyncio

from loguru import logger
from eth_account import Account

from config import WALLETS, AMOUNT_TO_SWAP, MIN_AMOUNT
from bridge.bridger import send_usdc_chain_to_chain, is_balance_updated
from utils.params import (
    polygon_w3,
    stargate_polygon_contract,
    stargate_polygon_address,
    usdc_polygon_contract,
    AVALANCHE_CHAIN_ID
)


async def polygon_to_avalanche(wallet: str) -> None:
    """Transfer function. It sends USDC from Polygon to Avalanche.
    Stargate docs:  https://stargateprotocol.gitbook.io/stargate/developers

    Args:
        wallet: wallet address
    """
    account = Account.from_key(wallet)
    address = account.address

    start_delay = random.randint(1, 200)
    logger.info(f'START DELAY | Waiting for {start_delay} seconds.')
    await asyncio.sleep(start_delay)

    balance = None
    logger_cntr = 0
    while not balance:
        await asyncio.sleep(10)
        if logger_cntr % 6 == 0:
            logger.info(f'BALANCE | Checking POLYGON {address} USDC balance')
        balance = await is_balance_updated(address, usdc_polygon_contract)
        logger_cntr += 1

    logger.info(f'BRIDGING | Trying to bridge {AMOUNT_TO_SWAP / 10 ** 6} USDC from POLYGON to AVALANCHE')
    polygon_to_avalanche_txn_hash = await send_usdc_chain_to_chain(
        wallet=wallet,
        from_chain_w3=polygon_w3,
        transaction_info={
            "chain_id": AVALANCHE_CHAIN_ID,
            "source_pool_id": 1,
            "dest_pool_id": 1,
            "refund_address": address,
            "amount_in": AMOUNT_TO_SWAP,
            "amount_out_min": MIN_AMOUNT,
            "lz_tx_obj": [
                0,
                0,
                '0x0000000000000000000000000000000000000001'
            ],
            "to": address,
            "data": "0x"
        },
        stargate_from_chain_contract=stargate_polygon_contract,
        stargate_from_chain_address=stargate_polygon_address,
        usdc_from_chain_contract=usdc_polygon_contract,
        from_chain_name='POLYGON',
        from_chain_explorer='polygonscan.com'
    )
    logger.info(f"POLYGON | {address} | Transaction: https://polygonscan.com/tx/{polygon_to_avalanche_txn_hash.hex()}")


async def main():
    tasks = []
    for wallet in WALLETS:
        tasks.append(asyncio.create_task(polygon_to_avalanche(wallet)))

    for task in tasks:
        await task

    logger.info(f'*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
