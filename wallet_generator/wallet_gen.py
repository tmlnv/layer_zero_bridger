from eth_account import Account
import secrets

priv = secrets.token_hex(32)  # a random hexadecimal string of 32 bytes / 64 characters
private_key = "0x" + priv
print("PRIVATE KEY:", private_key)
acct = Account.from_key(private_key)
print("Address:", acct.address)
