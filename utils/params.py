"""Transaction info"""
import json
import os
from typing import Optional

from web3 import AsyncWeb3, AsyncHTTPProvider

with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'router_abi.json')) as file:
    stargate_abi = json.load(file)
with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdc_abi.json')) as file:
    usdc_abi = json.load(file)
with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdt_abi.json')) as file:
    usdt_abi = json.load(file)


class Token:
    def __init__(self, name: str, polygon_address: str, fantom_address: Optional[str], avalanche_address: str,
                 bsc_address: Optional[str], stargate_pool_id: int):
        self.name = name
        self.polygon_address = polygon_address
        self.fantom_address = fantom_address
        self.avalanche_address = avalanche_address
        self.bsc_address = bsc_address
        self.stargate_pool_id = stargate_pool_id


usdc = Token(
    name="USDC",
    polygon_address='0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
    fantom_address='0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
    avalanche_address='0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e',
    bsc_address=None,
    stargate_pool_id=1
)

usdt = Token(
    name="USDT",
    polygon_address='0xc2132d05d31c914a87c6611c10748aeb04b58e8f',
    fantom_address=None,
    avalanche_address='0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
    bsc_address='0x55d398326f99059fF775485246999027B3197955',
    stargate_pool_id=2
)


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
    gas=500_000
)

token_addresses = {
    usdc.polygon_address.lower(): 'POLYGON',
    usdc.fantom_address.lower(): 'FANTOM',
    usdc.avalanche_address.lower(): 'AVALANCHE',
    usdt.bsc_address.lower(): 'BSC'
}
