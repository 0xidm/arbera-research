import pytest

from arbera.pod import Pod


def test_create():
    pod = Pod()
    assert pod
    assert pod.cbr == 0

def test_wrap():
    pod = Pod()
    pod.wrap(100) # TOKEN

    assert pod.base_token_balance == 100
    assert pod.base_token_wrapped_supply < 100
    assert pod.cbr > 1.00

def test_unwrap():
    pod = Pod()
    pod.wrap(100) # TOKEN
    pod.unwrap(50) # TOKEN

    assert pod.base_token_wrapped_supply < 50
    assert pod.cbr > 1.01
    assert pod.cbr_apr > 2.00

def test_stake_lp():
    pod = Pod()
    pod.wrap(100) # TOKEN
    pod.stake_lp(90) # TOKEN

    assert pod.lp_tvl > 0.0
    assert pod.lp_apr > 0.0

def test_fees():
    pod = Pod()

    assert pod.protocol_fee_balance == 0
    assert pod.burn_fee_balance == 0
    assert pod.partner_fee_balance == 0
    assert pod.buyback_fee_balance == 0

    pod.wrap(100) # TOKEN
    pod.unwrap(50) # TOKEN

    assert pod.protocol_fee_balance > 0
    assert pod.burn_fee_balance > 0
    assert pod.partner_fee_balance > 0
    assert pod.buyback_fee_balance > 0
