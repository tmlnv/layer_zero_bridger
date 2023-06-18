# Layer Zero Bridger

The Layer Zero Bridger is a Python script that automates the process of transferring USDC or USDT (stablecoin cryptocurrencies) between different blockchains (Polygon->BSC->Polygon in main script). It uses a set of pre-configured wallet addresses to perform transfers in both directions and repeat the process a configurable number of times.

![main.py script logger example for one wallet](https://drive.google.com/uc?export=view&id=1v99Wqi6qa5WA3WJJCuKFcKm8B35HN0rp)

## Supported chains and tokens

- Polygon (USDC, USDT)
- Fantom (USDC)
- Avalanche (USDC, USDT)
- BSC (USDT)

## Requirements

- Python 3.10 or higher
- An understanding of blockchain, cryptocurrency, and how to handle wallets and private keys securely.

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

3. Configure your wallets and number of cycles:

    Specify the wallet keys in the `private_keys.example.env` file and run a command below.

   ```bash
   mv private_keys.example.env private_keys.env
   ```
   
    In the `config.py` file, specify the wallet keys and the number of transfer cycles you want to run.

    ```python
    TIMES = 10  # Number of transfer cycles
    ```
    **Warning: Never disclose your private keys. They are sensitive information.**

## Running the Script

Execute the `main.py` script:

```bash
python main.py
```

**Optional:**

Execute only separated one-time bridging runs if you want just to transfer assets. Consider token availability on both departure and destination chains. Execute the `chain_to_chain.py` script using `--mode` flag with one of possible options:
- `pf` to bridge from Polygon to Fantom
- `pa` to bridge from Polygon to Avalanche
- `pb` to bridge from Polygon to BSC
- `fp` to bridge from Fantom to Polygon
- `fa` to bridge from Fantom to Avalanche
- `fb` to bridge from Fantom to BSC
- `ap` to bridge from Avalanche to Polygon
- `af` to bridge from Avalanche to Fantom
- `ab` to bridge from Avalanche to BSC
- `bp` to bridge from BSC to Polygon
- `bf` to bridge from BSC to Fantom
- `ba` to bridge from BSC to Avalanche

Example:

```bash
python chain_to_chain.py --mode pf
```
**Optional:**

Generate a new private key and its associated address if you require a fresh wallet. Execute the `wallet_generator/wallet_gen.py` script.

Example:

```bash
python wallet_generator/wallet_gen.py
```

## Operation

The main script performs the following actions for each wallet:

1. After a random delay of 1 to 200 seconds, it initiates a USDC transfer from Polygon to BSC. USDT tokens are received on BSC.
2. It waits for a random period between 1200 and 1500 seconds.
3. Then, it initiates a USDT transfer from BSC back to Polygon. USDC tokens are received on Polygon.
4. It waits for a random period between 100 and 300 seconds.
5. These steps are repeated a predefined number of times (`TIMES` in `config.py`).

The script logs all its actions and reports when each wallet's transfers are done and when all tasks are finished.

## Disclaimer

This script is meant for educational purposes. Always ensure you're keeping your private keys secure.

## License

[MIT](https://github.com/tmlnv/layer_zero_bridger/blob/main/LICENSE)
