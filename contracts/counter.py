from pyteal import *

def approval_program() -> Expr:
	count_key = Bytes("count")

	return Seq(
		# App creation -> initialize
		If(Txn.application_id() == Int(0)).Then(
			Seq(
				App.globalPut(count_key, Int(0)),
				Return(Int(1)),
			)
		),

		# Admin controls
		If(Txn.on_completion() == OnComplete.DeleteApplication).Then(
			Return(Txn.sender() == Global.creator_address())
		),
		If(Txn.on_completion() == OnComplete.UpdateApplication).Then(
			Return(Txn.sender() == Global.creator_address())
		),

		# Allow users to leave/opt-in freely
		If(Txn.on_completion() == OnComplete.CloseOut).Then(Return(Int(1))),
		If(Txn.on_completion() == OnComplete.OptIn).Then(Return(Int(1))),

		# Handle simple method calls by first arg
		If(Txn.application_args.length() == Int(1)).Then(
			Seq(
				If(Txn.application_args[0] == Bytes("inc")).Then(
					App.globalPut(count_key, App.globalGet(count_key) + Int(1))
				),
				If(Txn.application_args[0] == Bytes("dec")).Then(
					App.globalPut(count_key, App.globalGet(count_key) - Int(1))
				),
				If(Txn.application_args[0] == Bytes("reset")).Then(
					App.globalPut(count_key, Int(0))
				),
				Return(Int(1)),
			)
		),

		# Anything else -> reject
		Return(Int(0))
	)


def clear_state_program() -> Expr:
	return Return(Int(1))


if __name__ == "__main__":
	# Local compile helper
	import os
	from pyteal import compileTeal

	artifacts_dir = os.path.join("artifacts")
	os.makedirs(artifacts_dir, exist_ok=True)

	approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=8)
	clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=8)

	with open(os.path.join(artifacts_dir, "counter_approval.teal"), "w", encoding="utf-8") as f:
		f.write(approval_teal)
	with open(os.path.join(artifacts_dir, "counter_clear.teal"), "w", encoding="utf-8") as f:
		f.write(clear_teal)
	print("Wrote artifacts/counter_*.teal")
