from populus.contracts import get_max_gas
from populus.utils import wait_for_transaction

deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_executing_scheduled_call(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.PassesUInt

    deposit_amount = get_max_gas(rpc_client) * rpc_client.get_gas_price() * 20
    alarm.deposit.sendTransaction(client_contract._meta.address, value=deposit_amount)

    txn_hash = client_contract.scheduleIt.sendTransaction(alarm._meta.address, 3)
    wait_for_transaction(client_contract._meta.rpc_client, txn_hash)

    callKey = alarm.getLastCallKey.call()
    assert callKey is not None

    call_data = alarm.getCallData.call(callKey)
    assert call_data == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03'
