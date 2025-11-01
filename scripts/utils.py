import os
from typing import Tuple
from dotenv import load_dotenv
from algosdk.v2client import algod
from algosdk import mnemonic as algo_mnemonic
from algosdk import account as algo_account

load_dotenv()

DEFAULT_ALGOD_ADDRESS = os.getenv("ALGOD_ADDRESS", "https://testnet-api.algonode.cloud")
DEFAULT_ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")


def get_algod_client() -> algod.AlgodClient:
	algod_address = DEFAULT_ALGOD_ADDRESS
	algod_token = DEFAULT_ALGOD_TOKEN
	return algod.AlgodClient(algod_token, algod_address)


def get_private_key_from_env() -> Tuple[str, str]:
	mn = os.getenv("MNEMONIC")
	if not mn:
		raise RuntimeError("MNEMONIC not set in environment/.env")
	private_key = algo_mnemonic.to_private_key(mn)
	address = algo_account.address_from_private_key(private_key)
	return address, private_key


def ensure_dir(path: str) -> None:
	os.makedirs(path, exist_ok=True)


def write_text(path: str, content: str) -> None:
	ensure_dir(os.path.dirname(path) or ".")
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)


def read_text(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()
