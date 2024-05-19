"""Main script with CLI interface for all modules"""
import argparse
import asyncio

from modules.balance_checker import get_balances as balance_checker
from modules.bungee_refuel import main as bungee_refuel
from modules.chain_to_chain import main as chain_to_chain
from modules.core_script import main as core_script
from modules.custom_logger import logger
from modules.wallet_generator import create_wallet as wallet_generator


async def main():
    """
    Main script. Without CLI arguments runs core_script.py according to config.
    With CLI arguments can be used for wallet generation, one-way asset bridging via Layer Zero,
    balance checking and bridging into native tokens to pay for gas fees via Bungee Refuel.
    """
    parser = argparse.ArgumentParser(description="Layer Zero Bridger modules")

    mode_mapping = {
        "refuel": "bungee_refuel",
        "one-way": "chain_to_chain",
        "balance": "balance_checker",
        "new-wallet": "wallet_generator",
        "default": "core_script",
    }

    parser.add_argument(
        "--mode",
        type=str,
        choices=mode_mapping.keys(),
        default="default",
        help="Module name"
    )

    parser.add_argument(
        "routing_mode",
        type=str,
        nargs='?',
        default=None,
        help="Routing mode for one-way and Bungee Refuel operations"
    )

    args = parser.parse_args()

    mode = mode_mapping[args.mode]

    match mode:
        case "chain_to_chain":
            await chain_to_chain(args.routing_mode)
        case "bungee_refuel":
            await bungee_refuel(args.routing_mode)
        case "balance_checker":
            await balance_checker()
        case "wallet_generator":
            wallet_generator()
        case "core_script":  # default
            await balance_checker()
            await core_script()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("EXECUTION STOPPED")
