# tests.py
# Unit tests verifying the correctness of the Navigating the Sea algorithms.
#
# Run from the src folder with: python3 -m unittest tests -v

import copy
import itertools
import random
import unittest
from unittest import mock

import methods
from methods import (
    FindBestPath,
    SubmersiblePathBaseline,
    SubmersiblePathDP
)

ALGORITHMS = [SubmersiblePathBaseline, SubmersiblePathDP]


def brute_force_reference(chart):
    """
    Find the optimal score and path by checking every column sequence.

    This follows the problem definition directly and shares no code with
    methods.py, so it can serve as an answer key on small charts.

    Taking the smaller column in every row of two optimal paths gives another
    optimal path, so there is exactly one optimal path that is leftmost in
    every row. Both algorithms return that path, and so does this function,
    because it visits sequences in lexicographic order and only replaces the
    best on a strictly higher score.
    """
    n = len(chart)
    m = len(chart[0])
    best_score = None
    best_path = None

    for columns in itertools.product(range(m), repeat=n):
        if all(abs(columns[i + 1] - columns[i]) <= 1 for i in range(n - 1)):
            score = sum(chart[i][c] for i, c in enumerate(columns))
            if best_score is None or score > best_score:
                best_score = score
                best_path = list(enumerate(columns))

    return best_score, best_path


def random_chart(rng, n, m, low, high):
    return [[rng.randint(low, high) for _ in range(m)] for _ in range(n)]


def chart_with_planted_path(rng, n, m):
    """
    Build a chart whose optimal path is known in advance.

    A random valid path gets 100 in every cell and all other cells get a
    score from -10 to 10. Any other path leaves the planted path in at least
    one row and loses at least 90 there, so the planted path is the only
    optimal path and its score is 100 * n.
    """
    chart = random_chart(rng, n, m, -10, 10)
    column = rng.randrange(m)
    path = []

    for i in range(n):
        if i > 0:
            column = min(m - 1, max(0, column + rng.choice((-1, 0, 1))))
        path.append((i, column))
        chart[i][column] = 100

    return chart, path


class PathTestCase(unittest.TestCase):
    def assertValidPath(self, chart, score, path):
        """Check that path is a valid path and that score is its total."""
        n = len(chart)
        m = len(chart[0])

        self.assertEqual(len(path), n)

        for i, (row, column) in enumerate(path):
            self.assertEqual(row, i)
            self.assertTrue(0 <= column < m)

        for i in range(n - 1):
            self.assertLessEqual(abs(path[i + 1][1] - path[i][1]), 1)

        # Since Python 3.12, sum() compensates for rounding error, so with
        # float scores it can differ in the last digit from the algorithms,
        # which add one coordinate at a time
        self.assertAlmostEqual(score, sum(chart[r][c] for r, c in path))


class TestHandWrittenCases(PathTestCase):
    # Format: (description, chart, expected_score, expected_path)
    CASES = [
        (
            "planning.md example, best path goes through a vent",
            [[1, 3, 0],
             [4, -6, -2],
             [2, 1, 9]],
            10, [(0, 1), (1, 2), (2, 2)]
        ),
        (
            "single coordinate",
            [[7]],
            7, [(0, 0)]
        ),
        (
            "single negative coordinate",
            [[-4]],
            -4, [(0, 0)]
        ),
        (
            "single row, tie goes to the leftmost column",
            [[-3, 7, 2, 7]],
            7, [(0, 1)]
        ),
        (
            "single column, only one path exists",
            [[2], [-4], [1], [5]],
            4, [(0, 0), (1, 0), (2, 0), (3, 0)]
        ),
        (
            "every score is negative",
            [[-5, -2, -9],
             [-7, -3, -4],
             [-1, -8, -6]],
            -6, [(0, 1), (1, 1), (2, 0)]
        ),
        (
            "every score is equal, so every path ties",
            [[2, 2, 2],
             [2, 2, 2],
             [2, 2, 2]],
            6, [(0, 0), (1, 0), (2, 0)]
        ),
        (
            "no wrap-around from the left edge (chart[1][-1] would give 20)",
            [[10, 0, 0],
             [0, 0, 10]],
            10, [(0, 0), (1, 0)]
        ),
        (
            "no wrap-around into the left edge (chart[0][-1] would give 20)",
            [[0, 0, 10],
             [10, 0, 0]],
            10, [(0, 0), (1, 0)]
        ),
        (
            "best path follows the right edge",
            [[0, 0, 5],
             [0, 0, 5],
             [0, 0, 5]],
            15, [(0, 2), (1, 2), (2, 2)]
        ),
        (
            "best path zigzags",
            [[0, 5, 0],
             [5, 0, 0],
             [0, 5, 0],
             [0, 0, 5]],
            20, [(0, 1), (1, 0), (2, 1), (3, 2)]
        ),
        (
            "wide chart (n < m) with several optimal paths",
            [[1, 2, 3, 4, 5],
             [5, 4, 3, 2, 1]],
            7, [(0, 1), (1, 0)]
        ),
        (
            "tall chart (n > m)",
            [[1, -1],
             [-1, 1],
             [1, -1],
             [-1, 1],
             [1, -1]],
            5, [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0)]
        ),
        (
            "starting at the best surface score is not optimal",
            [[5, 0, 0, 1],
             [0, 0, 0, 0],
             [0, 0, 0, 10]],
            11, [(0, 3), (1, 2), (2, 3)]
        ),
        (
            "float scores",
            [[1.5, 2.25],
             [0.5, -1.0]],
            2.75, [(0, 1), (1, 0)]
        ),
    ]

    def check_cases(self, algorithm):
        for description, chart, expected_score, expected_path in self.CASES:
            with self.subTest(case=description):
                score, path = algorithm(chart)
                self.assertEqual(score, expected_score)
                self.assertEqual(path, expected_path)
                self.assertValidPath(chart, score, path)

    def test_baseline_hand_written_cases(self):
        self.check_cases(SubmersiblePathBaseline)

    def test_dp_hand_written_cases(self):
        self.check_cases(SubmersiblePathDP)


class TestInputHandling(unittest.TestCase):
    def test_invalid_charts_raise_value_error(self):
        invalid_charts = [
            ("no rows", []),
            ("no columns", [[]]),
            ("rows of different lengths", [[1, 2], [3]]),
        ]

        for algorithm in ALGORITHMS:
            for description, chart in invalid_charts:
                with self.subTest(algorithm=algorithm.__name__, case=description):
                    with self.assertRaises(ValueError):
                        algorithm(chart)

    def test_chart_is_not_modified(self):
        # benchmark.py may pass the same chart to both algorithms and to
        # every trial, so neither algorithm may change it.
        chart = [[1, 3, 0],
                 [4, -6, -2],
                 [2, 1, 9]]
        original = copy.deepcopy(chart)

        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__):
                algorithm(chart)
                self.assertEqual(chart, original)


class TestRandomCharts(PathTestCase):
    def test_small_charts_match_reference(self):
        # Scores from -3 to 3 make ties common, so the paths returned on
        # ties are checked as well as the scores.
        rng = random.Random(202)

        for _ in range(500):
            n = rng.randint(1, 6)
            m = rng.randint(1, 6)
            chart = random_chart(rng, n, m, -3, 3)
            expected = brute_force_reference(chart)

            with self.subTest(chart=chart):
                self.assertEqual(SubmersiblePathBaseline(chart), expected)
                self.assertEqual(SubmersiblePathDP(chart), expected)

    def test_float_charts_baseline_matches_dp(self):
        rng = random.Random(203)

        for _ in range(200):
            n = rng.randint(1, 8)
            m = rng.randint(1, 8)
            chart = [[rng.uniform(-100, 100) for _ in range(m)] for _ in range(n)]

            with self.subTest(chart=chart):
                baseline_result = SubmersiblePathBaseline(chart)
                self.assertEqual(SubmersiblePathDP(chart), baseline_result)
                self.assertValidPath(chart, *baseline_result)

    def test_planted_path_is_found_by_both_algorithms(self):
        # These charts are larger than the reference can check quickly but
        # still small enough for the exponential baseline.
        rng = random.Random(204)

        for n, m in [(9, 9), (10, 4), (4, 10), (8, 1), (1, 8)]:
            chart, planted_path = chart_with_planted_path(rng, n, m)

            for algorithm in ALGORITHMS:
                with self.subTest(algorithm=algorithm.__name__, size=(n, m)):
                    self.assertEqual(algorithm(chart), (100 * n, planted_path))


class TestLargeChartsDP(PathTestCase):
    # The baseline takes exponential time, so only the DP runs at this scale.

    def test_planted_path_is_found(self):
        rng = random.Random(205)

        for n, m in [(500, 500), (1000, 30), (30, 1000)]:
            chart, planted_path = chart_with_planted_path(rng, n, m)

            with self.subTest(size=(n, m)):
                self.assertEqual(SubmersiblePathDP(chart), (100 * n, planted_path))

    def test_tall_single_column(self):
        rng = random.Random(206)
        chart = random_chart(rng, 5000, 1, -100, 100)

        score, path = SubmersiblePathDP(chart)

        self.assertEqual(score, sum(row[0] for row in chart))
        self.assertEqual(path, [(i, 0) for i in range(5000)])

    def test_equal_scores_take_leftmost_straight_path(self):
        chart = [[3] * 300 for _ in range(300)]

        score, path = SubmersiblePathDP(chart)

        self.assertEqual(score, 900)
        self.assertEqual(path, [(i, 0) for i in range(300)])

    def test_random_large_chart_returns_valid_path(self):
        rng = random.Random(207)
        chart = random_chart(rng, 400, 400, -100, 100)

        score, path = SubmersiblePathDP(chart)

        self.assertValidPath(chart, score, path)


class TestFindBestPath(unittest.TestCase):
    EXAMPLE = [[1, 3, 0],
               [4, -6, -2],
               [2, 1, 9]]

    def test_returns_visited_path_on_last_row(self):
        visited_path = [(0, 1), (1, 2), (2, 2)]

        result = FindBestPath(self.EXAMPLE, 2, 2, visited_path)

        self.assertEqual(result, visited_path)

    def test_extends_the_given_path(self):
        # From (1, 0) the only moves are to (2, 0), worth 2, and (2, 1),
        # worth 1, even though (2, 2) is worth 9.
        result = FindBestPath(self.EXAMPLE, 1, 0, [(0, 1), (1, 0)])

        self.assertEqual(result, [(0, 1), (1, 0), (2, 0)])

    def test_call_count_matches_planning(self):
        # planning.md states that the baseline makes 27 calls to
        # FindBestPath on its example. The recursive calls look the name up
        # in the methods module, so patching it there counts all of them.
        with mock.patch.object(methods, "FindBestPath",
                               wraps=methods.FindBestPath) as spy:
            SubmersiblePathBaseline(self.EXAMPLE)

        self.assertEqual(spy.call_count, 27)


if __name__ == "__main__":
    unittest.main()
