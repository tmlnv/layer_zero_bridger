import random
import asyncio

from loguru import logger
from eth_account import Account

from config import WALLETS, AMOUNT_TO_SWAP, MIN_AMOUNT
from bridge.bridger import send_usdc_chain_to_chain, is_balance_updated
from utils.params import (
    avalanche_w3,
    stargate_avalanche_contract,
    stargate_avalanche_address,
    usdc_avalanche_contract,
    FANTOM_CHAIN_ID
)


async def avalanche_to_polygon(wallet: str) -> None:
    """Transfer function. It sends USDC from Avalanche to Polygon.
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
            logger.info(f'BALANCE | Checking AVALANCHE {address} USDC balance')
        balance = await is_balance_updated(address, usdc_avalanche_contract)
        logger_cntr += 1

    logger.info(f'BRIDGING | Trying to bridge {AMOUNT_TO_SWAP / 10 ** 6} USDC from AVALANCHE to FANTOM')
    avalanche_to_fantom_txn_hash = await send_usdc_chain_to_chain(
        wallet=wallet,
        from_chain_w3=avalanche_w3,
        transaction_info={
            "chain_id": FANTOM_CHAIN_ID,
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
        stargate_from_chain_contract=stargate_avalanche_contract,
        stargate_from_chain_address=stargate_avalanche_address,
        usdc_from_chain_contract=usdc_avalanche_contract,
        from_chain_name='AVALANCHE',
        from_chain_explorer='snowtrace.io',
        gas=500000
    )
    logger.success(f"AVALANCHE | {address} | Transaction: https://snowtrace.io/tx/{avalanche_to_fantom_txn_hash.hex()}")


async def main():
    tasks = []
    for wallet in WALLETS:
        tasks.append(asyncio.create_task(avalanche_to_polygon(wallet)))

    for task in tasks:
        await task

    logger.success(f'*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
