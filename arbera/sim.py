import time
import random
import itertools

from multiprocessing.pool import Pool, ThreadPool

import pandas as pd
import hiplot as hip

from arbera.pod import Pod


def generate_activity(num):
    for i in range(0, num):
        actions = [
            'wrap',
            'unwrap',
            'stake_lp',
            'unstake_lp',
        ]
        action = actions[random.randint(0, len(actions)-1)]

        operation = {
            'action': action,
            'amount': 100 * random.random(),
        }

        yield operation

def run_one(iteration, wrap_fee, unwrap_fee, buy_fee, sell_fee, protocol_fee, partner_fee, burn_fee, buyback_fee):
    pod = Pod(
        arbera_price_usd=2.5,
        base_token="TOKEN",
        base_price_usd=0.15,
        quote_token="HONEY",
        quote_price_usd=1.0,
        wrap_fee=wrap_fee,
        unwrap_fee=unwrap_fee,
        buy_fee=buy_fee,
        sell_fee=sell_fee,
        protocol_fee=protocol_fee,
        partner_fee=partner_fee,
        buyback_fee=buyback_fee,
        burn_fee=burn_fee,
    )

    for operation in generate_activity(200):
        pod.handle(operation)
        pod.tick()

    return pod

def generate_params():
    search_params = {
        "iteration": range(0, 10),
        "wrap_fee": range(1, 20, 4),
        "unwrap_fee": range(1, 20, 4),
        "buy_fee": range(1, 20, 4),
        "sell_fee": range(1, 20, 4),
        "protocol_fee": range(1, 5),
        "partner_fee": range(1, 5),
        "burn_fee": range(1, 45, 9),
        "buyback_fee": range(1, 5),
    }

    keys, values = zip(*search_params.items())
    params = [v for v in itertools.product(*values)]

    return search_params, params

def run_all(params, varnames):
    results_accumulator = []

    with Pool(processes=7) as pool:
        results = pool.starmap(run_one, params)
        for pod, param in zip(results, params):
            result = {
                **dict(zip(varnames, param)),
                "cbr": (pod.cbr-1) * 100,
                "total_lp_incentives": pod.total_lp_incentives,
                "arbera_fee_balance": pod.buyback_fee_balance,
                "base_token_wrapped_supply": pod.base_token_wrapped_supply,
                "base_token_balance": pod.base_token_balance,
                "partner_fee_balance": pod.partner_fee_balance,
                "protocol_fee_balance": pod.protocol_fee_balance,
                "burn_fee_balance": pod.burn_fee_balance,
            }

            results_accumulator.append(result)

    return results_accumulator

def write_csv(results_accumulator):
    df_values = [r.values() for r in results_accumulator]
    df_columns = results_accumulator[0].keys()

    print("Writing results to var/results.csv.gz")
    df = pd.DataFrame(df_values, columns=df_columns)
    df.to_csv("var/results.csv.gz", index=False)
    print("Done")

    return df

def main():
    search_params, params = generate_params()

    start_time = time.time()
    print(f"Starting simulation with {len(params)} iterations")

    results_accumulator = run_all(params, search_params.keys())

    end_time = time.time()
    print(f"Finished in {end_time - start_time} seconds")

    df = write_csv(results_accumulator)
    df_sample = df.sample(n=50_000)

    h = hip.Experiment.from_dataframe(df_sample)
    h.parameters_definition["cbr"].type = hip.ValueType.NUMERIC_LOG
    h.to_html('docs/parameters.html')

if __name__ == "__main__":
    main()
