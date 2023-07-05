"""Blockchain classes and  info"""
from typing import Optional

from web3 import AsyncWeb3, AsyncHTTPProvider

from modules.tokens import usdc, usdt
from abi.abi import stargate_abi, usdc_abi, usdt_abi


class Chain:
    def __init__(self, name: str, rpc_url: str, stargate_address: str, usdc_address: Optional[str],
                 usdt_address: Optional[str], chain_id: int, explorer: str, gas: int):
        self.name = name
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.stargate_address = self.w3.to_checksum_address(stargate_address)
        self.stargate_contract = self.w3.eth.contract(address=self.stargate_address, abi=stargate_abi)
        self.usdc_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(usdc_address), abi=usdc_abi)\
            if usdc_address else None
        self.usdt_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(usdt_address), abi=usdt_abi)\
            if usdt_address else None
        self.chain_id = chain_id
        self.explorer = explorer
        self.gas = gas


polygon = Chain(
    name='POLYGON',
    rpc_url='https://polygon-rpc.com/',
    stargate_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    usdc_address=usdc.polygon_address,
    usdt_address=usdt.polygon_address,
    chain_id=109,
    explorer='polygonscan.com',
    gas=500_000
)

fantom = Chain(
    name='FANTOM',
    rpc_url='https://rpc.ftm.tools/',
    stargate_address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
    usdc_address=usdc.fantom_address,
    usdt_address=None,
    chain_id=112,
    explorer='ftmscan.com',
    gas=600_000
)

avalanche = Chain(
    name='AVALANCHE',
    rpc_url='https://api.avax.network/ext/bc/C/rpc',
    stargate_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    usdc_address=usdc.avalanche_address,
    usdt_address=usdt.avalanche_address,
    chain_id=106,
    explorer='snowtrace.io',
    gas=500_000
)

bsc = Chain(
    name='BSC',
    rpc_url='https://bsc-dataseed1.defibit.io/',
    stargate_address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
    usdc_address=None,
    usdt_address=usdt.bsc_address,
    chain_id=102,
    explorer='bscscan.com',
    gas=400_000
)
