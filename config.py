import random

from dotenv import dotenv_values

AMOUNT_MIN = 100  # Min amount to bridge
AMOUNT_MAX = 150  # Max amount to bridge
# If stated amounts exceed wallet balance, the whole available balance would be bridged
TIMES = 1  # Number of runs

AMOUNT_TO_SWAP = random.randint(AMOUNT_MIN, AMOUNT_MAX)  # Bridge Quantity Randomization

private_keys = dotenv_values("private_keys.env")
PRIVATE_KEYS = [key for key in private_keys.values()]

BUNGEE_AMOUNT = 4.5  # $ value of native asset to be bridged via Bungee Refuel
