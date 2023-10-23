"""Helper functions"""
import aiohttp
from eth_account import Account
from hexbytes import HexBytes
from loguru import logger
from web3.contract import AsyncContract

from modules.chains import Chain


async def get_token_decimals(token_contract: AsyncContract) -> int:
    """ Function for getting info how many decimals token has

    Args:
        token_contract: token contract to check
    """
    return await token_contract.functions.decimals().call()


async def get_token_symbol(token_contract: AsyncContract) -> str:
    """ Function for getting token Symbol (BTC for Bitcoin, etc.)

    Args:
        token_contract: token contract to check
    """
    return await token_contract.functions.symbol().call()


def get_min_amount_to_swap(amount_to_swap: int, slippage: float = 0.005) -> int:
    """Function for getting minimum receiving amount after the bridge

    Args:
        amount_to_swap: amount to be sent
        slippage:       slippage, %
    """
    return round(amount_to_swap - amount_to_swap * slippage)


async def get_correct_amount_and_min_amount(
        token_contract: AsyncContract, amount_to_swap: int, slippage: float = 0.005) -> (int, int):
    """Function for getting correct amount to be sent and min amount to be received

    Args:
        token_contract: token contract to check
        amount_to_swap: amount to be sent
        slippage:       slippage, %
    """
    decimals = await get_token_decimals(token_contract=token_contract)
    correct_amount_to_swap = int(amount_to_swap * 10 ** decimals)
    min_amount = get_min_amount_to_swap(amount_to_swap=amount_to_swap, slippage=slippage)
    return correct_amount_to_swap, min_amount


def wallet_public_address(wallet_private_key: str) -> str:
    """Function for getting public wallet adress from private key"""
    return Account.from_key(wallet_private_key).address


async def get_token_price(token_symbol: str) -> float:
    """Function for fetching token $ price"""
    url = f'https://min-api.cryptocompare.com/data/price?fsym={token_symbol}&tsyms=USDT'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return (await response.json())['USDT']


async def _send_transaction(address: str, from_chain: Chain, transaction: dict, private_key: str) -> HexBytes:
    """Signing and sending transaction function"""
    signed_transaction = from_chain.w3.eth.account.sign_transaction(transaction, private_key)
    logger.info(f'SIGNING | {address} | Transaction signed')
    try:
        transaction_hash = await from_chain.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    except Exception as e:
        logger.error(
            f"SENDING | {address} | Problem sending transaction. Probably wallet balance is too low. {e}"
        )
    hex_tr = transaction_hash.hex()
    logger.info(f'SENDING | {address} | Transaction: https://{from_chain.explorer}/tx/{hex_tr}')
    receipt = await from_chain.w3.eth.wait_for_transaction_receipt(transaction_hash)

    if receipt.status == 1:
        logger.success(f"SENDING | {address} | Transaction succeeded")
    else:
        logger.error(f"SENDING | {address} | Transaction failed")

    return hex_tr
