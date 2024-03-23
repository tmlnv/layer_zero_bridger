# Layer Zero Bridger

The Layer Zero Bridger is a Python script that automates the process of transferring USDC or USDT (stablecoin cryptocurrencies) between different blockchains (Polygon -> Avalanche -> BSC -> Polygon as a default route). It uses a set of pre-configured wallet addresses to perform transfers in both directions and repeat the process a configurable number of times.
In addition to this, it is also possible to use script for Bungee Refuel, wallet balance checking, new wallets generation and more.

![main.py script logger example for one wallet](https://drive.google.com/uc?export=view&id=1D-kc1iyD6cSAHgX4EjYQA-lfJY_sTMJz)

## Supported chains and tokens

- Polygon (USDC, USDT)
- Fantom (USDC)
- Avalanche (USDC, USDT)
- BSC (USDT)
- Arbitrum (USDT, USDC)
- Optimism (USDC)
- Base (USDC)

## Requirements

- Python 3.11
- An understanding of blockchain, cryptocurrency, and how to handle wallets and private keys securely.
- Docker (optional)

## Getting Started

1. Clone the repository:

    ```bash
    git clone https://github.com/tmlnv/layer_zero_bridger.git
    cd layer_zero_bridger
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```
   
   Or, using Docker:
   
   ```bash
   docker build -t layer_zero_bridger .
   ```

3. Configure your wallets and number of cycles:

    Specify the wallet keys in the `private_keys.example.env` file and run a command below.  
    _Note_: keys should be specified with a name for each key in a `KEY=value` way.

   ```bash
   mv private_keys.example.env private_keys.env
   ```
   
    In the `config.py` file, specify the min and max $ amounts for transferring, the number of transfer cycles you want to run and a $ amount for Bungee Refueling.

    ```python
    AMOUNT_MIN = 100  # Min amount to bridge
    AMOUNT_MAX = 150  # Max amount to bridge
    # If stated amounts exceed wallet balance, the whole available balance would be bridged
    TIMES = 10  # Number of transfer cycles
    BUNGEE_AMOUNT = 10  # $ value of native asset to be bridged via Bungee Refuel
    ```
    **Warning: Never disclose your private keys. They are sensitive information.**

## Usage

Execute the `main.py` script:

```bash
python main.py
```

Or, using Docker:

```bash
docker run layer_zero_bridger -v ./private_keys.env:/app/private_keys.env
```

To pass CLI arguments, append them after the image name and private_keys.env mounting:

```bash
docker run layer_zero_bridger -v ./private_keys.env:/app/private_keys.env --mode balance
````

## Operation

The main script performs the following actions for each wallet:

1. After a random delay of 1 to 200 seconds, it initiates a USDC transfer from Polygon to Avalanche.
2. It waits for a random period between 1200 and 1500 seconds.
3. Then, it initiates a USDC transfer from Avalanche to BSC. USDT tokens are received on BSC.
4. It waits for a random period between 1200 and 1500 seconds.
5. Then, it initiates a USDT transfer from BSC back to Polygon. USDC tokens are received on Polygon.
6. It waits for a random period between 100 and 300 seconds.
7. These steps are repeated a predefined number of times (`TIMES` in `config.py`).

The script logs all its actions and reports when each wallet's transfers are done and when all tasks are finished.

## Modules usage

To use separate modules, execute the `main.py` script using `--mode` flag with one of possible options or pass the `--mode` flag followed by the specific option to the Docker run command:

### One way bridge

Execute only separated one-time bridging runs if you want just to transfer assets. Consider token availability on both departure and destination chains. Execute the `main.py` script using `--mode one-way` flag with one of possible options:
- `pf` to bridge from Polygon to Fantom
- `pa` to bridge from Polygon to Avalanche
- `pb` to bridge from Polygon to BSC
- `parb` to bridge from Polygon to Arbitrum
- `po` to bridge from Polygon to Optimism
- `pbase` to bridge from Polygon to Base
- `fp` to bridge from Fantom to Polygon
- `fa` to bridge from Fantom to Avalanche
- `fb` to bridge from Fantom to BSC
- `ap` to bridge from Avalanche to Polygon
- `af` to bridge from Avalanche to Fantom
- `ab` to bridge from Avalanche to BSC
- `aarb` to bridge from Avalanche to Arbitrum
- `ao` to bridge from Avalanche to Optimism
- `abase` to bridge from Avalanche to Base
- `bp` to bridge from BSC to Polygon
- `bf` to bridge from BSC to Fantom
- `ba` to bridge from BSC to Avalanche
- `barb` to bridge from BSC to Arbitrum
- `bo` to bridge from BSC to Optimism
- `bbase` to bridge from BSC to Base
- `arbp` to bridge from Arbitrum to Polygon
- `arba` to bridge from Arbitrum to Avalanche
- `arbb` to bridge from Arbitrum to BSC
- `arbo` to bridge from Arbitrum to Optimism
- `arbbase` to bridge from Arbitrum to Base
- `op` to bridge from Optimism to Polygon
- `oa` to bridge from Optimism to Avalanche
- `ob` to bridge from Optimism to BSC
- `oarb` to bridge from Optimism to Arbitrum
- `obase` to bridge from Optimism to Base
- `basep` to bridge from Base to Polygon
- `basea` to bridge from Base to Avalanche
- `baseb` to bridge from Base to BSC
- `basearb` to bridge from Base to Arbitrum
- `baseo` to bridge from Base to Optimism

Example:

```bash
python main.py --mode one-way pf
```
### New wallet

Generate a new private key and its associated address if you require a fresh wallet. Execute the `main.py` script using `--mode new-wallet` flag.

Example:

```bash
python main.py --mode new-wallet
```

### Checking Balances

Check wallet balances. Execute the `main.py` script using `--mode balance` flag.

Example:

```bash
python main.py --mode balance
```

### Bungee Refuel

Get native tokens on the destination chain to pay fees using Bungee Refuel. Execute the `main.py` script using `--mode refuel` flag with one of possible options:
- `pa` to refuel from Polygon to Avalanche
- `pb` to refuel from Polygon to BSC
- `parb` to refuel from Polygon to Arbitrum
- `po` to refuel from Polygon to Optimism
- `pbase` to refuel from Polygon to Base
- `ap` to refuel from Avalanche to Polygon
- `ab` to refuel from Avalanche to BSC
- `aarb` to refuel from Avalanche to Arbitrum
- `ao` to refuel from Avalanche to Optimism
- `abase` to refuel from Avalanche to Base
- `bp` to refuel from BSC to Polygon
- `ba` to refuel from BSC to Avalanche
- `barb` to refuel from BSC to Arbitrum
- `bo` to refuel from BSC to Optimism
- `bbase` to refuel from BSC to Base
- `arbp` to refuel from Arbitrum to Polygon
- `arba` to refuel from Arbitrum to Avalanche
- `arbb` to refuel from Arbitrum to BSC
- `arbo` to refuel from Arbitrum to Optimism
- `arbbase` to refuel from Arbitrum to Base
- `op` to refuel from Optimism to Polygon
- `oa` to refuel from Optimism to Avalanche
- `ob` to refuel from Optimism to BSC
- `oarb` to refuel from Optimism to Arbitrum
- `obase` to refuel from Optimism to Base
- `basep` to refuel from Base to Polygon
- `basea` to refuel from Base to Avalanche
- `baseb` to refuel from Base to BSC
- `basearb` to refuel from Base to Arbitrum
- `baseo` to refuel from Base to Optimism

Example:

```bash
python main.py --mode refuel pa
```
_Note_: Consider that Bungee Refuel has different limits for different chains.

## Disclaimer

This script is meant for educational purposes. Always ensure you're keeping your private keys secure.

## License

[MIT](https://github.com/tmlnv/layer_zero_bridger/blob/main/LICENSE)
