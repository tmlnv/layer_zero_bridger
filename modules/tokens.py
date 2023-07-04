"""Token classes and info"""
from typing import Optional


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

token_addresses = {
    usdc.polygon_address.lower(): 'POLYGON',
    usdc.fantom_address.lower(): 'FANTOM',
    usdc.avalanche_address.lower(): 'AVALANCHE',
    usdt.bsc_address.lower(): 'BSC'
}
