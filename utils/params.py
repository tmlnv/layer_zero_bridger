"""Transaction making info"""
import json
import os

from web3 import AsyncWeb3, AsyncHTTPProvider

with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'router_abi.json')) as file:
    stargate_abi = json.load(file)
with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdc_abi.json')) as file:
    usdc_abi = json.load(file)

polygon_usdc_address = '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
fantom_usdc_address = '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75'
avalanche_usdc_address = '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'


class Chain:
    def __init__(self, name: str, rpc_url: str, stargate_address: str, usdc_address: str, chain_id: int, explorer: str,
                 gas: int):
        self.name = name
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.stargate_address = self.w3.to_checksum_address(stargate_address)
        self.stargate_contract = self.w3.eth.contract(address=self.stargate_address, abi=stargate_abi)
        self.usdc_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(usdc_address), abi=usdc_abi)
        self.chain_id = chain_id
        self.explorer = explorer
        self.gas = gas


polygon = Chain(
    name='POLYGON',
    rpc_url='https://polygon-rpc.com/',
    stargate_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    usdc_address=polygon_usdc_address,
    chain_id=109,
    explorer='polygonscan.com',
    gas=500_000
)

fantom = Chain(
    name='FANTOM',
    rpc_url='https://rpc.ftm.tools/',
    stargate_address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
    usdc_address=fantom_usdc_address,
    chain_id=112,
    explorer='ftmscan.com',
    gas=600_000
)

avalanche = Chain(
    name='AVALANCHE',
    rpc_url='https://api.avax.network/ext/bc/C/rpc',
    stargate_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    usdc_address=avalanche_usdc_address,
    chain_id=106,
    explorer='snowtrace.io',
    gas=500_000
)

usdc_addresses = {
    polygon_usdc_address.lower(): 'POLYGON',
    fantom_usdc_address.lower(): 'FANTOM',
    avalanche_usdc_address.lower(): 'AVALANCHE'
}
