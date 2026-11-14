# Project 3: Navigating the Sea

## Problem Formulation

The objective of the Navigating the Sea problem is to find a path for an autonomous submersible through a newly discovered ocean trench that maximizes the total accumulated biomass density score. The trench is represented by an $n \times m$ grid of $n$ vertical depth zones (rows) and $m$ horizontal coordinates (columns), where $n, m \ge 1$ and both are numbered from 1. Each coordinate $(i, j)$ has a surveyed biomass density score $B(i, j)$, which can be positive (rich coral), negative (hazardous hydrothermal vents that damage sensors), or zero. The submersible starts at any coordinate on the surface (row 1) and must reach the ocean floor (row $n$), where it may end at any coordinate. To conserve battery, it can only move downward: from $(i, j)$, it can move only to $(i+1, j-1)$ (down-left), $(i+1, j)$ (straight down), or $(i+1, j+1)$ (down-right), and it cannot leave the grid.

Formally, for $1 \le r \le n$, a valid path to row $r$ is a sequence of coordinates $(1, c_1), (2, c_2), \dots, (r, c_r)$, one for each row, where $1 \le c_i \le m$ for every $i$ and $|c_{i+1} - c_i| \le 1$ for $1 \le i \le r - 1$. Its score is $\sum_{i=1}^{r} B(i, c_i)$. A valid path to row $n$ is simply called a valid path. The input is the grid $B$, and the output is a valid path with the maximum score, together with that score. If several paths tie, any one of them may be returned. Our goal is to design an algorithm that finds an optimal path and scales efficiently even when the grid is very large.

## Baseline Solution

Our baseline is an exhaustive recursive search that checks every valid continuation of a supplied path. The recursive helper `FindBestPath` tries the moves from its current coordinate $(i, j)$ to $(i+1, j-1)$, $(i+1, j)$, and $(i+1, j+1)$, skipping destinations outside the grid. Each recursive branch receives a new copy of the path, so paths from different branches do not modify one another. When the recursion reaches the final row, it returns the completed path. The caller then calculates the total score of every returned option and keeps the option with the highest total. If several options tie, the first one is kept because destinations are examined from left to right and the algorithm replaces the best option only when it finds a strictly higher total.

The main algorithm, `SubmersiblePathBaseline`, tries every surface column from left to right. For each column $j$, it calls `FindBestPath(chart, 1, j, [(1, j)])`, so the starting coordinate is included in the path and its score. It calculates the total score of each returned path and keeps the best path and score across all starting columns, again retaining the first path when scores tie. The best score is initialized to negative infinity so that paths with negative totals are also considered. Finally, it returns both the maximum score and a path that achieves it.

For example, consider the following $3 \times 3$ grid:

```math
B = \begin{bmatrix} 1 & 3 & 0 \\ 4 & -6 & -2 \\ 2 & 1 & 9 \end{bmatrix}
```

It has 17 valid paths: 5 starting from $(1,1)$, 7 from $(1,2)$, and 5 from $(1,3)$. The only optimal path is $(1,2) \to (2,3) \to (3,3)$, with a score of $3 + (-2) + 9 = 10$, and it passes through the vent at $(2,3)$. Always moving to the highest-scoring next coordinate scores only 7, 9, and 7 from the three starting columns, so the next move cannot be chosen by looking only one row ahead.

The drawback is the number of paths. When $m \ge 2$, every coordinate above the floor has two or three moves, so there are between $m \cdot 2^{n-1}$ and $m \cdot 3^{n-1}$ valid paths: 136,946 for a $10 \times 10$ grid and about $1.8 \times 10^{10}$ for a $20 \times 20$ grid.

### Pseudocode

```text
ALGORITHM SubmersiblePathBaseline(chart)

    Input:
        chart: An n x m grid of biomass density scores, with n, m >= 1
               and rows and columns both numbered from 1

    Output:
        The maximum total biomass density score and a path that achieves it

    m ← number of columns in chart
    bestScore ← negative infinity
    bestPath ← nothing

    FOR startColumn from 1 to m:

        candidatePath ← FindBestPath(chart, 1, startColumn, [(1, startColumn)])
        total ← 0

        FOR each (pathRow, pathColumn) in candidatePath:
            total ← total + chart[pathRow][pathColumn]

        IF total is greater than bestScore:
            bestScore ← total
            bestPath ← candidatePath

    RETURN bestScore, bestPath


FUNCTION FindBestPath(chart, row, column, visitedPath)

    // visitedPath is a valid path from row 1 to (row, column),
    // including both its starting coordinate and its current coordinate

    nextRow ← row + 1
    destinations ← empty list
    highestTotal ← negative infinity
    bestOption ← nothing

    IF nextRow is outside the chart:
        RETURN visitedPath

    options ← empty list

    FOR each possibleColumn in:
        column - 1
        column
        column + 1

        IF possibleColumn is inside the chart:

            destination ← (nextRow, possibleColumn)
            add destination to destinations

            newPath ← copy of visitedPath
            add destination to newPath

            option ← FindBestPath(
                chart,
                nextRow,
                possibleColumn,
                newPath
            )

            add option to options

    FOR each option in options:

        total ← 0

        FOR each (optionRow, optionColumn) in option:
            total ← total + chart[optionRow][optionColumn]

        IF total is greater than highestTotal:
            highestTotal ← total
            bestOption ← option

    RETURN bestOption
```

### Correctness

Assume that `visitedPath` is a valid path from row 1 to `(row, column)`, including both its starting coordinate and its current coordinate. We show by induction on the number of rows remaining that `FindBestPath(chart, row, column, visitedPath)` returns a completed path of maximum total score among all valid extensions of this fixed path. If the next row is outside the chart, the current path already reaches the final row and is its only completed extension, so returning `visitedPath` is correct.

Otherwise, the algorithm considers each legal next column: `column - 1`, `column`, and `column + 1`. For every legal move, it copies `visitedPath` and appends the destination, preserving the required path condition for the recursive call. Each call has one fewer row remaining, so by the induction hypothesis it returns the best completed extension of that new path. Therefore, the `options` list contains the best completed path for every possible next move.

The final loop calculates the total score of each option and keeps the option with the greatest total. Every completed extension of `visitedPath` must take one of the legal next moves, so the returned `bestOption` has the maximum score among all such extensions.

For every surface column $j$, `SubmersiblePathBaseline` initializes the path to `[(1, j)]`, which satisfies the helper's precondition. The helper therefore returns the best complete path starting at $(1, j)$, including the starting coordinate. Every valid path starts in one of these columns, so comparing all returned paths produces the maximum score over the full grid. Initializing `bestScore` to negative infinity ensures that a path is selected even when all totals are negative, and updating only for a strictly higher score retains an optimal path when scores tie. Thus, the algorithm returns both an optimal path and its total score.

## Algorithmic Strategy

We propose a dynamic programming algorithm. The key observation is that the best valid path ending at $(i, j)$ must pass through column $j - 1$, $j$, or $j + 1$ in row $i - 1$, and its part up to row $i - 1$ must itself be a best path to that coordinate, since otherwise replacing it with a better one would give a better path to $(i, j)$. So instead of checking every path like the baseline, we compute, for every coordinate, the best score $D(i, j)$ of a valid path to row $i$ (as defined in the Problem Formulation) that ends at column $j$:

```math
D(1, j) = B(1, j), \qquad D(i, j) = B(i, j) + \max_{k} D(i-1, k) \text{ for } 2 \le i \le n
```

where $k$ ranges over the columns $j - 1$, $j$, and $j + 1$ that lie inside the grid. The table is filled one row at a time from the surface down, so every value on the right-hand side is already known when it is needed. Every valid path ends somewhere on the ocean floor, so the answer is $\max_j D(n, j)$. To return the path itself, we also record in $P(i, j)$ the column $k$ that gives the maximum, choosing the leftmost one when there is a tie, and follow these pointers from the best floor coordinate back to the surface.

Each coordinate is computed once from at most three values, while the baseline re-explores everything below a coordinate once for every partial path that reaches it (27 calls to `FindBestPath` across all three starting columns, even though the example has only 9 coordinates). On that example, the last row of $D$ is $9, 8, 10$, so the algorithm returns 10 and follows $P$ back to the same optimal path $(1,2) \to (2,3) \to (3,3)$.

### Pseudocode

```text
Algorithm SubmersiblePathDP(B):

    Input:
        B: An n x m grid of biomass density scores, where B[i][j] is the
           score at row i and column j (both numbered from 1)

    Output:
        The maximum total biomass density score and a path that achieves it

    n = number of rows in B
    m = number of columns in B

    // D[i][j] is the best score of a valid path from row 1 to (i, j), and
    // P[i][j] is the column in row i - 1 that this best path comes from
    D = n x m table
    P = n x m table

    for j from 1 to m:
        D[1][j] = B[1][j]

    for i from 2 to n:
        for j from 1 to m:
            D[i][j] = -infinity
            for prev_col in [j - 1, j, j + 1]:
                if 1 <= prev_col <= m:
                    if B[i][j] + D[i - 1][prev_col] > D[i][j]:
                        D[i][j] = B[i][j] + D[i - 1][prev_col]
                        P[i][j] = prev_col

    // Choose the best coordinate on the ocean floor
    best_score = -infinity
    for j from 1 to m:
        if D[n][j] > best_score:
            best_score = D[n][j]
            best_col = j

    // Follow P from the floor back to the surface
    best_path = [(n, best_col)]
    col = best_col
    for i from n down to 2:
        col = P[i][col]
        append (i - 1, col) to best_path
    reverse best_path

    return best_score, best_path
```

### Correctness and Optimality

The loop over `prev_col` computes exactly the recurrence above: it starts from $-\infty$, keeps the largest value of $B(i, j) + D(i - 1, k)$ over the columns $k$ inside the grid, and sets $P(i, j)$ to the $k$ that gives it, so $D(i, j) = B(i, j) + D(i - 1, P(i, j))$. At least one such column ($k = j$) always exists.

We show by induction on $i$ that $D(i, j)$ is the maximum score of a valid path to row $i$ that ends at column $j$, and that following $P$ back from $(i, j)$ gives a path with that score. For $i = 1$, the only such path is $(1, j)$ itself, with score $B(1, j)$. Now let $i \ge 2$ and assume the claim for row $i - 1$. Any valid path to $(i, j)$ passes through some column $k$ in row $i - 1$ with $k \in \lbrace j - 1, j, j + 1 \rbrace$ inside the grid, and its part up to row $i - 1$ scores at most $D(i - 1, k)$ by the induction hypothesis, so its total is at most $B(i, j) + \max_k D(i - 1, k) = D(i, j)$. Conversely, following $P$ back from $(i - 1, P(i, j))$ gives a path with score $D(i - 1, P(i, j))$ by the induction hypothesis, and adding $(i, j)$ to it gives a valid path to $(i, j)$ with score $B(i, j) + D(i - 1, P(i, j)) = D(i, j)$.

Every valid path ends at some coordinate $(n, j)$ on the ocean floor, so the maximum total score is $\max_j D(n, j)$, which is `best_score`. Following $P$ back from `best_col` gives `best_path`, a valid path that achieves it. Therefore, the algorithm always returns an optimal path.

## Complexity Analysis

Our Dynamic programming algortithm increases our running time significantly compared to our baseline. Our baseline  algorithm uses a recursive search with a worst case time of O(3^n). This is because it explores each coordinate. Our dynamic strategy is much more efficient before checks each coordinate in the m x n grid once. It examines at most three possible predecessor coordinates to determine the maxium score. Each coordinate requires a constant amount off work and therefore reduces the wrst case running time for this algorrithm. Making it O(mn). This makes this algorithm more suitable for larger grids.
