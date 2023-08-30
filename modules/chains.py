"""Blockchain classes and  info"""
from typing import Optional

from web3 import AsyncWeb3, AsyncHTTPProvider

from modules.tokens import usdc, usdt
from abi.abi import stargate_abi, usdc_abi, usdt_abi, bungee_refuel_abi


class Chain:
    def __init__(
            self,
            name: str,
            native_asset_symbol: str,
            rpc_url: str,
            stargate_router_address: str,
            usdc_address: Optional[str],
            usdt_address: Optional[str],
            bungee_refuel_address: str,
            layer_zero_chain_id: int,
            bungee_chain_id: int,
            explorer: str,
            gas: int
    ):
        self.name = name
        self.native_asset_symbol = native_asset_symbol
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.stargate_router_address = self.w3.to_checksum_address(stargate_router_address)
        self.stargate_contract = self.w3.eth.contract(address=self.stargate_router_address, abi=stargate_abi)
        self.usdc_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(usdc_address), abi=usdc_abi)\
            if usdc_address else None
        self.usdt_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(usdt_address), abi=usdt_abi)\
            if usdt_address else None
        self.bungee_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(bungee_refuel_address), abi=bungee_refuel_abi
        )
        self.layer_zero_chain_id = layer_zero_chain_id
        self.bungee_chain_id = bungee_chain_id
        self.explorer = explorer
        self.gas = gas
        self.native_token_decimals = 18 # for all blockchains to be compatible with Solidity, native asset should have 18 decimals


polygon = Chain(
    name='POLYGON',
    native_asset_symbol='MATIC',
    rpc_url='https://polygon-rpc.com/',
    stargate_router_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    usdc_address=usdc.polygon_address,
    usdt_address=usdt.polygon_address,
    bungee_refuel_address='0xAC313d7491910516E06FBfC2A0b5BB49bb072D91',
    layer_zero_chain_id=109,
    bungee_chain_id=137,
    explorer='polygonscan.com',
    gas=500_000
)

fantom = Chain(
    name='FANTOM',
    native_asset_symbol='FTM',
    rpc_url='https://rpc.ftm.tools/',
    stargate_router_address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
    usdc_address=usdc.fantom_address,
    usdt_address=None,
    bungee_refuel_address='0x040993fbF458b95871Cd2D73Ee2E09F4AF6d56bB',
    layer_zero_chain_id=112,
    bungee_chain_id=250,
    explorer='ftmscan.com',
    gas=600_000
)

avalanche = Chain(
    name='AVALANCHE',
    native_asset_symbol='AVAX',
    rpc_url='https://api.avax.network/ext/bc/C/rpc',
    stargate_router_address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
    usdc_address=usdc.avalanche_address,
    usdt_address=usdt.avalanche_address,
    bungee_refuel_address='0x040993fbf458b95871cd2d73ee2e09f4af6d56bb',
    layer_zero_chain_id=106,
    bungee_chain_id=43114,
    explorer='snowtrace.io',
    gas=500_000
)

bsc = Chain(
    name='BSC',
    native_asset_symbol='BNB',
    rpc_url='https://bsc-dataseed1.defibit.io/',
    stargate_router_address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
    usdc_address=None,
    bungee_refuel_address='0xbe51d38547992293c89cc589105784ab60b004a9',
    usdt_address=usdt.bsc_address,
    layer_zero_chain_id=102,
    bungee_chain_id=56,
    explorer='bscscan.com',
    gas=700_000
)

arbitrum = Chain(
    name='ARBITRUM',
    native_asset_symbol='ETH',
    rpc_url='https://rpc.ankr.com/arbitrum',
    stargate_router_address='0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
    usdc_address=usdc.arbitrum_address,
    bungee_refuel_address='0xc0E02AA55d10e38855e13B64A8E1387A04681A00',
    usdt_address=usdt.arbitrum_address,
    layer_zero_chain_id=110,
    bungee_chain_id=42161,
    explorer='arbiscan.io',
    gas=500_000
)

optimism = Chain(
    name='OPTIMISM',
    native_asset_symbol='ETH',
    rpc_url='https://rpc.ankr.com/optimism',
    stargate_router_address='0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
    usdc_address=usdc.optimism_adress,
    bungee_refuel_address='0x5800249621DA520aDFdCa16da20d8A5Fc0f814d8',
    usdt_address=None,
    layer_zero_chain_id=111,
    bungee_chain_id=10,
    explorer='optimistic.etherscan.io',
    gas=700_000
)

base = Chain(
    name='BASE',
    native_asset_symbol='ETH',
    rpc_url='https://base.blockpi.network/v1/rpc/public',
    stargate_router_address='0x45f1A95A4D3f3836523F5c83673c797f4d4d263B',
    usdc_address=usdc.base_address,
    bungee_refuel_address='0x3a23F943181408EAC424116Af7b7790c94Cb97a5',
    usdt_address=None,
    layer_zero_chain_id=184,
    bungee_chain_id=8453,
    explorer='basescan.org',
    gas=700_000
)
