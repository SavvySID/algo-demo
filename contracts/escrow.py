from pyteal import *

def escrow(receiver: str, max_amount: int) -> Expr:
	return And(
		Txn.type_enum() == TxnType.Payment,
		Txn.receiver() == Addr(receiver),
		Txn.amount() <= Int(max_amount),
		Txn.close_remainder_to() == Global.zero_address(),
		Txn.rekey_to() == Global.zero_address(),
	)

if __name__ == "__main__":
	import argparse
	from pyteal import compileTeal
	import os

	parser = argparse.ArgumentParser(description="Compile escrow teal")
	parser.add_argument("--receiver", required=True, help="Receiver address")
	parser.add_argument("--max", required=True, type=int, help="Max amount per payment (microAlgos)")
	args = parser.parse_args()

	program = escrow(args.receiver, args.max)
	teal = compileTeal(program, mode=Mode.Signature, version=8)

	os.makedirs("artifacts", exist_ok=True)
	path = os.path.join("artifacts", "escrow.teal")
	with open(path, "w", encoding="utf-8") as f:
		f.write(teal)
	print(f"Wrote {path}")