import pytest

from arbera.sim import generate_params, generate_activity, run_one, run_all


def test_generate_activity():
    activity = list(generate_activity(50))
    assert len(activity) == 50

    actions = [ x['action'] for x in activity ]
    for action in ['wrap', 'unwrap', 'stake_lp', 'unstake_lp']:
        assert action in actions

def test_generate_params():
    params = generate_params()
    assert len(params) > 0

def test_run_one():
    pod = run_one(
        iteration=0,
        wrap_fee=1,
        unwrap_fee=1,
        buy_fee=1,
        sell_fee=1,
        protocol_fee=1,
        partner_fee=1,
        burn_fee=1,
        buyback_fee=1,
    )

    for operation in generate_activity(50):
        pod.handle(operation)

    assert pod.protocol_fee_balance > 0
    assert pod.burn_fee_balance > 0
    assert pod.partner_fee_balance > 0
    assert pod.buyback_fee_balance > 0

    assert pod.base_token_lp_balance > 0
    assert pod.quote_token_lp_balance > 0

    assert pod.cbr > 1.0
    assert pod.cbr_apr > 0.0
    assert pod.lp_tvl > 0.0
    assert pod.lp_apr > 0.0

    assert pod.total_lp_incentives > 0
    assert pod.arbitrage_ratio != 0.0
