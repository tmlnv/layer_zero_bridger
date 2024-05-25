""" Bungee Refuel Module
    Docs: https://docs.socket.tech/socket-api/contract-addresses
"""
import asyncio
import random
import sys
from typing import Coroutine

import aiohttp
from web3 import Web3

from config import BUNGEE_AMOUNT, PRIVATE_KEYS
from modules.chains import Chain, arbitrum, avalanche, base, bsc, optimism, polygon
from modules.custom_logger import logger
from modules.utils import _send_transaction, get_token_price, wallet_public_address


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


async def _get_bungee_limits(from_chain: Chain, to_chain: Chain) -> tuple[int, int]:
    bungee_params = await _get_bungee_data()

    for chain in bungee_params["result"]:
        if chain["chainId"] == from_chain.bungee_chain_id:
            limits: list = chain["limits"]

            for limit in limits:
                if limit["chainId"] == to_chain.bungee_chain_id:
                    if not limit["isEnabled"]:
                        logger.error(msg := f"Destination chain {to_chain.name} is not enabled")
                        raise ValueError(msg)
                    destination_chain_limits: dict = limit

    return int(destination_chain_limits["minAmount"]), int(destination_chain_limits["maxAmount"])


async def _create_transaction(address: str, from_chain: Chain, to_chain: Chain, amount: int | float) -> dict:
    amount *= 1 + random.uniform(0, 0.1)

    min_bungee_limit, max_bungee_limit = await _get_bungee_limits(from_chain=from_chain, to_chain=to_chain)

    min_bungee_limit = min_bungee_limit / 10**from_chain.native_token_decimals
    max_bungee_limit = max_bungee_limit / 10**from_chain.native_token_decimals
    logger.info(
        "BUNGEE LIMITS | "
        + (
            limits_msg := f"Min is {min_bungee_limit} {from_chain.native_asset_symbol}, "
            f"Max is {max_bungee_limit} {from_chain.native_asset_symbol}"
        )
    )

    if amount < min_bungee_limit or amount > max_bungee_limit:
        logger.error(
            msg := (
                f"BUNGEE AMOUNTS | {address} | Transferring {amount} {from_chain.native_asset_symbol} is not possible. "
                + limits_msg
            )
        )
        raise ValueError(msg)

    transaction = await from_chain.bungee_contract.functions.depositNativeToken(
        to_chain.bungee_chain_id, address
    ).build_transaction(
        {
            "from": address,
            "gas": from_chain.gas * 2,
            "gasPrice": await from_chain.w3.eth.gas_price,
            "value": Web3.to_wei(amount, "ether"),
            "nonce": await from_chain.w3.eth.get_transaction_count(address)
        }
    )
    logger.info(f"BUNGEE REFUEL | {address} | Transaction created")
    return transaction


async def bungee_refuel(from_chain: Chain, to_chain: Chain, private_key: str, amount: int | float) -> None:
    address = wallet_public_address(private_key)

    logger.info(f"BUNGEE REFUEL | {address} | Starting refuel from {from_chain.name} to {to_chain.name}")
    transaction = await _create_transaction(address=address, from_chain=from_chain, to_chain=to_chain, amount=amount)

    await _send_transaction(address=address, from_chain=from_chain, transaction=transaction, private_key=private_key)


async def main(args: str):
    mode_mapping = {
        "pa": "polygon-avalanche",
        "pb": "polygon-bsc",
        "parb": "polygon-arbitrum",
        "po": "polygon-optimism",
        "pbase": "polygon-base",
        "ap": "avalanche-polygon",
        "ab": "avalanche-bsc",
        "aarb": "avalanche-arbitrum",
        "ao": "avalanche-optimism",
        "abase": "avalanche-base",
        "bp": "bsc-polygon",
        "ba": "bsc-avalanche",
        "barb": "bsc-arbitrum",
        "bo": "bsc-optimism",
        "bbase": "bsc-base",
        "arbp": "arbitrum-polygon",
        "arba": "arbitrum-avalanche",
        "arbb": "arbitrum-bsc",
        "arbo": "arbitrum-optimism",
        "arbbase": "arbitrum-base",
        "op": "optimism-polygon",
        "oa": "optimism-avalanche",
        "ob": "optimism-bsc",
        "oarb": "optimism-arbitrum",
        "obase": "optimism-base",
        "basep": "base-polygon",
        "basea": "base-avalanche",
        "baseb": "base-bsc",
        "basearb": "base-arbitrum",
        "baseo": "base-optimism"
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
            case "polygon-base":
                tasks.append(
                    bungee_refuel(
                        from_chain=polygon,
                        to_chain=base,
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
            case "avalanche-base":
                tasks.append(
                    bungee_refuel(
                        from_chain=avalanche,
                        to_chain=base,
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
            case "bsc-base":
                tasks.append(
                    bungee_refuel(
                        from_chain=bsc,
                        to_chain=base,
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
            case "arbitrum-base":
                tasks.append(
                    bungee_refuel(
                        from_chain=arbitrum,
                        to_chain=base,
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
            case "optimism-base":
                tasks.append(
                    bungee_refuel(
                        from_chain=optimism,
                        to_chain=base,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(optimism.native_asset_symbol)
                    )
                )
            case "base-polygon":
                tasks.append(
                    bungee_refuel(
                        from_chain=base,
                        to_chain=polygon,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(base.native_asset_symbol)
                    )
                )
            case "base-avalanche":
                tasks.append(
                    bungee_refuel(
                        from_chain=base,
                        to_chain=avalanche,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(base.native_asset_symbol)
                    )
                )
            case "base-bsc":
                tasks.append(
                    bungee_refuel(
                        from_chain=base,
                        to_chain=bsc,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(base.native_asset_symbol)
                    )
                )
            case "base-arbitrum":
                tasks.append(
                    bungee_refuel(
                        from_chain=base,
                        to_chain=arbitrum,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(base.native_asset_symbol)
                    )
                )
            case "base-optimism":
                tasks.append(
                    bungee_refuel(
                        from_chain=base,
                        to_chain=optimism,
                        private_key=private_key,
                        amount=await get_bungee_refuel_amount(base.native_asset_symbol)
                    )
                )

    logger.info(f"Doing Bungee Refuel {mode_mapping[args]}.")
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.success("*** FINISHED ***")
