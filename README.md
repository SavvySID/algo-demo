# Algorand Demo: Stateful Counter dApp + Stateless Escrow

This repo contains a minimal, working Algorand demo with:
- A stateful Counter smart contract (PyTEAL) with `inc`, `dec`, `reset` methods
- A stateless Escrow (LogicSig) that only allows controlled payments
- Python scripts to compile, deploy, and interact on TestNet

## Prerequisites
- Python 3.9+
- An Algorand TestNet account (fund via the TestNet dispenser)
- Windows PowerShell or any shell

## Install
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1  # On PowerShell
pip install -r requirements.txt
```

## Configuration
By default this project uses the public TestNet endpoint (no API key required):
- ALGOD_ADDRESS: https://testnet-api.algonode.cloud
- ALGOD_TOKEN: "" (empty string)

Create a `.env` in the repository root with your TestNet account mnemonic:
```bash
ALGOD_ADDRESS=https://testnet-api.algonode.cloud
ALGOD_TOKEN=
MNEMONIC="your 25-word mnemonic here"
```
Never use a MainNet mnemonic for testing.

## Project Structure
```
contracts/
  counter.py        # PyTEAL stateful counter
  escrow.py         # PyTEAL stateless escrow (LogicSig)
scripts/
  utils.py          # Shared client/account helpers
  compile_contracts.py
  deploy_counter.py
  call_counter.py
  escrow_tools.py   # compile/fund/withdraw for escrow
artifacts/           # compiled TEAL, app ids, addresses
```

Create the `artifacts/` folder if it doesn’t exist.

## Usage
Ensure your `.env` is set. Activate your venv before running scripts.

1) Compile contracts
```bash
python -m scripts.compile_contracts
```

2) Deploy counter dApp
```bash
python -m scripts.deploy_counter
```
Outputs `artifacts/counter_app_id.txt`.

3) Interact with counter
```bash
python -m scripts.call_counter inc
python -m scripts.call_counter dec
python -m scripts.call_counter reset
python -m scripts.call_counter read
```

4) Escrow: compile with parameters
```bash
python -m scripts.escrow_tools compile --receiver RECEIVER_ADDR --max 1000000
```
Outputs `artifacts/escrow.teal` and `artifacts/escrow_address.txt`.

5) Fund escrow (send from your account to the escrow address)
```bash
python -m scripts.escrow_tools fund --amount 200000
```

6) Withdraw from escrow to receiver (must be <= max and match receiver)
```bash
python -m scripts.escrow_tools withdraw --amount 100000
```

## Notes
- All scripts target TestNet.
- Keep your mnemonic safe. `.env` is used locally and should not be committed.

### Tips
- The `--receiver` must be a valid Algorand address (base32 string). You can use your own account from `.env`. Print it quickly (PowerShell):
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); from algosdk import mnemonic, account; pk = mnemonic.to_private_key(os.getenv('MNEMONIC')); print(account.address_from_private_key(pk))"
```
