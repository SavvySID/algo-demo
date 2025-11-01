import os
import subprocess
from pyteal import compileTeal, Mode
from contracts.counter import approval_program, clear_state_program
from scripts.utils import ensure_dir


def main() -> None:
	ensure_dir("artifacts")

	approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=8)
	clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=8)

	with open("artifacts/counter_approval.teal", "w", encoding="utf-8") as f:
		f.write(approval_teal)
	with open("artifacts/counter_clear.teal", "w", encoding="utf-8") as f:
		f.write(clear_teal)
	print("Wrote artifacts/counter_*.teal")

	# Compile escrow with defaults only if args provided externally; otherwise skip
	# Provide a simple hint
	print("Escrow TEAL can be compiled via: python contracts/escrow.py --receiver <ADDR> --max <AMT>")


if __name__ == "__main__":
	main()
