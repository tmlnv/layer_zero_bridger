from termcolor import colored
from eth_account import Account
import secrets


def create_wallet():
    """ Simple function for generating private and public keys."""
    priv = secrets.token_hex(32)  # a random hexadecimal string of 32 bytes / 64 characters
    private_key = "0x" + priv
    print("PRIVATE KEY:", colored(private_key, "light_magenta"))
    acct = Account.from_key(private_key)
    print("ADDRESS:", colored(acct.address, "light_cyan"))
