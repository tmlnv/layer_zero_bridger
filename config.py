import random

AMOUNT_MIN = 100  # Min amount to bridge
AMOUNT_MAX = 150  # Max amount to bridge
TIMES = 1  # Number of runs

AMOUNT_TO_SWAP = random.randint(AMOUNT_MIN, AMOUNT_MAX)  # Bridge Quantity Randomization

with open('private_keys.txt', 'r') as f:
    WALLETS = [row.strip() for row in f]
