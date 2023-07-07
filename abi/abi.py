"""Abi for tokens"""
import json
import os

with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'router_abi.json')) as router, \
        open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdc_abi.json')) as usdc, \
        open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdt_abi.json')) as usdt:
    stargate_abi = json.load(router)
    usdc_abi = json.load(router)
    usdt_abi = json.load(usdt)
