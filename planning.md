# Project 3: Navigating the Sea

## Problem Formulation

In the Navigating the Sea problem, we want to find the path an autonomous submersible should take through a newly discovered ocean trench so that the total biomass density score it accumulates is as large as possible. The trench is an $n \times m$ grid with $n$ vertical depth zones (rows) and $m$ horizontal coordinates (columns), where $n, m \ge 1$ and we number both from 1. Every coordinate $(i, j)$ has a surveyed biomass density score $B(i, j)$. A positive score means rich coral, a negative score means a hazardous hydrothermal vent that damages the sensors, and a score can also be zero. The submersible can start at any coordinate on the surface (row 1) and has to reach the ocean floor (row $n$), but it can finish at any coordinate there. To save battery, it only ever moves downward. From $(i, j)$ it can go to $(i+1, j-1)$ (down-left), $(i+1, j)$ (straight down), or $(i+1, j+1)$ (down-right), and it is not allowed to leave the grid.

More formally, for $1 \le r \le n$, a valid path to row $r$ is a sequence of coordinates $(1, c_1), (2, c_2), \dots, (r, c_r)$ with one coordinate per row, where $1 \le c_i \le m$ for every $i$ and $|c_{i+1} - c_i| \le 1$ for $1 \le i \le r - 1$. We define its score as $\sum_{i=1}^{r} B(i, c_i)$. When $r = n$, we just call it a valid path. The input is the grid $B$, and the output is a valid path with the highest score along with that score. If more than one path has the highest score, returning any of them is fine. Our goal is an algorithm that finds an optimal path and still runs efficiently when the grid is very large.

## Baseline Solution

Our baseline is an exhaustive recursive search that tries every valid way to continue a given path. The recursive helper `FindBestPath` looks at the three moves from the current coordinate $(i, j)$, which are $(i+1, j-1)$, $(i+1, j)$, and $(i+1, j+1)$, and skips any that fall outside the grid. Each recursive branch gets its own copy of the path, so branches never change each other's paths. Once the recursion reaches the last row, it returns the finished path. The caller then adds up the score of each path it got back and keeps the one with the highest total. Since the destinations are checked from left to right and the best option is only replaced when a strictly higher total shows up, the first option wins when there is a tie.

The main algorithm, `SubmersiblePathBaseline`, goes through every surface column from left to right. For each column $j$, it calls `FindBestPath(chart, 1, j, [(1, j)])`, which means the starting coordinate is part of both the path and its score. It adds up the total score of each path that comes back and keeps the best path and score over all starting columns, again keeping the first one if there is a tie. We start the best score at negative infinity so that paths with negative totals are still considered. At the end, it returns the maximum score together with a path that reaches it.

As an example, take this $3 \times 3$ grid:

```math
B = \begin{bmatrix} 1 & 3 & 0 \\ 4 & -6 & -2 \\ 2 & 1 & 9 \end{bmatrix}
```

This grid has 17 valid paths: 5 that start at $(1,1)$, 7 that start at $(1,2)$, and 5 that start at $(1,3)$. The only optimal one is $(1,2) \to (2,3) \to (3,3)$, which scores $3 + (-2) + 9 = 10$ even though it goes through the vent at $(2,3)$. If the submersible always moved to the next coordinate with the highest score, it would only get 7, 9, and 7 from the three starting columns. So we cannot pick the next move just by looking one row ahead.

The problem with this approach is how many paths there are. When $m \ge 2$, every coordinate above the floor has two or three possible moves, so the number of valid paths is between $m \cdot 2^{n-1}$ and $m \cdot 3^{n-1}$. That is 136,946 paths for a $10 \times 10$ grid and about $1.8 \times 10^{10}$ for a $20 \times 20$ grid.

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

Suppose `visitedPath` is a valid path from row 1 to `(row, column)` that includes both its starting coordinate and its current coordinate. We use induction on the number of rows remaining to show that `FindBestPath(chart, row, column, visitedPath)` returns the completed path with the highest total score out of all valid extensions of this fixed path. If the next row is outside the chart, the current path has already reached the last row and is its own only completed extension, so returning `visitedPath` is correct.

If not, the algorithm considers each legal next column: `column - 1`, `column`, and `column + 1`. For each legal move, it copies `visitedPath` and adds the destination to the end, so the path condition still holds for the recursive call. Each of these calls has one fewer row left, so by the induction hypothesis it returns the best completed extension of the new path. This means the `options` list holds the best completed path for every possible next move.

The last loop adds up the total score of each option and keeps the one with the highest total. Any completed extension of `visitedPath` has to start with one of the legal next moves, so the `bestOption` that gets returned has the highest score among all of these extensions.

For each surface column $j$, `SubmersiblePathBaseline` starts the path as `[(1, j)]`, which meets the helper's precondition. The helper then returns the best complete path that starts at $(1, j)$, with the starting coordinate included. Every valid path starts in one of these columns, so comparing all the returned paths gives the maximum score over the whole grid. Starting `bestScore` at negative infinity makes sure a path gets picked even if every total is negative, and only updating on a strictly higher score keeps an optimal path when there are ties. As a result, the algorithm returns an optimal path along with its total score.

## Algorithmic Strategy

We propose a dynamic programming algorithm. It is based on the fact that the best valid path ending at $(i, j)$ has to pass through column $j - 1$, $j$, or $j + 1$ in row $i - 1$, and the part of it up to row $i - 1$ must also be a best path to that coordinate. If it were not, we could swap in a better one and get a better path to $(i, j)$. So rather than checking every path like the baseline does, we compute for each coordinate the best score $D(i, j)$ of a valid path to row $i$ (as defined in the Problem Formulation) that ends at column $j$:

```math
D(1, j) = B(1, j), \qquad D(i, j) = B(i, j) + \max_{k} D(i-1, k) \text{ for } 2 \le i \le n
```

Here $k$ ranges over whichever of the columns $j - 1$, $j$, and $j + 1$ are inside the grid. We fill in the table one row at a time, starting from the surface and going down, so every value on the right-hand side is already known by the time we need it. Every valid path ends somewhere on the ocean floor, so the answer is $\max_j D(n, j)$. To get the path itself, we also store in $P(i, j)$ the column $k$ that gives the maximum (taking the leftmost one if there is a tie), and then follow these pointers from the best floor coordinate back up to the surface.

Each coordinate is computed only once from at most three values. The baseline, on the other hand, re-explores everything below a coordinate once for every partial path that reaches it. In the example, it makes 27 calls to `FindBestPath` across the three starting columns, even though the grid has only 9 coordinates. For the same example, the last row of $D$ is $9, 8, 10$, so the algorithm returns 10 and follows $P$ back to the same optimal path $(1,2) \to (2,3) \to (3,3)$.

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

The loop over `prev_col` computes exactly the recurrence above. It starts from $-\infty$, keeps the largest value of $B(i, j) + D(i - 1, k)$ over the columns $k$ inside the grid, and sets $P(i, j)$ to the $k$ that produced it, so $D(i, j) = B(i, j) + D(i - 1, P(i, j))$. There is always at least one such column, namely $k = j$.

We prove by induction on $i$ that $D(i, j)$ is the maximum score of a valid path to row $i$ ending at column $j$, and that following $P$ back from $(i, j)$ gives a path with that score. For $i = 1$, the only such path is $(1, j)$ itself, and its score is $B(1, j)$. Now let $i \ge 2$ and assume the claim holds for row $i - 1$. Any valid path to $(i, j)$ goes through some column $k$ in row $i - 1$, where $k \in \lbrace j - 1, j, j + 1 \rbrace$ is inside the grid. By the induction hypothesis, its part up to row $i - 1$ scores at most $D(i - 1, k)$, so its total is at most $B(i, j) + \max_k D(i - 1, k) = D(i, j)$. In the other direction, the induction hypothesis tells us that following $P$ back from $(i - 1, P(i, j))$ gives a path with score $D(i - 1, P(i, j))$. Adding $(i, j)$ to the end of it gives a valid path to $(i, j)$ with score $B(i, j) + D(i - 1, P(i, j)) = D(i, j)$.

Since every valid path ends at some coordinate $(n, j)$ on the ocean floor, the maximum total score is $\max_j D(n, j)$, which is `best_score`. Following $P$ back from `best_col` gives `best_path`, a valid path with that score. So the algorithm always returns an optimal path.

## Complexity Analysis

Our dynamic programming algorithm avoids the repeated work the baseline does by computing the best score for each coordinate only once. We analyze both algorithms in terms of $n$ rows and $m$ columns, where $n, m \ge 1$, and we do not assume the grid is square. We also assume that reading a grid entry and adding or comparing scores take constant time.

For the baseline, `SubmersiblePathBaseline` calls `FindBestPath` once for each of the $m$ starting columns. A complete path makes $n-1$ downward moves with at most three choices at each step, so one recursion tree has at most $1 + 3 + \cdots + 3^{n-1} = O(3^{n-1})$ calls. Moves outside the grid are skipped, but different partial paths that reach the same coordinate still lead to separate recursive calls.

We also need to count the work done inside each call. A nonterminal call copies the current path for at most three legal moves, and each copy has at most $n$ coordinates. After the recursive calls return, it adds up the scores of at most three completed paths with $n$ coordinates each. So each call does at most $O(n)$ work, not counting its recursive calls. Over all $m$ starting columns, this comes to $O(nm3^{n-1})$ time. The outer algorithm also adds up the score of each returned path, which takes another $O(nm)$ time.

This gives a simple worst-case upper bound of $T_{\text{baseline}}(n,m) = O(nm3^{n-1} + nm) = O(nm3^{n-1})$ on the baseline's total running time. It is an upper bound and not an exact count, because coordinates near the edges of the grid have fewer than three successors. Still, when $m \ge 2$, every coordinate above the floor has at least two legal successors, so the exhaustive search grows exponentially with the number of rows. When $m=1$ there is only one possible path, but the pseudocode as written still takes $O(n^2)$ time because it keeps copying partial paths and recomputing the score of the completed path. When $n=1$, comparing the $m$ single-coordinate paths takes $O(m)$ time.

For the dynamic programming algorithm, filling in the first row of $D$ takes $O(m)$ time. Each of the other $(n-1)m$ coordinates looks at no more than three predecessor coordinates and records the best score and its predecessor in constant time, so computing the whole table takes $O(nm)$ time. After that, finding the best coordinate in the last row takes $O(m)$ time, and following the predecessor pointers to build the path and then reversing it each take $O(n)$ time.

Adding these up, the total running time is $T_{\text{DP}}(n,m) = O(m + nm + m + n) = O(nm + m + n)$. Because $n, m \ge 1$, both $n$ and $m$ are at most $nm$, which simplifies the bound to $O(nm)$. The algorithm fills in every one of the $nm$ entries of $D$ no matter what the scores are, so its running time is also $\Omega(nm)$ and therefore $\Theta(nm)$. In other words, the running time is linear in the number of grid coordinates, which makes this algorithm far more practical than exhaustive search for grids with many rows and more than one column.

The two algorithms also differ in how much space they need. Not counting the input grid, the baseline uses $O(n^2)$ extra space. Its recursion depth is $O(n)$, and each active call can hold onto a partial path plus at most three completed candidate paths, each with at most $n$ coordinates. It is these stored paths, and not just the recursion stack, that make the space quadratic. The starting columns are handled one after another, so their memory use is not multiplied by $m$.

The dynamic programming algorithm keeps two $n \times m$ tables, $D$ and $P$, which take $O(nm)$ space. The returned path takes another $O(n)$, so the extra space is $O(nm+n) = O(nm)$ overall. For both algorithms, the input grid itself takes $O(nm)$ storage, and we leave it out of these extra-space bounds.
