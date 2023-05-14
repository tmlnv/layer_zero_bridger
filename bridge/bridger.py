import asyncio

from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from loguru import logger

from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.exceptions import ValidationError

from config import AMOUNT_TO_SWAP
from utils.params import usdc_addresses


async def send_usdc_chain_to_chain(
        wallet: str,
        from_chain_w3: AsyncWeb3,
        transaction_info: dict,
        stargate_from_chain_contract: AsyncContract,
        stargate_from_chain_address: ChecksumAddress,
        usdc_from_chain_contract: AsyncContract,
        from_chain_name: str,
        from_chain_explorer: str,
        gas: int
) -> HexBytes:
    """Send USDC from one blockchain to another. Tokens are sent to the same wallet.

    Args:
        wallet:                         Wallet address
        from_chain_w3:                  Client
        transaction_info:               Transaction info
        stargate_from_chain_contract:   Sending chain stargate router contract
        stargate_from_chain_address:    Address of Stargate Finance: Router at sending chain
        usdc_from_chain_contract:       Sending chain usdc contract
        from_chain_name:                Sending chain name
        from_chain_explorer:            Sending chain explorer
        gas:                            Amount of gas
    """
    account = from_chain_w3.eth.account.from_key(wallet)
    address = account.address

    nonce = await from_chain_w3.eth.get_transaction_count(address)
    gas_price = await from_chain_w3.eth.gas_price
    fees = await stargate_from_chain_contract.functions.quoteLayerZeroFee(
        transaction_info["chain_id"],  # uint16 _dstChainId
        1,  # uint8 _functionType
        "0x0000000000000000000000000000000000001010",  # bytes calldata _toAddress
        "0x",  # bytes calldata _transferAndCallPayload
        [0, 0, "0x0000000000000000000000000000000000000001"]  # Router.lz_tx_obj memory _lzTxParams
    ).call()
    fee = fees[0]

    allowance = await usdc_from_chain_contract.functions.allowance(address, stargate_from_chain_address).call()
    logger.debug(f"ALLOWANCE | {from_chain_name} Wallet {address} allowance for USDC is {allowance / 1000}")

    if allowance < AMOUNT_TO_SWAP:
        approve_txn = await usdc_from_chain_contract.functions.approve(
            stargate_from_chain_address,
            AMOUNT_TO_SWAP
        ).build_transaction(
            {
                'from': address,
                'gas': 150000,
                'gasPrice': gas_price,
                'nonce': nonce,
            }
        )
        signed_approve_txn = from_chain_w3.eth.account.sign_transaction(approve_txn, wallet)
        approve_txn_hash = await from_chain_w3.eth.send_raw_transaction(signed_approve_txn.rawTransaction)

        logger.info(f"{from_chain_name} | USDC APPROVED https://{from_chain_explorer}/tx/{approve_txn_hash.hex()}")
        nonce += 1

        await asyncio.sleep(30)

    usdc_balance = await usdc_from_chain_contract.functions.balanceOf(address).call()

    if usdc_balance >= AMOUNT_TO_SWAP:

        swap_txn = await stargate_from_chain_contract.functions.swap(
            transaction_info["chain_id"],
            transaction_info["source_pool_id"],
            transaction_info["dest_pool_id"],
            transaction_info["refund_address"],
            transaction_info["amount_in"],
            transaction_info["amount_out_min"],
            transaction_info["lz_tx_obj"],
            transaction_info["to"],
            transaction_info["data"]
        ).build_transaction(
            {
                'from': address,
                'value': fee,
                'gas': gas,
                'gasPrice': await from_chain_w3.eth.gas_price,
                'nonce': await from_chain_w3.eth.get_transaction_count(address),
            }
        )

        signed_swap_txn = from_chain_w3.eth.account.sign_transaction(swap_txn, wallet)
        swap_txn_hash = await from_chain_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
        return swap_txn_hash

    elif usdc_balance < AMOUNT_TO_SWAP:

        try:
            min_amount = usdc_balance - (usdc_balance * 5) // 1000

            swap_txn = await stargate_from_chain_contract.functions.swap(
                transaction_info["chain_id"],
                transaction_info["source_pool_id"],
                transaction_info["dest_pool_id"],
                transaction_info["refund_address"],
                usdc_balance,
                min_amount,
                transaction_info["lz_tx_obj"],
                transaction_info["to"],
                transaction_info["data"]
            ).build_transaction(
                {
                    'from': address,
                    'value': fee,
                    'gas': gas,
                    'gasPrice': await from_chain_w3.eth.gas_price,
                    'nonce': await from_chain_w3.eth.get_transaction_count(address),
                }
            )

            signed_swap_txn = from_chain_w3.eth.account.sign_transaction(swap_txn, wallet)
            swap_txn_hash = await from_chain_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
            return swap_txn_hash

        except ValidationError as e:
            logger.error(f'Amount to be bridged is too low. Attempting raised an {e}')


async def check_balance(address: str, usdc_contract: AsyncContract) -> int:
    """Check USDC balance of the adress on the chain specified by the address.
    (USDC has different contracts of different blockchains.)

    Args:
        address:        wallet address
        usdc_contract:  USDC contract on a specified chain to interact with
    """
    usdc_balance = await usdc_contract.functions.balanceOf(address).call()
    logger.info(
        f'BALANCE | {usdc_addresses[usdc_contract.address.lower()]} Wallet {address} USDC balance is '
        f'{round(usdc_balance / 10 ** 6, 2)}'
    )
    return usdc_balance


async def is_balance_updated(address: str, usdc_contract: AsyncContract) -> bool:
    """ CHecks whether USDC balance on a specified chain is upodated.
    (Is transfer completed or not)

    Args:
        address:        wallet address
        usdc_contract:  USDC contract on a specified chain to interact with
    """
    balance = await check_balance(address, usdc_contract)

    while balance < 3 * (10 ** 6):
        await asyncio.sleep(10)
        balance = await check_balance(address, usdc_contract)

    return True
