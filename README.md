# Layer Zero Bridger

The Layer Zero Bridger is a Python script that automates the process of transferring USDC (a stablecoin cryptocurrency) between different blockchains (main use case Polygon and Fantom). It uses a set of pre-configured wallet addresses to perform transfers in both directions and repeat the process a configurable number of times.

## Supported chains

- Polygon
- Fantom
- Avalanche

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

    In the `private_keys.txt` file, specify the wallet keys. Do not leave empty lines.
   
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

Execute only separated one-time bridging runs if you want just to transfer assets:

```bash
python polygon_to_fantom.py
```
```bash
python fantom_to_avalanche.py
```
```bash
python avalanche_to_fantom.py
```
```bash
python fantom_to_polygon.py
```
```bash
python polygon_to_avalanche.py
```
```bash
python avalanche_to_polygon.py
```

## Operation

The main script performs the following actions for each wallet:

1. After a random delay of 1 to 200 seconds, it initiates a USDC transfer from Polygon to Fantom.
2. It waits for a random period between 1200 and 1500 seconds.
3. Then, it initiates a USDC transfer from Fantom back to Polygon.
4. It waits for a random period between 100 and 300 seconds.
5. These steps are repeated a predefined number of times (`TIMES` in `config.py`).

The script logs all its actions and reports when each wallet's transfers are done and when all tasks are finished.

## Disclaimer

This script is meant for educational purposes. Always ensure you're keeping your private keys secure.

## License

[MIT](https://github.com/tmlnv/layer_zero_bridger/blob/main/LICENSE)
