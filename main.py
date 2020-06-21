import random
import numpy as np
from pprint import pprint
from multiprocessing import Pool

T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, PRI, DUO, TRI, TET, PEN = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20

TIERS = ['+0', '+1', '+2', '+3', '+4', '+5', '+6', '+7', '+8', '+9', '+10', '+11', '+12', '+13', '+14', '+15', 'PRI', 'DUO', 'TRI', 'TET', 'PEN']

success_rates_by_tier = [1, 1, 1, 1, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.15, 0.1, 0.30, 0.25, 0.2, 0.15, 0.06]
gem_cost_by_tier = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 5, 10, 10, 10, 10, 10]
dura_loss_by_tier = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10]

NB_SIM = 10000

MEM_PRICE  = 1800000
GEM_PRICE  = 800000
BASE_PRICE = 250000000

def do_enhance(tier):
    success_rate = success_rates_by_tier[tier]
    faillure_rate = 1 - success_rate
    result = random.choices([True, False], [success_rate, faillure_rate])[0]

    if result:
        return tier + 1
    elif tier <= PRI:
        return tier
    else:
        return tier - 1

def simulate(base, goal, limit=0):
    nb = [0] * len(TIERS)
    fails = [0] * len(TIERS)
    total = 0
    current = base
    while current != goal and (total < limit or limit == 0):
        nb[current] += 1
        total += 1
        new = do_enhance(current)
        if new <= current:
            fails[current] += 1
        current = new
    return {
        'total_attempts': total,
        'attempts': nb,
        'failed_attempts': fails,
        'final_tier': current,
        'total_cost': np.sum(
                        [nb[tier] * gem_cost_by_tier[tier] * GEM_PRICE + fails[tier] * dura_loss_by_tier[tier] * MEM_PRICE 
                            for tier in range(len(TIERS)-1)]
                )
    }

def print_by_tier(data):
    return [print(f'\t{TIERS[i]}->{TIERS[i+1]}: {d}') for i, d in enumerate(data) if d > 0]

def print_result(data, percentiles=[0, 25, 50, 75, 100]):
    ptotal = np.percentile([simulation['total_attempts'] for simulation in simulations], percentiles)
    print(f'#Total attempts:')
    for i, total in enumerate(ptotal):
        print(f'\t{percentiles[i]}% < {int(total)}')

    pattempts = [np.percentile([simulation['attempts'][tier] for simulation in simulations], percentiles) for tier in range(len(TIERS))]
    print('#Attempts by tier:')
    for t, patt in enumerate(pattempts[:-1]):
        if any([int(att) != 0 for att in patt]):
            print(f"\t{TIERS[t]}->{TIERS[t + 1]}:\t{[f'{percentiles[p]}% < {int(att)}' for p, att in enumerate(patt)]}")

    pcost = np.percentile([simulation['total_cost'] for simulation in simulations], percentiles)
    print('#Cost:')
    for i, cost in enumerate(pcost):
        print(f'\t{percentiles[i]}% < {int(cost):,}')
    
    pfinal = np.percentile([simulation['final_tier'] for simulation in simulations], percentiles)
    print('#Final Tier:')
    for i, final in enumerate(pfinal):
        print(f'\t{percentiles[i]}% < {TIERS[int(final)]}')

    #[print(f'\t{TIERS[i]}->{TIERS[i+1]}: {pa}') for i, pa in enumerate(pattempts) if p > 0]

if __name__ == "__main__":

    base_tier = T0
    goal_tier = TET
    max_gem = 0

    with Pool(processes=15) as pool:
            simulations = pool.starmap(simulate, list(zip([base_tier], [goal_tier], [max_gem])) * NB_SIM , 15)

    print_result(simulations, [33, 50, 66, 99])