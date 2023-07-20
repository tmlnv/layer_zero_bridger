"""Abi for tokens"""
import json
import os

with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'router_abi.json')) as file:
    stargate_abi = json.load(file)
with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdc_abi.json')) as file:
    usdc_abi = json.load(file)
with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'usdt_abi.json')) as file:
    usdt_abi = json.load(file)
with open(os.path.join(os.path.abspath(os.path.join(__file__, os.path.pardir)), 'bungee_refuel_abi.json')) as file:
    bungee_refuel_abi = json.load(file)
