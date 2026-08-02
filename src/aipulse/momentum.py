"""Momentum tracking: detect rising and falling topics over time.

Momentum measures term frequency changes between consecutive time periods.
Rising topics are those whose frequency increased significantly (>20%).
Falling topics are those whose frequency decreased significantly (>20%).

This enables detection of emerging trends and fading ones at a glance.
"""

from collections import Counter
from typing import List, Tuple, Dict

def compute_momentum(
    prev_counts: Dict[str, int],
    curr_counts: Dict[str, int],
    threshold: float = 0.2
) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
    """Compute rising and falling topics between two periods.

    Args:
        prev_counts: term frequency dict from previous period
        curr_counts: term frequency dict from current period
        threshold: minimum relative change to qualify as rising/falling

    Returns:
        (rising, falling) tuples of (term, change_rate)
    """
    rising = []
    falling = []

    all_terms = set(prev_counts.keys()) | set(curr_counts.keys())

    for term in all_terms:
        prev_freq = prev_counts.get(term, 0)
        curr_freq = curr_counts.get(term, 0)

        if prev_freq == 0 and curr_freq > 0:
            change_rate = float('inf')
        elif prev_freq == 0 and curr_freq == 0:
            continue
        else:
            change_rate = (curr_freq - prev_freq) / prev_freq

        if change_rate >= threshold:
            rising.append((term, change_rate))
        elif change_rate <= -threshold:
            falling.append((term, change_rate))

    rising.sort(key=lambda x: x[1], reverse=True)
    falling.sort(key=lambda x: x[1])

    return rising, falling

if __name__ == '__main__':
    prev = {'AI': 45, 'LLM': 32, 'benchmark': 28, 'chip': 15}
    curr = {'AI': 52, 'LLM': 38, 'chip': 42, 'quantum': 20}

    rising, falling = compute_momentum(prev, curr)

    print('Rising topics:')
    for term, rate in rising:
        print(f'  {term}: +{rate:.1%}')

    print('Falling topics:')
    for term, rate in falling:
        print(f'  {term}: {rate:.1%}')
