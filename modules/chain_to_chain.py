import random
import asyncio
import sys
from typing import Coroutine

from eth_typing import ChecksumAddress
from web3 import AsyncWeb3
from web3.contract import AsyncContract
from tqdm import tqdm

from config import PRIVATE_KEYS, AMOUNT_TO_SWAP
from modules.bridger import send_token_chain_to_chain, is_balance_updated
from modules.tokens import usdc, usdt
from modules.chains import polygon, avalanche, bsc, fantom, arbitrum, optimism, base
from modules.utils import get_correct_amount_and_min_amount, get_token_decimals, wallet_public_address
from modules.custom_logger import logger


async def chain_to_chain(
        wallet: str,
        from_chain_name: str,
        token: str,
        token_from_chain_contract: AsyncContract,
        to_chain_name: str,
        from_chain_w3: AsyncWeb3,
        destination_chain_id: int,
        source_pool_id: int,
        dest_pool_id: int,
        stargate_from_chain_contract: AsyncContract,
        stargate_from_chain_address: ChecksumAddress,
        from_chain_explorer: str,
        gas: int
) -> None:
    """Transfer function. It bridges token from source blockchain to destination blockchain.
    Stargate docs:  https://stargateprotocol.gitbook.io/stargate/developers

    Args:
        wallet:                         Wallet private key
        from_chain_name:                Sending chain name
        token:                          Token to be sent symbol
        token_from_chain_contract:      Sending chain token contract
        to_chain_name:                  Destination chain name
        from_chain_w3:                  Client
        destination_chain_id:           Destination chain id from stargate docs
        source_pool_id:                 Source pool id
        dest_pool_id:                   Destination pool id
        stargate_from_chain_contract:   Sending chain stargate router contract
        stargate_from_chain_address:    Address of Stargate Finance: Router at sending chain
        from_chain_explorer:            Sending chain explorer
        gas:                            Amount of gas
    """
    address = wallet_public_address(wallet)

    amount_to_swap, min_amount = await get_correct_amount_and_min_amount(token_contract=token_from_chain_contract,
                                                                         amount_to_swap=AMOUNT_TO_SWAP)

    start_delay = random.randint(1, 200)
    logger.info(f"START DELAY | {address} | Waiting for {start_delay} seconds.")
    with tqdm(
            total=start_delay, desc=f"Waiting START DELAY | {address}", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
    ) as pbar:
        for i in range(start_delay):
            await asyncio.sleep(1)
            pbar.update(1)

    balance = None
    logger_cntr = 0
    while not balance:
        await asyncio.sleep(30)
        if logger_cntr % 3 == 0:
            logger.info(f"BALANCE | {address} | Checking {from_chain_name} {token} balance")
        balance = await is_balance_updated(address=address, token=token, token_contract=token_from_chain_contract)
        logger_cntr += 1

    logger.info(
        f"BRIDGING | {address} | "
        f"Trying to bridge {amount_to_swap / 10 ** await get_token_decimals(token_from_chain_contract)} "
        f"{token} from {from_chain_name} to {to_chain_name}"
    )
    bridging_txn_hash = await send_token_chain_to_chain(
        wallet=wallet,
        from_chain_w3=from_chain_w3,
        transaction_info={
            "chain_id": destination_chain_id,
            "source_pool_id": source_pool_id,
            "dest_pool_id": dest_pool_id,
            "refund_address": address,
            "amount_in": amount_to_swap,
            "amount_out_min": min_amount,
            "lz_tx_obj": [
                0,
                0,
                "0x0000000000000000000000000000000000000001"
            ],
            "to": address,
            "data": "0x"
        },
        stargate_from_chain_contract=stargate_from_chain_contract,
        stargate_from_chain_address=stargate_from_chain_address,
        token_from_chain_contract=token_from_chain_contract,
        from_chain_name=from_chain_name,
        token=token,
        amount_to_swap=amount_to_swap,
        from_chain_explorer=from_chain_explorer,
        gas=gas
    )
    logger.success(
        f"{from_chain_name} | {address} | Transaction: https://{from_chain_explorer}/tx/{bridging_txn_hash.hex()}"
    )
    logger.success(f"LAYERZEROSCAN | {address} | Transaction: https://layerzeroscan.com/tx/{bridging_txn_hash.hex()}")


async def main(args: str):

    mode_mapping = {
        "pf": "polygon-fantom",
        "pa": "polygon-avalanche",
        "pb": "polygon-bsc",
        "parb": "polygon-arbitrum",
        "po": "polygon-optimism",
        "pbase": "polygon-base",
        "fp": "fantom-polygon",
        "fa": "fantom-avalanche",
        "fb": "fantom-bsc",
        "ap": "avalanche-polygon",
        "af": "avalanche-fantom",
        "ab": "avalanche-bsc",
        "aarb": "avalanche-arbitrum",
        "ao": "avalanche-optimism",
        "abase": "avalanche-base",
        "bp": "bsc-polygon",
        "bf": "bsc-fantom",
        "ba": "bsc-avalanche",
        "barb": "bsc-arbitrum",
        "bo": "bsc-optimism",
        "bbase": "bsc-base",
        "arbp": "arbitrum-polygon",
        "arba": "arbitrum-avalanche",
        "arbb": "arbitrum-bsc",
        "arbo": "arbuitrum-optimism",
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

    logger.info(args)
    if args is None:
        print("Error: the route argument is required")
        sys.exit(2)
    elif args not in mode_mapping.keys():
        logger.error(
            f"Unsupported route. Supported routes:\n{list(mode_mapping.values())}\n"
            "Usage example: type 'pa' for 'polygon-avalanche' route"
        )
        sys.exit(2)

    mode = mode_mapping[args]

    tasks: list[Coroutine] = []
    for wallet in PRIVATE_KEYS:
        match mode:
            case "polygon-fantom":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=polygon.name,
                        token=usdc.name,
                        token_from_chain_contract=polygon.usdc_contract,
                        to_chain_name=fantom.name,
                        from_chain_w3=polygon.w3,
                        destination_chain_id=fantom.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=polygon.stargate_contract,
                        stargate_from_chain_address=polygon.stargate_router_address,
                        from_chain_explorer=polygon.explorer,
                        gas=polygon.gas
                    )
                )
            case "polygon-avalanche":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=polygon.name,
                        token=usdc.name,
                        token_from_chain_contract=polygon.usdc_contract,
                        to_chain_name=avalanche.name,
                        from_chain_w3=polygon.w3,
                        destination_chain_id=avalanche.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=polygon.stargate_contract,
                        stargate_from_chain_address=polygon.stargate_router_address,
                        from_chain_explorer=polygon.explorer,
                        gas=polygon.gas
                    )
                )
            case "polygon-bsc":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=polygon.name,
                        token=usdc.name,
                        token_from_chain_contract=polygon.usdc_contract,
                        to_chain_name=bsc.name,
                        from_chain_w3=polygon.w3,
                        destination_chain_id=bsc.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=polygon.stargate_contract,
                        stargate_from_chain_address=polygon.stargate_router_address,
                        from_chain_explorer=polygon.explorer,
                        gas=polygon.gas
                    )
                )
            case "polygon-arbitrum":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=polygon.name,
                        token=usdc.name,
                        token_from_chain_contract=polygon.usdc_contract,
                        to_chain_name=arbitrum.name,
                        from_chain_w3=polygon.w3,
                        destination_chain_id=arbitrum.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=polygon.stargate_contract,
                        stargate_from_chain_address=polygon.stargate_router_address,
                        from_chain_explorer=polygon.explorer,
                        gas=polygon.gas
                    )
                )
            case "polygon-optimism":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=polygon.name,
                        token=usdc.name,
                        token_from_chain_contract=polygon.usdc_contract,
                        to_chain_name=optimism.name,
                        from_chain_w3=polygon.w3,
                        destination_chain_id=optimism.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=polygon.stargate_contract,
                        stargate_from_chain_address=polygon.stargate_router_address,
                        from_chain_explorer=polygon.explorer,
                        gas=polygon.gas
                    )
                )
            case "polygon-base":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=polygon.name,
                        token=usdc.name,
                        token_from_chain_contract=polygon.usdc_contract,
                        to_chain_name=base.name,
                        from_chain_w3=polygon.w3,
                        destination_chain_id=base.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=polygon.stargate_contract,
                        stargate_from_chain_address=polygon.stargate_router_address,
                        from_chain_explorer=polygon.explorer,
                        gas=polygon.gas
                    )
                )
            case "fantom-polygon":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=fantom.name,
                        token=usdc.name,
                        token_from_chain_contract=fantom.usdc_contract,
                        to_chain_name=polygon.name,
                        from_chain_w3=fantom.w3,
                        destination_chain_id=polygon.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=fantom.stargate_contract,
                        stargate_from_chain_address=fantom.stargate_router_address,
                        from_chain_explorer=fantom.explorer,
                        gas=fantom.gas
                    )
                )
            case "fantom-avalanche":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=fantom.name,
                        token=usdc.name,
                        token_from_chain_contract=fantom.usdc_contract,
                        to_chain_name=avalanche.name,
                        from_chain_w3=fantom.w3,
                        destination_chain_id=avalanche.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=fantom.stargate_contract,
                        stargate_from_chain_address=fantom.stargate_router_address,
                        from_chain_explorer=fantom.explorer,
                        gas=fantom.gas
                    )
                )
            case "fantom-bsc":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=fantom.name,
                        token=usdc.name,
                        token_from_chain_contract=fantom.usdc_contract,
                        to_chain_name=bsc.name,
                        from_chain_w3=fantom.w3,
                        destination_chain_id=bsc.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=fantom.stargate_contract,
                        stargate_from_chain_address=fantom.stargate_router_address,
                        from_chain_explorer=fantom.explorer,
                        gas=fantom.gas
                    )
                )
            case "avalanche-polygon":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=avalanche.name,
                        token=usdc.name,
                        token_from_chain_contract=avalanche.usdc_contract,
                        to_chain_name=polygon.name,
                        from_chain_w3=avalanche.w3,
                        destination_chain_id=polygon.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=avalanche.stargate_contract,
                        stargate_from_chain_address=avalanche.stargate_router_address,
                        from_chain_explorer=avalanche.explorer,
                        gas=avalanche.gas
                    )
                )
            case "avalanche-fantom":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=avalanche.name,
                        token=usdc.name,
                        token_from_chain_contract=avalanche.usdc_contract,
                        to_chain_name=fantom.name,
                        from_chain_w3=avalanche.w3,
                        destination_chain_id=fantom.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=avalanche.stargate_contract,
                        stargate_from_chain_address=avalanche.stargate_router_address,
                        from_chain_explorer=avalanche.explorer,
                        gas=avalanche.gas
                    )
                )
            case "avalanche-bsc":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=avalanche.name,
                        token=usdc.name,
                        token_from_chain_contract=avalanche.usdc_contract,
                        to_chain_name=bsc.name,
                        from_chain_w3=avalanche.w3,
                        destination_chain_id=bsc.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=avalanche.stargate_contract,
                        stargate_from_chain_address=avalanche.stargate_router_address,
                        from_chain_explorer=avalanche.explorer,
                        gas=avalanche.gas
                    )
                )
            case "avalanche-arbitrum":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=avalanche.name,
                        token=usdc.name,
                        token_from_chain_contract=avalanche.usdc_contract,
                        to_chain_name=arbitrum.name,
                        from_chain_w3=avalanche.w3,
                        destination_chain_id=arbitrum.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=avalanche.stargate_contract,
                        stargate_from_chain_address=avalanche.stargate_router_address,
                        from_chain_explorer=avalanche.explorer,
                        gas=avalanche.gas
                    )
                )
            case "avalanche-optimism":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=avalanche.name,
                        token=usdc.name,
                        token_from_chain_contract=avalanche.usdc_contract,
                        to_chain_name=optimism.name,
                        from_chain_w3=avalanche.w3,
                        destination_chain_id=optimism.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=avalanche.stargate_contract,
                        stargate_from_chain_address=avalanche.stargate_router_address,
                        from_chain_explorer=avalanche.explorer,
                        gas=avalanche.gas
                    )
                )
            case "avalanche-base":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=avalanche.name,
                        token=usdc.name,
                        token_from_chain_contract=avalanche.usdc_contract,
                        to_chain_name=base.name,
                        from_chain_w3=avalanche.w3,
                        destination_chain_id=base.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=avalanche.stargate_contract,
                        stargate_from_chain_address=avalanche.stargate_router_address,
                        from_chain_explorer=avalanche.explorer,
                        gas=avalanche.gas
                    )
                )
            case "bsc-polygon":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=bsc.name,
                        token=usdt.name,
                        token_from_chain_contract=bsc.usdt_contract,
                        to_chain_name=polygon.name,
                        from_chain_w3=bsc.w3,
                        destination_chain_id=polygon.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=bsc.stargate_contract,
                        stargate_from_chain_address=bsc.stargate_router_address,
                        from_chain_explorer=bsc.explorer,
                        gas=bsc.gas
                    )
                )
            case "bsc-fantom":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=bsc.name,
                        token=usdt.name,
                        token_from_chain_contract=bsc.usdt_contract,
                        to_chain_name=fantom.name,
                        from_chain_w3=bsc.w3,
                        destination_chain_id=fantom.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=bsc.stargate_contract,
                        stargate_from_chain_address=bsc.stargate_router_address,
                        from_chain_explorer=bsc.explorer,
                        gas=bsc.gas
                    )

                )
            case "bsc-avalanche":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=bsc.name,
                        token=usdt.name,
                        token_from_chain_contract=bsc.usdt_contract,
                        to_chain_name=avalanche.name,
                        from_chain_w3=bsc.w3,
                        destination_chain_id=avalanche.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=bsc.stargate_contract,
                        stargate_from_chain_address=bsc.stargate_router_address,
                        from_chain_explorer=bsc.explorer,
                        gas=bsc.gas
                    )
                )
            case "bsc-arbitrum":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=bsc.name,
                        token=usdt.name,
                        token_from_chain_contract=bsc.usdt_contract,
                        to_chain_name=arbitrum.name,
                        from_chain_w3=bsc.w3,
                        destination_chain_id=arbitrum.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=bsc.stargate_contract,
                        stargate_from_chain_address=bsc.stargate_router_address,
                        from_chain_explorer=bsc.explorer,
                        gas=bsc.gas
                    )
                )
            case "bsc-optimism":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=bsc.name,
                        token=usdt.name,
                        token_from_chain_contract=bsc.usdt_contract,
                        to_chain_name=optimism.name,
                        from_chain_w3=bsc.w3,
                        destination_chain_id=optimism.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=bsc.stargate_contract,
                        stargate_from_chain_address=bsc.stargate_router_address,
                        from_chain_explorer=bsc.explorer,
                        gas=bsc.gas
                    )
                )
            case "bsc-base":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=bsc.name,
                        token=usdt.name,
                        token_from_chain_contract=bsc.usdt_contract,
                        to_chain_name=base.name,
                        from_chain_w3=bsc.w3,
                        destination_chain_id=base.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=bsc.stargate_contract,
                        stargate_from_chain_address=bsc.stargate_router_address,
                        from_chain_explorer=bsc.explorer,
                        gas=bsc.gas
                    )
                )
            case "arbitrum-polygon":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=arbitrum.name,
                        token=usdt.name,
                        token_from_chain_contract=arbitrum.usdt_contract,
                        to_chain_name=polygon.name,
                        from_chain_w3=arbitrum.w3,
                        destination_chain_id=polygon.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=arbitrum.stargate_contract,
                        stargate_from_chain_address=arbitrum.stargate_router_address,
                        from_chain_explorer=arbitrum.explorer,
                        gas=arbitrum.gas
                    )
                )
            case "arbitrum-avalanche":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=arbitrum.name,
                        token=usdt.name,
                        token_from_chain_contract=arbitrum.usdt_contract,
                        to_chain_name=avalanche.name,
                        from_chain_w3=arbitrum.w3,
                        destination_chain_id=avalanche.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=arbitrum.stargate_contract,
                        stargate_from_chain_address=arbitrum.stargate_router_address,
                        from_chain_explorer=arbitrum.explorer,
                        gas=arbitrum.gas
                    )
                )
            case "arbitrum-bsc":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=arbitrum.name,
                        token=usdt.name,
                        token_from_chain_contract=arbitrum.usdt_contract,
                        to_chain_name=bsc.name,
                        from_chain_w3=arbitrum.w3,
                        destination_chain_id=bsc.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=arbitrum.stargate_contract,
                        stargate_from_chain_address=arbitrum.stargate_router_address,
                        from_chain_explorer=arbitrum.explorer,
                        gas=arbitrum.gas
                    )
                )
            case "arbitrum-optimism":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=arbitrum.name,
                        token=usdt.name,
                        token_from_chain_contract=arbitrum.usdt_contract,
                        to_chain_name=optimism.name,
                        from_chain_w3=arbitrum.w3,
                        destination_chain_id=optimism.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=arbitrum.stargate_contract,
                        stargate_from_chain_address=arbitrum.stargate_router_address,
                        from_chain_explorer=arbitrum.explorer,
                        gas=arbitrum.gas
                    )
                )
            case "arbitrum-base":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=arbitrum.name,
                        token=usdt.name,
                        token_from_chain_contract=arbitrum.usdt_contract,
                        to_chain_name=base.name,
                        from_chain_w3=arbitrum.w3,
                        destination_chain_id=base.layer_zero_chain_id,
                        source_pool_id=usdt.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=arbitrum.stargate_contract,
                        stargate_from_chain_address=arbitrum.stargate_router_address,
                        from_chain_explorer=arbitrum.explorer,
                        gas=arbitrum.gas
                    )
                )
            case "optimism-polygon":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=optimism.name,
                        token=usdc.name,
                        token_from_chain_contract=optimism.usdc_contract,
                        to_chain_name=polygon.name,
                        from_chain_w3=optimism.w3,
                        destination_chain_id=polygon.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=optimism.stargate_contract,
                        stargate_from_chain_address=optimism.stargate_router_address,
                        from_chain_explorer=optimism.explorer,
                        gas=optimism.gas
                    )
                )
            case "optimism-avalanche":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=optimism.name,
                        token=usdc.name,
                        token_from_chain_contract=optimism.usdc_contract,
                        to_chain_name=avalanche.name,
                        from_chain_w3=optimism.w3,
                        destination_chain_id=avalanche.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=optimism.stargate_contract,
                        stargate_from_chain_address=optimism.stargate_router_address,
                        from_chain_explorer=optimism.explorer,
                        gas=optimism.gas
                    )
                )
            case "optimism-bsc":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=optimism.name,
                        token=usdc.name,
                        token_from_chain_contract=optimism.usdc_contract,
                        to_chain_name=bsc.name,
                        from_chain_w3=optimism.w3,
                        destination_chain_id=bsc.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=optimism.stargate_contract,
                        stargate_from_chain_address=optimism.stargate_router_address,
                        from_chain_explorer=optimism.explorer,
                        gas=optimism.gas
                    )
                )
            case "optimism-arbitrum":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=optimism.name,
                        token=usdc.name,
                        token_from_chain_contract=optimism.usdc_contract,
                        to_chain_name=arbitrum.name,
                        from_chain_w3=optimism.w3,
                        destination_chain_id=arbitrum.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=optimism.stargate_contract,
                        stargate_from_chain_address=optimism.stargate_router_address,
                        from_chain_explorer=optimism.explorer,
                        gas=optimism.gas
                    )
                )
            case "optimism-base":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=optimism.name,
                        token=usdc.name,
                        token_from_chain_contract=optimism.usdc_contract,
                        to_chain_name=base.name,
                        from_chain_w3=optimism.w3,
                        destination_chain_id=base.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=optimism.stargate_contract,
                        stargate_from_chain_address=optimism.stargate_router_address,
                        from_chain_explorer=optimism.explorer,
                        gas=optimism.gas
                    )
                )
            case "base-polygon":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=base.name,
                        token=usdc.name,
                        token_from_chain_contract=base.usdc_contract,
                        to_chain_name=polygon.name,
                        from_chain_w3=base.w3,
                        destination_chain_id=polygon.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=base.stargate_contract,
                        stargate_from_chain_address=base.stargate_router_address,
                        from_chain_explorer=base.explorer,
                        gas=base.gas
                    )
                )
            case "base-avalanche":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=base.name,
                        token=usdc.name,
                        token_from_chain_contract=base.usdc_contract,
                        to_chain_name=avalanche.name,
                        from_chain_w3=base.w3,
                        destination_chain_id=avalanche.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=base.stargate_contract,
                        stargate_from_chain_address=base.stargate_router_address,
                        from_chain_explorer=base.explorer,
                        gas=base.gas
                    )
                )
            case "base-bsc":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=base.name,
                        token=usdc.name,
                        token_from_chain_contract=base.usdc_contract,
                        to_chain_name=bsc.name,
                        from_chain_w3=base.w3,
                        destination_chain_id=bsc.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=base.stargate_contract,
                        stargate_from_chain_address=base.stargate_router_address,
                        from_chain_explorer=base.explorer,
                        gas=base.gas
                    )
                )
            case "base-arbitrum":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=base.name,
                        token=usdc.name,
                        token_from_chain_contract=base.usdc_contract,
                        to_chain_name=arbitrum.name,
                        from_chain_w3=base.w3,
                        destination_chain_id=arbitrum.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdt.stargate_pool_id,
                        stargate_from_chain_contract=base.stargate_contract,
                        stargate_from_chain_address=base.stargate_router_address,
                        from_chain_explorer=base.explorer,
                        gas=base.gas
                    )
                )
            case "base-optimism":
                tasks.append(
                    chain_to_chain(
                        wallet=wallet,
                        from_chain_name=base.name,
                        token=usdc.name,
                        token_from_chain_contract=base.usdc_contract,
                        to_chain_name=optimism.name,
                        from_chain_w3=base.w3,
                        destination_chain_id=optimism.layer_zero_chain_id,
                        source_pool_id=usdc.stargate_pool_id,
                        dest_pool_id=usdc.stargate_pool_id,
                        stargate_from_chain_contract=base.stargate_contract,
                        stargate_from_chain_address=base.stargate_router_address,
                        from_chain_explorer=base.explorer,
                        gas=base.gas
                    )
                )

    logger.info(f"Bridging {mode_mapping[args]}.")
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.success("*** FINISHED ***")
