# methods.py
# Implements solutions for the Navigating the Sea problem.
#
# Rows and columns are numbered from 0 here (planning.md numbers them from 1),
# so every coordinate in a returned path can index the chart directly.


def _validate_chart(chart: list) -> None:
    """
    Check that the chart is a non-empty rectangular grid.

    Both algorithms assume n, m >= 1 and that every row has the same number
    of columns, as stated in the Problem Formulation of planning.md.

    Args:
        chart (list): The grid of biomass density scores to check.

    Raises:
        ValueError: If the chart has no rows, its first row has no columns,
            or its rows have different lengths.
    """

    if len(chart) == 0 or len(chart[0]) == 0:
        raise ValueError("chart must have at least one row and one column")

    m = len(chart[0])

    for row in chart:
        if len(row) != m:
            raise ValueError("every row of chart must have the same length")


def SubmersiblePathBaseline(chart: list) -> tuple:
    """
    Find a path with the maximum total biomass density score by exhaustive
    search.

    The submersible starts at any column of the surface (row 0) and moves one
    row down at a time, to the down-left, straight down, or down-right
    coordinate, without leaving the grid, until it reaches the ocean floor
    (row n - 1). This function tries every surface column from left to right
    and uses FindBestPath to search every valid path that starts there.

    When several paths tie for the maximum score, the path found first is
    kept, which is the leftmost choice at every step.

    For an n x m chart, the running time is O(n * m * 3^(n-1)) and the extra
    space is O(n^2), as derived in the Complexity Analysis of planning.md.

    Args:
        chart (list): An n x m grid (a list of n rows, each a list of m
            scores) of biomass density scores, where n, m >= 1.

    Returns:
        tuple: (best_score, best_path), where best_score is the maximum total
            score and best_path is a list of n (row, column) tuples, one per
            row, that achieves it.

    Raises:
        ValueError: If the chart is empty or its rows have different lengths.
    """

    _validate_chart(chart)

    m = len(chart[0])

    # Starting below every possible total lets a path be chosen even when
    # every path has a negative score
    best_score = float("-inf")
    best_path = None

    for start_column in range(m):
        # The starting coordinate is part of the path, so it counts toward
        # the score
        candidate_path = FindBestPath(chart, 0, start_column, [(0, start_column)])

        total = 0
        for path_row, path_column in candidate_path:
            total += chart[path_row][path_column]

        # Strictly greater keeps the leftmost starting column on ties
        if total > best_score:
            best_score = total
            best_path = candidate_path

    return best_score, best_path


def FindBestPath(chart: list, row: int, column: int, visited_path: list) -> list:
    """
    Find the completed path with the highest total score that extends
    visited_path.

    visited_path must be a valid path from row 0 to (row, column), including
    both its starting coordinate and (row, column) itself. The function tries
    every legal move to the next row, recursively finds the best completion
    of each move, and keeps the completion with the highest total score.
    Moves are tried from left to right and only a strictly higher total
    replaces the current best, so the leftmost move wins on ties.

    Args:
        chart (list): The n x m grid of biomass density scores.
        row (int): The row of the current coordinate.
        column (int): The column of the current coordinate.
        visited_path (list): The (row, column) tuples of the path so far,
            ending at (row, column).

    Returns:
        list: A path of n (row, column) tuples from row 0 to row n - 1 with
            the highest total score among all completions of visited_path.
    """

    n = len(chart)
    m = len(chart[0])

    next_row = row + 1
    highest_total = float("-inf")
    best_option = None

    # The path already reaches the ocean floor, so it is its only completion
    if next_row >= n:
        return visited_path

    options = []

    for possible_column in (column - 1, column, column + 1):
        if 0 <= possible_column < m:
            destination = (next_row, possible_column)

            # Each branch extends its own copy so that branches never change
            # each other's paths
            new_path = visited_path.copy()
            new_path.append(destination)

            option = FindBestPath(chart, next_row, possible_column, new_path)
            options.append(option)

    for option in options:
        total = 0
        for option_row, option_column in option:
            total += chart[option_row][option_column]

        if total > highest_total:
            highest_total = total
            best_option = option

    return best_option
