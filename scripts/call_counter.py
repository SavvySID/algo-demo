import argparse
import os
from typing import Any, Dict
from algosdk.v2client.algod import AlgodClient
from algosdk import transaction
from algosdk.transaction import ApplicationNoOpTxn
from scripts.utils import get_algod_client, get_private_key_from_env


ARTIFACTS_DIR = "artifacts"


def wait_for_confirmation(client: AlgodClient, txid: str) -> Dict[str, Any]:
	return transaction.wait_for_confirmation(client, txid, 10)


def read_global_state(client: AlgodClient, app_id: int) -> Dict[str, Any]:
	app = client.application_info(app_id)
	kvs = app["params"].get("global-state", [])
	decoded = {}
	for kv in kvs:
		key = kv["key"]
		# global-state keys are base64 strings
		import base64
		k_decoded = base64.b64decode(key).decode()
		if "uint" in kv["value"]:
			decoded[k_decoded] = kv["value"]["uint"]
		else:
			decoded[k_decoded] = kv["value"]["bytes"]
	return decoded


def call_method(action: str) -> None:
	client = get_algod_client()
	sender, sk = get_private_key_from_env()

	with open(os.path.join(ARTIFACTS_DIR, "counter_app_id.txt"), "r", encoding="utf-8") as f:
		app_id = int(f.read().strip())

	if action == "read":
		state = read_global_state(client, app_id)
		print(state)
		return

	sp = client.suggested_params()
	args = [action.encode()]
	txn = ApplicationNoOpTxn(sender, sp, app_id, app_args=args)
	signed = txn.sign(sk)
	txid = client.send_transaction(signed)
	confirmed = wait_for_confirmation(client, txid)
	print(f"Called {action}. Round: {confirmed['confirmed-round']}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Call counter app")
	parser.add_argument("action", choices=["inc", "dec", "reset", "read"], help="Action to perform")
	args = parser.parse_args()
	call_method(args.action)
