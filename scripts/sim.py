#!/usr/bin/env python3

import time
import random
from multiprocessing.pool import Pool, ThreadPool

import pandas as pd

from arbera.pod import Pod


def generate_activity(num):
    for i in range(0, num):
        operation = {
            'action': 'wrap' if random.randint(0, 1) else 'unwrap',
            'amount': 100 * random.random(),
        }
        yield operation

def run_one(iteration, burn_fee, wrap_fee, unwrap_fee, partner_fee):
    pod = Pod(
        burn_fee=burn_fee,
        wrap_fee=wrap_fee,
        unwrap_fee=unwrap_fee,
        partner_fee=partner_fee,
    )
    for operation in generate_activity(50):
        pod.handle(operation)
    return pod

def main():
    params = []
    results_accumulator = []

    for iteration in range(0, 20):
        for burn_fee in range(0, 50, 5):
            for wrap_fee in range(0, 10, 2):
                for unwrap_fee in range(0, 10, 2):
                    for partner_fee in range(0, 5):
                        this_task = [
                            iteration,
                            burn_fee,
                            wrap_fee,
                            unwrap_fee,
                            partner_fee,
                        ]
                        params.append(this_task)
                    
    print("Starting simulation")
    start_time = time.time()

    with Pool(processes=7) as pool:
        results = pool.starmap(run_one, params)
        for pod, param in zip(results, params):
            result = {
                **dict(zip(["iteration", "burn_fee", "wrap_fee", "unwrap_fee", "partner_fee"], param)),
                "cbr": pod.cbr,
                "rewards": pod.rewards,
                "peas_fee_balance": pod.peas_fee_balance,
                "token0_wrapped_supply": pod.token0_wrapped_supply,
                "token0_balance": pod.token0_balance,
                "partner_fee_balance": pod.partner_fee_balance,
                "burn_fee_balance": pod.burn_fee_balance,
            }

            results_accumulator.append(result)

    end_time = time.time()
    print(f"Finished in {end_time - start_time} seconds")

    df_values = [r.values() for r in results_accumulator]
    df_columns = results_accumulator[0].keys()

    print("Writing results to var/results.csv.gz")
    df = pd.DataFrame(df_values, columns=df_columns)
    df.to_csv("var/results.csv.gz", index=False)
    print("Done")

if __name__ == "__main__":
    main()
