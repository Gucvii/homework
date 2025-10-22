from __future__ import annotations

import time
from pathlib import Path
from typing import List, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from arithmetic import generate_unique_expressions


def benchmark(ns: List[int], r: int = 10) -> List[Tuple[int, float]]:
    results: List[Tuple[int, float]] = []
    for n in ns:
        t0 = time.time()
        _ = generate_unique_expressions(n=n, r=r, max_ops=3)
        t1 = time.time()
        results.append((n, t1 - t0))
    return results


def save_chart(results: List[Tuple[int, float]], out_path: str) -> None:
    xs = [n for n, _ in results]
    ys = [t for _, t in results]
    plt.figure(figsize=(6, 4))
    plt.plot(xs, ys, marker='o')
    plt.title('Performance: n vs time')
    plt.xlabel('n (number of expressions)')
    plt.ylabel('time (s)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path)


if __name__ == '__main__':
    ns = [10, 100, 500, 1000]
    results = benchmark(ns, r=10)
    out = Path.cwd() / 'performance.png'
    save_chart(results, str(out))
    print(f'saved chart to {out}')