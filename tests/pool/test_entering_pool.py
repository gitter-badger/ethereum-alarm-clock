from populus.utils import wait_for_transaction, wait_for_block


deploy_max_wait = 30
deploy_max_first_block_wait = 180
deploy_wait_for_block = 1

geth_max_wait = 45


def test_entering_pool(geth_node, geth_coinbase, rpc_client, deployed_contracts):
    caller_pool = deployed_contracts.CallerPool

    assert caller_pool.callerBonds.call(geth_coinbase) == 0
    deposit_amount = caller_pool.getMinimumBond.call() * 10

    txn_1_hash = caller_pool.depositBond.sendTransaction(value=deposit_amount)
    wait_for_transaction(rpc_client, txn_1_hash)

    assert caller_pool.isInAnyPool.call() is False
    assert caller_pool.canEnterPool.call() is True

    wait_for_transaction(rpc_client, caller_pool.enterPool.sendTransaction())

    # Now queued to be in the next pool.
    assert caller_pool.getActivePoolKey.call() == 0
    assert caller_pool.isInAnyPool.call() is True
    assert caller_pool.canEnterPool.call() is False

    next_pool_key = caller_pool.getNextPoolKey.call()
    assert next_pool_key > 0
    assert caller_pool.isInPool.call(next_pool_key) is True

    wait_for_block(rpc_client, next_pool_key, 180)

    assert caller_pool.isInAnyPool.call() is True
    assert caller_pool.canEnterPool.call() is False
