import random
import asyncio
import argparse
import sys

from eth_typing import ChecksumAddress
from loguru import logger
from eth_account import Account
from web3 import AsyncWeb3
from web3.contract import AsyncContract

from config import WALLETS, AMOUNT_TO_SWAP, MIN_AMOUNT
from bridge.bridger import send_usdc_chain_to_chain, is_balance_updated
from utils.params import polygon, fantom, avalanche


async def chain_to_chain(
        wallet: str,
        from_chain_name: str,
        usdc_from_chain_contract: AsyncContract,
        to_chain_name: str,
        from_chain_w3: AsyncWeb3,
        destination_chain_id: int,
        stargate_from_chain_contract: AsyncContract,
        stargate_from_chain_address: ChecksumAddress,
        from_chain_explorer: str,
        gas: int
) -> None:
    """Transfer function. It sends USDC from Polygon to Fantom.
    Stargate docs:  https://stargateprotocol.gitbook.io/stargate/developers

    Args:
        wallet:                         wallet address
        from_chain_name:                Sending chain name
        usdc_from_chain_contract:       Sending chain usdc contract
        to_chain_name:                  Destination chain name
        from_chain_w3:                  Client
        destination_chain_id:           Destination chain id from stargate docs
        stargate_from_chain_contract:   Sending chain stargate router contract
        stargate_from_chain_address:    Address of Stargate Finance: Router at sending chain
        from_chain_explorer:            Sending chain explorer
        gas:                            Amount of gas
    """
    account = Account.from_key(wallet)
    address = account.address

    start_delay = random.randint(1, 200)
    logger.info(f'START DELAY | Waiting for {start_delay} seconds.')
    await asyncio.sleep(start_delay)

    balance = None
    logger_cntr = 0
    while not balance:
        await asyncio.sleep(30)
        if logger_cntr % 3 == 0:
            logger.info(f'BALANCE | Checking {from_chain_name} {address} USDC balance')
        balance = await is_balance_updated(address, usdc_from_chain_contract)
        logger_cntr += 1

    logger.info(
        f'BRIDGING | Trying to bridge {AMOUNT_TO_SWAP / 10 ** 6} USDC from {from_chain_name} to {to_chain_name}')
    bridging_txn_hash = await send_usdc_chain_to_chain(
        wallet=wallet,
        from_chain_w3=from_chain_w3,
        transaction_info={
            "chain_id": destination_chain_id,
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
        stargate_from_chain_contract=stargate_from_chain_contract,
        stargate_from_chain_address=stargate_from_chain_address,
        usdc_from_chain_contract=usdc_from_chain_contract,
        from_chain_name=from_chain_name,
        from_chain_explorer=from_chain_explorer,
        gas=gas
    )
    logger.success(
        f"{from_chain_name} | {address} | Transaction: https://{from_chain_explorer}/tx/{bridging_txn_hash.hex()}"
    )
    logger.success(f"LAYERZEROSCAN | Transaction: https://layerzeroscan.com/tx/{bridging_txn_hash.hex()}")


async def main():
    parser = argparse.ArgumentParser(
        description='Optional use case. Bridge USDC from one chain to another once for specified wallets.'
    )

    mode_mapping = {
        "pf": "polygon-fantom",
        "pa": "polygon-avalanche",
        "fp": "fantom-polygon",
        "fa": "fantom-avalanche",
        "ap": "avalanche-polygon",
        "af": "avalanche-fantom"
    }

    parser.add_argument(
        "--mode",
        type=str,
        choices=mode_mapping.keys(),
        help="Bridging mode"
    )

    args = parser.parse_args()
    if args.mode is None:
        print("Error: the --mode argument is required")
        sys.exit(2)

    mode = mode_mapping[args.mode]

    tasks = []
    for wallet in WALLETS:
        match mode:
            case "polygon-fantom":
                tasks.append(
                    asyncio.create_task(
                        chain_to_chain(
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
                    )
                )
            case "polygon-avalanche":
                tasks.append(
                    asyncio.create_task(
                        chain_to_chain(
                            wallet=wallet,
                            from_chain_name=polygon.name,
                            usdc_from_chain_contract=polygon.usdc_contract,
                            to_chain_name=avalanche.name,
                            from_chain_w3=polygon.w3,
                            destination_chain_id=avalanche.chain_id,
                            stargate_from_chain_contract=polygon.stargate_contract,
                            stargate_from_chain_address=polygon.stargate_address,
                            from_chain_explorer=polygon.explorer,
                            gas=polygon.gas
                        )
                    )
                )
            case "fantom-polygon":
                tasks.append(
                    asyncio.create_task(
                        chain_to_chain(
                            wallet=wallet,
                            from_chain_name=fantom.name,
                            usdc_from_chain_contract=fantom.usdc_contract,
                            to_chain_name=polygon.name,
                            from_chain_w3=fantom.w3,
                            destination_chain_id=polygon.chain_id,
                            stargate_from_chain_contract=fantom.stargate_contract,
                            stargate_from_chain_address=fantom.stargate_address,
                            from_chain_explorer=fantom.explorer,
                            gas=fantom.gas
                        )
                    )
                )
            case "fantom-avalanche":
                tasks.append(
                    asyncio.create_task(
                        chain_to_chain(
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
                    )
                )
            case "avalanche-polygon":
                tasks.append(
                    asyncio.create_task(
                        chain_to_chain(
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
                    )
                )
            case "avalanche-fantom":
                tasks.append(
                    asyncio.create_task(
                        chain_to_chain(
                            wallet=wallet,
                            from_chain_name=avalanche.name,
                            usdc_from_chain_contract=avalanche.usdc_contract,
                            to_chain_name=fantom.name,
                            from_chain_w3=avalanche.w3,
                            destination_chain_id=fantom.chain_id,
                            stargate_from_chain_contract=avalanche.stargate_contract,
                            stargate_from_chain_address=avalanche.stargate_address,
                            from_chain_explorer=avalanche.explorer,
                            gas=avalanche.gas
                        )
                    )
                )

    for task in tasks:
        logger.info(f'Bridging {mode_mapping[args.mode]}')
        await task

    logger.success(f'*** FINISHED ***')


if __name__ == '__main__':
    asyncio.run(main())
