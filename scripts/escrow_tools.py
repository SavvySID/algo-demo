import argparse
import base64
import os
from typing import Any, Dict

from algosdk import logic
from algosdk.v2client.algod import AlgodClient
from algosdk import transaction
from algosdk.transaction import PaymentTxn, LogicSigTransaction, LogicSigAccount

from scripts.utils import get_algod_client, get_private_key_from_env, ensure_dir, write_text, read_text


ARTIFACTS_DIR = "artifacts"
ESCROW_TEAL = os.path.join(ARTIFACTS_DIR, "escrow.teal")
ESCROW_ADDR_PATH = os.path.join(ARTIFACTS_DIR, "escrow_address.txt")


def compile_teal(client: AlgodClient, teal_source_path: str) -> bytes:
	with open(teal_source_path, "r", encoding="utf-8") as f:
		source = f.read()
	comp = client.compile(source)
	return base64.b64decode(comp["result"])  # bytes program


def wait_for_confirmation(client: AlgodClient, txid: str) -> Dict[str, Any]:
	return transaction.wait_for_confirmation(client, txid, 10)


def do_compile(receiver: str, max_amount: int) -> None:
	ensure_dir(ARTIFACTS_DIR)
	# call contracts/escrow.py to render TEAL
	cmd = f"python contracts/escrow.py --receiver {receiver} --max {max_amount}"
	print(cmd)
	ret = os.system(cmd)
	if ret != 0:
		raise RuntimeError("Failed to render escrow TEAL")

	client = get_algod_client()
	program = compile_teal(client, ESCROW_TEAL)
	lsig_addr = logic.address(program)
	write_text(ESCROW_ADDR_PATH, lsig_addr)
	print(f"Escrow address: {lsig_addr}")


def do_fund(amount: int) -> None:
	client = get_algod_client()
	sender, sk = get_private_key_from_env()
	lsig_addr = read_text(ESCROW_ADDR_PATH).strip()
	sp = client.suggested_params()
	txn = PaymentTxn(sender=sender, sp=sp, receiver=lsig_addr, amt=amount)
	signed = txn.sign(sk)
	txid = client.send_transaction(signed)
	confirmed = wait_for_confirmation(client, txid)
	print(f"Funded escrow {lsig_addr} with {amount} microAlgos @ round {confirmed['confirmed-round']}")


def do_withdraw(amount: int) -> None:
	client = get_algod_client()
	receiver = None
	# Extract receiver from the TEAL (best-effort hint) or just require user to know it
	# Here we trust the TEAL and the network to enforce receiver; we simply send to that same receiver
	with open(ESCROW_TEAL, "r", encoding="utf-8") as f:
		for line in f:
			if line.strip().startswith("addr "):
				receiver = line.strip().split()[1]
				break
	if not receiver:
		raise RuntimeError("Cannot find receiver in escrow.teal; recompile with receiver")

	program = compile_teal(client, ESCROW_TEAL)
	lsig = LogicSigAccount(program)
	lsig_addr = logic.address(program)
	sp = client.suggested_params()
	txn = PaymentTxn(sender=lsig_addr, sp=sp, receiver=receiver, amt=amount)
	lstx = LogicSigTransaction(txn, lsig)
	txid = client.send_transaction(lstx)
	confirmed = wait_for_confirmation(client, txid)
	print(f"Withdrew {amount} microAlgos from escrow to {receiver} @ round {confirmed['confirmed-round']}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Escrow tools")
	sub = parser.add_subparsers(dest="cmd", required=True)

	p_compile = sub.add_parser("compile", help="Compile escrow with receiver and max")
	p_compile.add_argument("--receiver", required=True)
	p_compile.add_argument("--max", required=True, type=int)

	p_fund = sub.add_parser("fund", help="Fund escrow address from your account")
	p_fund.add_argument("--amount", required=True, type=int)

	p_withdraw = sub.add_parser("withdraw", help="Withdraw from escrow to receiver via LogicSig")
	p_withdraw.add_argument("--amount", required=True, type=int)

	args = parser.parse_args()
	if args.cmd == "compile":
		do_compile(args.receiver, args.max)
	elif args.cmd == "fund":
		do_fund(args.amount)
	elif args.cmd == "withdraw":
		do_withdraw(args.amount)
