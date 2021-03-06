from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45
geth_chain_name = "default-test-lower-gas-limit"


def test_infinite_loop_protection(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.InfiniteLoop

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)
    rpc_client.send_transaction(to=client_contract._meta.address, value=1000000000)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None
    wait_for_block(rpc_client, alarm.getCallTargetBlock.call(callKey), 300)
    call_txn_hash = alarm.doCall.sendTransaction(callKey)
    call_txn_receipt = wait_for_transaction(alarm._meta.rpc_client, call_txn_hash)
    call_txn = rpc_client.get_transaction_by_hash(call_txn_hash)

    assert alarm.checkIfCalled.call(callKey) is True
    assert alarm.checkIfSuccess.call(callKey) is False

    assert call_txn_receipt['gasUsed'] == call_txn['gas']
