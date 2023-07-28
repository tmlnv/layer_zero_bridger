""" Bungee Refuel Module
    Docs: https://docs.socket.tech/socket-api/contract-addresses
"""
import asyncio
import sys
from typing import Coroutine
import random

import aiohttp
from web3 import Web3

from modules.chains import Chain, polygon, avalanche, bsc, arbitrum, optimism
from config import PRIVATE_KEYS, BUNGEE_AMOUNT
from modules.custom_logger import logger
from modules.utils import wallet_public_address, get_token_price


async def get_bungee_refuel_amount(token_symbol: str):
    return round(BUNGEE_AMOUNT / await get_token_price(token_symbol=token_symbol), 5)


async def _get_bungee_data() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://refuel.socket.tech/chains") as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                raise ValueError("Could not fetch Bungee params")


async def _get_bungee_limits(from_chain: Chain, to_chain: Chain) -> (int, int):
    bungee_params = await _get_bungee_data()

    for chain in bungee_params['result']:
        if chain['chainId'] == from_chain.bungee_chain_id:
            limits: list = chain['limits']

            for limit in limits:
                if limit['chainId'] == to_chain.bungee_chain_id:
                    if not limit['isEnabled']:
                        logger.error(msg := f"Destination chain {to_chain.name} is not enabled")
                        raise ValueError(msg)
                    destination_chain_limits: dict = limit

    logger.info(f"LIMITS {destination_chain_limits['minAmount']}, {destination_chain_limits['maxAmount']}")
    return int(destination_chain_limits['minAmount']), int(destination_chain_limits['maxAmount'])


async def _create_transaction(address: str, from_chain: Chain, to_chain: Chain, amount: int | float) -> dict:
    amount *= (1 + random.uniform(0, 0.1))

    min_bungee_limit, max_bungee_limit = await _get_bungee_limits(from_chain=from_chain, to_chain=to_chain)

    min_bungee_limit = min_bungee_limit / 10 ** from_chain.native_token_decimals
    max_bungee_limit = max_bungee_limit / 10 ** from_chain.native_token_decimals

    if amount < min_bungee_limit or amount > max_bungee_limit:
        logger.error(msg := (
            f"BUNGEE AMOUNTS | {address} |Transferring {amount} {from_chain.native_asset_symbol} is not possible."
            f" Min is {min_bungee_limit} {from_chain.native_asset_symbol}, "
            f"Max is {max_bungee_limit} {from_chain.native_asset_symbol}"
        ))
        raise ValueError(msg)

    transaction = await from_chain.bungee_contract.functions.depositNativeToken(
        to_chain.bungee_chain_id, address
    ).build_transaction(
        {
            'from': address,
            'gas': from_chain.gas * 2,
            'gasPrice': await from_chain.w3.eth.gas_price,
            'value': Web3.to_wei(amount, 'ether'),
            'nonce': await from_chain.w3.eth.get_transaction_count(address),
        }
    )
    logger.info(f"BUNGEE REFUEL | {address} | Transaction created")
    return transaction


async def _send_transaction(address: str, from_chain: Chain, transaction: dict, private_key: str) -> None:
    signed_transaction = from_chain.w3.eth.account.sign_transaction(transaction, private_key)
    logger.info(f'BUNGEE REFUEL | {address} | Transaction signed')
    try:
        transaction_hash = await from_chain.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    except Exception as e:
        logger.error(
            f"BUNGEE REFUEL | {address} | Problem sending transaction. Probably wallet balance is too low. {e}"
        )
    logger.info(f'BUNGEE REFUEL | {address} | Transaction: https://{from_chain.explorer}/tx/{transaction_hash.hex()}')
    receipt = await from_chain.w3.eth.wait_for_transaction_receipt(transaction_hash)

    if receipt.status == 1:
        logger.success(f"BUNGEE REFUEL | {address} | Transaction succeeded")
    else:
        logger.error(f"BUNGEE REFUEL | {address} | Transaction failed")


async def bungee_refuel(from_chain: Chain, to_chain: Chain, private_key: str, amount: int | float) -> None:
    address = wallet_public_address(private_key)

    logger.info(f'BUNGEE REFUEL | {address} | Starting refuel from {from_chain.name} to {to_chain.name}')
    transaction = await _create_transaction(address=address, from_chain=from_chain, to_chain=to_chain, amount=amount)

    await _send_transaction(address=address, from_chain=from_chain, transaction=transaction, private_key=private_key)


async def main(args: str):
    mode_mapping = {
        "pa": "polygon-avalanche",
        "pb": "polygon-bsc",
        "parb": "polygon-arbitrum",
        "po": "polygon-optimism",
        "ap": "avalanche-polygon",
        "ab": "avalanche-bsc",
        "aarb": "avalanche-arbitrum",
        "ao": "avalanche-optimism",
        "bp": "bsc-polygon",
        "ba": "bsc-avalanche",
        "barb": "bsc-arbitrum",
        "bo": "bsc-optimism",
        "arbp": "arbitrum-polygon",
        "arba": "arbitrum-avalanche",
        "arbb": "arbitrum-bsc",
        "arbo": "arbuitrum-optimism",
        "op": "optimism-polygon",
        "oa": "optimism-avalanche",
        "ob": "optimism-bsc",
        "oarb": "optimism-arbitrum"
    }

    if args is None:
        logger.error("Error: the route argument is required")
        sys.exit(2)
    elif args not in mode_mapping.keys():
        logger.error(
            f"Unsupported route. Supported routes:\n{list(mode_mapping.values())}\n"
            "Usage example: type 'pa' for 'polygon-avalanche' route"
        )
        sys.exit(2)

    mode = mode_mapping[args]

    tasks: list[Coroutine] = []
    for private_key in PRIVATE_KEYS:
        match mode:
            case "polygon-avalanche":
                tasks.append(
                    bungee_refuel(
                        from_chain=polygon,
                        to_chain=avalanche,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(polygon.native_asset_symbol)
                    )
                )
            case "polygon-bsc":
                tasks.append(
                    bungee_refuel(
                        from_chain=polygon,
                        to_chain=bsc,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(polygon.native_asset_symbol)
                    )
                )
            case "polygon-arbitrum":
                tasks.append(
                    bungee_refuel(
                        from_chain=polygon,
                        to_chain=arbitrum,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(polygon.native_asset_symbol)
                    )
                )
            case "polygon-optimism":
                tasks.append(
                    bungee_refuel(
                        from_chain=polygon,
                        to_chain=optimism,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(polygon.native_asset_symbol)
                    )
                )
            case "avalanche-polygon":
                tasks.append(
                    bungee_refuel(
                        from_chain=avalanche,
                        to_chain=polygon,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(avalanche.native_asset_symbol)
                    )
                )
            case "avalanche-bsc":
                tasks.append(
                    bungee_refuel(
                        from_chain=avalanche,
                        to_chain=bsc,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(avalanche.native_asset_symbol)
                    )
                )
            case "avalanche-arbitrum":
                tasks.append(
                    bungee_refuel(
                        from_chain=avalanche,
                        to_chain=arbitrum,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(avalanche.native_asset_symbol)
                    )
                )
            case "avalanche-optimism":
                tasks.append(
                    bungee_refuel(
                        from_chain=avalanche,
                        to_chain=optimism,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(avalanche.native_asset_symbol)
                    )
                )
            case "bsc-polygon":
                tasks.append(
                    bungee_refuel(
                        from_chain=bsc,
                        to_chain=polygon,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(bsc.native_asset_symbol)
                    )
                )
            case "bsc-avalanche":
                tasks.append(
                    bungee_refuel(
                        from_chain=bsc,
                        to_chain=avalanche,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(bsc.native_asset_symbol)
                    )
                )
            case "bsc-arbitrum":
                tasks.append(
                    bungee_refuel(
                        from_chain=bsc,
                        to_chain=arbitrum,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(bsc.native_asset_symbol)
                    )
                )
            case "bsc-optimism":
                tasks.append(
                    bungee_refuel(
                        from_chain=bsc,
                        to_chain=optimism,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(bsc.native_asset_symbol)
                    )
                )
            case "arbitrum-polygon":
                tasks.append(
                    bungee_refuel(
                        from_chain=arbitrum,
                        to_chain=polygon,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(arbitrum.native_asset_symbol)
                    )
                )
            case "arbitrum-avalanche":
                tasks.append(
                    bungee_refuel(
                        from_chain=arbitrum,
                        to_chain=avalanche,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(arbitrum.native_asset_symbol)
                    )
                )
            case "arbitrum-bsc":
                tasks.append(
                    bungee_refuel(
                        from_chain=arbitrum,
                        to_chain=bsc,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(arbitrum.native_asset_symbol)
                    )
                )
            case "arbitrum-optimism":
                tasks.append(
                    bungee_refuel(
                        from_chain=arbitrum,
                        to_chain=optimism,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(arbitrum.native_asset_symbol)
                    )
                )
            case "optimism-polygon":
                tasks.append(
                    bungee_refuel(
                        from_chain=optimism,
                        to_chain=polygon,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(optimism.native_asset_symbol)
                    )
                )
            case "optimism-avalanche":
                tasks.append(
                    bungee_refuel(
                        from_chain=optimism,
                        to_chain=avalanche,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(optimism.native_asset_symbol)
                    )
                )
            case "optimism-bsc":
                tasks.append(
                    bungee_refuel(
                        from_chain=optimism,
                        to_chain=bsc,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(optimism.native_asset_symbol)
                    )
                )
            case "optimism-arbitrum":
                tasks.append(
                    bungee_refuel(
                        from_chain=optimism,
                        to_chain=arbitrum,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(optimism.native_asset_symbol)
                    )
                )

    logger.info(f"Doing Bungee Refuel {mode_mapping[args]}.")
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.success("*** FINISHED ***")
