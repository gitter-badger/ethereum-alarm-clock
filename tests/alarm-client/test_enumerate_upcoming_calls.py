from ethereum import utils
from populus.utils import wait_for_transaction

from alarm_client.client import enumerate_upcoming_calls


deploy_max_wait = 15
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_enumerate_upcoming_tree_positions(geth_node, rpc_client, deployed_contracts):
    alarm = deployed_contracts.Alarm
    client_contract = deployed_contracts.SpecifyBlock

    anchor_block = rpc_client.get_block_number()

    blocks = (1, 4, 4, 8, 15, 25, 25, 25, 30, 40, 50, 60)

    call_keys = []

    for n in blocks:
        wait_for_transaction(rpc_client, client_contract.scheduleIt.sendTransaction(alarm._meta.address, anchor_block + 100 + n))

        last_call_key = alarm.getLastCallKey.call()
        assert last_call_key is not None

        call_keys.append(last_call_key)

    expected_calls = tuple(utils.encode_hex(c) for c in call_keys[1:10])
    actual_calls = tuple(utils.encode_hex(c) for c in enumerate_upcoming_calls(alarm, anchor_block + 100 + 4))
    assert actual_calls == expected_calls
