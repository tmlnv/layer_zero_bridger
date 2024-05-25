import asyncio

from colorama import Fore, Style
from prettytable import PrettyTable
from web3.contract import AsyncContract

from config import PRIVATE_KEYS
from modules.chains import Chain, arbitrum, avalanche, base, bsc, optimism, polygon
from modules.custom_logger import logger
from modules.utils import get_token_decimals, get_token_symbol, wallet_public_address

tokens = {
    "POLYGON": polygon.usdc_contract,
    "AVALANCHE": avalanche.usdc_contract,
    "BSC": bsc.usdt_contract,
    "ARBITRUM": arbitrum.usdt_contract,
    "OPTIMISM": optimism.usdc_contract,
    "BASE": base.usdc_contract,
}

supported_chains = [polygon, avalanche, bsc, arbitrum, optimism, base]

TOKEN_SYMBOLS = ["USDC", "USDT", "USDbC"]

balances = dict()


async def _get_token_data(token_contract: AsyncContract):
    """Get decimals and symbol of a token

    Args:
        token_contract: contract of the token. Can be checked via scans.
    """
    decimals = await get_token_decimals(token_contract=token_contract)
    symbol = await get_token_symbol(token_contract=token_contract)

    return decimals, symbol


async def _check_balance(wallet: str, token_contract: AsyncContract, skip_small: bool = True) -> tuple[float, str]:
    """Check token balance for the specified wallet

    Args:
        wallet:             wallet public address
        token_contract:     web3 token contract
        skip_small:         boolean flag to skip showing small values
    """
    token_decimal, symbol = await _get_token_data(token_contract=token_contract)
    balance = await token_contract.functions.balanceOf(wallet).call()

    human_readable = balance / 10**token_decimal

    if human_readable != 0 and human_readable < 0.01 and skip_small:
        human_readable = "DUST"

    return human_readable, symbol


async def _worker(wallet: str, chain: Chain) -> tuple[str, str, dict[str, float]]:
    """Function for getting balance of a token for a given chain

    Args:
        wallet:             wallet public address
        chain:              blockchain for checking
    """
    token = tokens[chain.name]
    balance, symbol = await _check_balance(wallet=wallet, token_contract=token)

    return wallet, chain.name, {symbol: balance}


async def _main(wallets: list[str], chains: list[Chain]) -> None:
    """Async function for getting all balance of a specified token for specified wallet on a given chain

    Args:
        wallets:    list of public addresses
        chains      list of blockchains
    """
    tasks = [_worker(wallet, chain) for wallet in wallets for chain in chains]
    results = await asyncio.gather(*tasks)

    for wallet, chain_name, result in results:
        if wallet not in balances:
            balances[wallet] = {}
        if chain_name not in balances[wallet]:
            balances[wallet][chain_name] = {}
        balances[wallet][chain_name].update(result)


def print_results():
    """Print results in a table"""
    column_names = ["Wallet"]
    for chain in supported_chains:
        for token in TOKEN_SYMBOLS:
            column_names.append(f"{chain.name}_{token}")

    columns_to_drop = set(column_names[1:])

    for wallet, chains in balances.items():
        for chain in supported_chains:
            for token in TOKEN_SYMBOLS:
                balance = chains.get(chain.name, {}).get(token, None)
                column_name = f"{chain.name}_{token}"

                if balance is not None and column_name in columns_to_drop:
                    columns_to_drop.remove(column_name)

    table = PrettyTable()
    table.field_names = [column_name for column_name in column_names if column_name not in columns_to_drop]

    for wallet, chains in balances.items():
        row_data = [wallet]

        for column_name in table.field_names[1:]:
            chain, token = column_name.split("_")
            balance = chains.get(chain, {}).get(token, "N/A")
            row_data.append(balance)

        table.add_row(row_data)

    colored_table = Fore.GREEN + Style.NORMAL + str(table) + Style.RESET_ALL

    logger.info("WALLET BALANCES")
    print(colored_table)


async def get_balances():
    """Get all balances for private keys of wallets provided"""
    public_wallets = []
    for private_key in PRIVATE_KEYS:
        wallet = wallet_public_address(private_key)
        public_wallets.append(wallet)

        balances.update({wallet: {}})

        for chain in supported_chains:
            balances[wallet].update({chain.name: {}})

    await _main(wallets=public_wallets, chains=supported_chains)

    print_results()
