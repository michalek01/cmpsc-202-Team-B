# benchmark.py
# Empirically measures the running time of the Navigating the Sea algorithms
# as the chart grows, and saves every measurement to assets/empirical_results.csv.
#
# Run from the src folder with: python3 benchmark.py

import csv
import platform
import random
import statistics
from pathlib import Path
from time import perf_counter

from methods import SubmersiblePathBaseline, SubmersiblePathDP

SEED = 42
TRIALS = 5

# Scores cover both coral (positive) and vents (negative). Neither algorithm's
# running time depends on the scores themselves: the baseline always explores
# every valid path and the DP always fills every coordinate, so only the chart
# dimensions affect the measurements.
SCORE_LOW = -100
SCORE_HIGH = 100

# Experiment 1 compares both algorithms on small square charts. Each extra row
# makes the baseline about 3.5 times slower at this size, and it already takes
# about 3 seconds at n = 13, so n = 14 would take about 11 seconds per trial
# and n = 20 several hours.
COMPARISON_SIZES = list(range(2, 14))

# Experiment 2 measures only the DP, on charts from 10,000 to 4,000,000
# coordinates, far beyond what the baseline can handle.
SCALABILITY_SIZES = [100, 250, 500, 1000, 1500, 2000]

EXPERIMENTS = [
    (
        "Comparison",
        [("Baseline", SubmersiblePathBaseline), ("DP", SubmersiblePathDP)],
        COMPARISON_SIZES
    ),
    (
        "Scalability",
        [("DP", SubmersiblePathDP)],
        SCALABILITY_SIZES
    ),
]

# Generated files (the CSV and the plots) are stored in the assets folder at
# the root of the repository, next to src.
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CSV_PATH = ASSETS_DIR / "empirical_results.csv"
CSV_COLUMNS = ["Experiment", "Algorithm", "Rows", "Columns", "Cells", "Trial", "Time"]


def generate_chart(rng: random.Random, n: int, m: int) -> list:
    """
    Generate an n x m chart of random integer biomass density scores.

    Args:
        rng (random.Random): The random number generator to draw scores from.
        n (int): The number of rows.
        m (int): The number of columns.

    Returns:
        list: A list of n rows, each a list of m scores from SCORE_LOW to
            SCORE_HIGH inclusive.
    """

    return [[rng.randint(SCORE_LOW, SCORE_HIGH) for _ in range(m)] for _ in range(n)]


def time_algorithm(algorithm, chart: list) -> tuple:
    """
    Run an algorithm once on a chart and measure how long it takes.

    Only the algorithm call is timed, so generating the chart and recording
    the result do not count toward the measurement.

    Args:
        algorithm: SubmersiblePathBaseline or SubmersiblePathDP.
        chart (list): The chart to pass to the algorithm.

    Returns:
        tuple: (result, seconds), where result is the (best_score, best_path)
            returned by the algorithm and seconds is the elapsed time.
    """

    start = perf_counter()
    result = algorithm(chart)
    end = perf_counter()

    return result, end - start


def run_experiment(name: str, algorithms: list, sizes: list, rng: random.Random) -> list:
    """
    Time every algorithm on one square chart of each size.

    For each size n, a single n x n chart is generated and every algorithm
    runs TRIALS times on that same chart, so all algorithms are compared on
    identical input.

    Args:
        name (str): The experiment name to record in each row.
        algorithms (list): (label, function) pairs to time.
        sizes (list): The values of n to measure.
        rng (random.Random): The random number generator for the charts.

    Returns:
        list: One dict per trial with the keys in CSV_COLUMNS.

    Raises:
        RuntimeError: If the algorithms return different results on the same
            chart.
    """

    rows = []

    for n in sizes:
        chart = generate_chart(rng, n, n)
        results = {}

        for label, algorithm in algorithms:
            times = []

            for trial in range(1, TRIALS + 1):
                result, seconds = time_algorithm(algorithm, chart)
                times.append(seconds)
                rows.append({
                    "Experiment": name,
                    "Algorithm": label,
                    "Rows": n,
                    "Columns": n,
                    "Cells": n * n,
                    "Trial": trial,
                    "Time": seconds,
                })

            results[label] = result
            print(f"  {name:<12} n = m = {n:<5} {label:<9} "
                  f"median {statistics.median(times):.6f} s")

        # Both algorithms keep the leftmost optimal path on ties (see
        # tests.py), so the whole result must match, not only the score. This
        # confirms that the code being timed is also returning correct answers.
        expected = next(iter(results.values()))
        for label, result in results.items():
            if result != expected:
                raise RuntimeError(
                    f"{label} returned a different result on the {n} x {n} chart"
                )

    return rows


def write_csv(rows: list, path: Path) -> None:
    """
    Write the benchmark rows to a CSV file, creating its folder if needed.

    Args:
        rows (list): Dicts with the keys in CSV_COLUMNS.
        path (Path): Where to write the CSV file.
    """

    path.parent.mkdir(exist_ok=True)

    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows: list) -> None:
    """
    Print the median time of every algorithm at every size.

    When both algorithms ran on the same chart, the speedup of the DP over
    the baseline is printed as well.

    Args:
        rows (list): Dicts with the keys in CSV_COLUMNS.
    """

    times = {}
    for row in rows:
        key = (row["Experiment"], row["Rows"], row["Cells"])
        times.setdefault(key, {}).setdefault(row["Algorithm"], []).append(row["Time"])

    print()
    print(f"{'Experiment':<12} {'n = m':>6} {'Cells':>10} "
          f"{'Baseline (s)':>14} {'DP (s)':>12} {'Speedup':>10}")

    for (experiment, n, cells), by_algorithm in times.items():
        baseline = by_algorithm.get("Baseline")
        dp = statistics.median(by_algorithm["DP"])

        if baseline is None:
            baseline_text = "-"
            speedup_text = "-"
        else:
            baseline = statistics.median(baseline)
            baseline_text = f"{baseline:.6f}"
            speedup_text = f"{baseline / dp:,.1f}x"

        print(f"{experiment:<12} {n:>6} {cells:>10,} "
              f"{baseline_text:>14} {dp:>12.6f} {speedup_text:>10}")


def run_benchmarks() -> None:
    """Run both experiments, save the measurements, and print a summary."""

    print(f"Python {platform.python_version()} on {platform.platform()} "
          f"({platform.machine()})")
    print(f"Seed {SEED}, {TRIALS} trials per algorithm and size")
    print()

    rng = random.Random(SEED)
    rows = []

    for name, algorithms, sizes in EXPERIMENTS:
        rows.extend(run_experiment(name, algorithms, sizes, rng))

    write_csv(rows, CSV_PATH)
    print_summary(rows)

    print()
    print(f"Saved {len(rows)} measurements to {CSV_PATH}")


if __name__ == "__main__":
    run_benchmarks()
