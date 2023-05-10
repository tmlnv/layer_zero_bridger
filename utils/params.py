"""Transaction making info"""
import json

from web3 import AsyncWeb3, AsyncHTTPProvider

POLYGON_CHAIN_ID = 109
FANTOM_CHAIN_ID = 112
AVALANCHE_CHAIN_ID = 106

usdc_addresses = {
    '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174': 'POLYGON',
    '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75': 'FANTOM',
    '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e': 'AVALANCHE'
}

polygon_rpc_url = 'https://polygon-rpc.com/'
fantom_rpc_url = 'https://rpc.ftm.tools/'
avalanche_rpc_url = 'https://api.avax.network/ext/bc/C/rpc'

polygon_w3 = AsyncWeb3(AsyncHTTPProvider(polygon_rpc_url))
fantom_w3 = AsyncWeb3(AsyncHTTPProvider(fantom_rpc_url))
avalanche_w3 = AsyncWeb3(AsyncHTTPProvider(avalanche_rpc_url))

stargate_polygon_address = polygon_w3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')
stargate_fantom_address = fantom_w3.to_checksum_address('0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6')
stargate_avalanche_address = fantom_w3.to_checksum_address('0x45A01E4e04F14f7A4a6702c74187c5F6222033cd')

stargate_abi = json.load(open('router_abi.json'))
usdc_abi = json.load(open('usdc_abi.json'))

usdc_polygon_address = polygon_w3.to_checksum_address('0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174')
usdc_fantom_address = fantom_w3.to_checksum_address('0x04068DA6C83AFCFA0e13ba15A6696662335D5B75')
usdc_avalanche_address = avalanche_w3.to_checksum_address('0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e')

stargate_polygon_contract = polygon_w3.eth.contract(address=stargate_polygon_address, abi=stargate_abi)
stargate_fantom_contract = fantom_w3.eth.contract(address=stargate_fantom_address, abi=stargate_abi)
stargate_avalanche_contract = avalanche_w3.eth.contract(address=stargate_avalanche_address, abi=stargate_abi)

usdc_polygon_contract = polygon_w3.eth.contract(address=usdc_polygon_address, abi=usdc_abi)
usdc_fantom_contract = fantom_w3.eth.contract(address=usdc_fantom_address, abi=usdc_abi)
usdc_avalanche_contract = avalanche_w3.eth.contract(address=usdc_avalanche_address, abi=usdc_abi)
