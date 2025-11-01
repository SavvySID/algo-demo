import json
import os
import base64
from algosdk.transaction import ApplicationCreateTxn, OnComplete, StateSchema
from algosdk.v2client.algod import AlgodClient
from algosdk import transaction
from scripts.utils import get_algod_client, get_private_key_from_env, ensure_dir, write_text


ARTIFACTS_DIR = "artifacts"


def compile_teal(client: AlgodClient, teal_source_path: str) -> bytes:
	with open(teal_source_path, "r", encoding="utf-8") as f:
		source = f.read()
	comp = client.compile(source)
	return base64.b64decode(comp["result"])  # result is base64-encoded


def wait_for_confirmation(client: AlgodClient, txid: str) -> dict:
	return transaction.wait_for_confirmation(client, txid, 10)


def main() -> None:
	ensure_dir(ARTIFACTS_DIR)
	client = get_algod_client()
	creator, sk = get_private_key_from_env()

	approval_bin = compile_teal(client, os.path.join(ARTIFACTS_DIR, "counter_approval.teal"))
	clear_bin = compile_teal(client, os.path.join(ARTIFACTS_DIR, "counter_clear.teal"))

	sp = client.suggested_params()
	global_schema = StateSchema(num_uints=1, num_byte_slices=0)
	local_schema = StateSchema(num_uints=0, num_byte_slices=0)

	txn = ApplicationCreateTxn(
		sender=creator,
		sp=sp,
		on_complete=OnComplete.NoOpOC,
		approval_program=approval_bin,
		clear_program=clear_bin,
		global_schema=global_schema,
		local_schema=local_schema,
	)
	signed = txn.sign(sk)
	txid = client.send_transaction(signed)
	confirmed = wait_for_confirmation(client, txid)
	app_id = confirmed["application-index"]

	write_text(os.path.join(ARTIFACTS_DIR, "counter_app_id.txt"), str(app_id))
	print(f"Deployed counter app. App ID: {app_id}")


if __name__ == "__main__":
	main()
