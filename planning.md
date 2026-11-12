***Project 3: Navigating the Sea***

**Problem Formulation**  
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. 


Inputs: Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). 


Output: Determine the path that maximizes the total accumulated biomass density score.


Constraints: To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. 

**Baseline Solution:**

Our baseline is an exhaustive brute-force search that checks every valid path, so it always finds a best one, although it is too slow for large grids. The grid has $n$ rows and $m$ columns, both numbered from 1. A valid path is a sequence of coordinates $(1, c_1), (2, c_2), \dots, (n, c_n)$, one for each row, where every $c_i$ satisfies $1 \le c_i \le m$ and consecutive columns satisfy $|c_{i+1} - c_i| \le 1$. Its score is $\sum_{i=1}^{n} B(i, c_i)$.

The algorithm tries each surface coordinate $(1, j)$ as a starting point. From $(i, j)$, it recursively tries the moves to $(i+1, j-1)$, $(i+1, j)$, and $(i+1, j+1)$, skipping down-left when $j = 1$ and down-right when $j = m$. When the recursion reaches row $n$, it compares the score of the finished path with the best score so far and, if it is higher, records the score and the path. Because one shared list holds the current path, the path is copied when recorded. The search never stops early on a negative running total, because a hydrothermal vent may lead to rich coral further down. If several paths tie, it returns the one whose column sequence comes first in lexicographic order, since it tries moves from left to right and only replaces the best path on a strictly higher score.

For example, consider the following $3 \times 3$ grid:

```math
B = \begin{bmatrix} 1 & 3 & 0 \\ 4 & -6 & -2 \\ 2 & 1 & 9 \end{bmatrix}
```

It has 17 valid paths: 5 starting from $(1,1)$, 7 from $(1,2)$, and 5 from $(1,3)$. The only optimal path is $(1,2) \to (2,3) \to (3,3)$, with a score of $3 + (-2) + 9 = 10$, and it passes through the vent at $(2,3)$. Always moving to the highest-scoring next coordinate scores only 7, 9, and 7 from the three starting columns, so the next move cannot be chosen by looking only one row ahead.

The drawback is the number of paths. When $m \ge 2$, every coordinate above the floor has two or three moves, so there are between $m \cdot 2^{n-1}$ and $m \cdot 3^{n-1}$ valid paths: 136,946 for a $10 \times 10$ grid and about $1.8 \times 10^{10}$ for a $20 \times 20$ grid.

**Baseline Pseudocode:**

```text
Algorithm SubmersiblePathBruteForce(B):

    Input:
        B: An n x m grid of biomass density scores, where B[i][j] is the
           score at row i and column j (both numbered from 1)

    Output:
        The maximum total biomass density score and a path that achieves it

    n = number of rows in B
    m = number of columns in B

    // B, n, m, best_score and best_path are shared by every call to Explore
    best_score = -infinity
    best_path = empty list

    for j from 1 to m:
        Explore(1, j, B[1][j], [(1, j)])

    return best_score, best_path


Function Explore(i, j, score, path):

    // path is a valid path from row 1 to row i ending at column j,
    // and score is its total
    if i == n:
        if score > best_score:
            best_score = score
            best_path = copy of path
        return

    for next_col in [j - 1, j, j + 1]:
        if 1 <= next_col <= m:
            append (i + 1, next_col) to path
            Explore(i + 1, next_col, score + B[i + 1][next_col], path)
            remove the last element from path
```

**Baseline Correctness:**

Every call `Explore(i, j, score, path)` is made with `path` holding a valid path from row 1 to row $i$ that ends at column $j$, and with `score` equal to its total. This holds for the calls from the outer loop, where `path` is $[(1, j)]$ and `score` is $B(1, j)$, and each recursive call extends `path` by one downward move inside the grid and adds that coordinate's score. Every call also returns with `path` unchanged: a call at row $n$ does not modify it, and every other call removes each coordinate it appends once the recursive call on it returns, which by induction on $n - i$ has left `path` as it found it. Since $i$ grows by one with each call, the recursion always stops at row $n$.

Conversely, every valid path $(1, c_1), \dots, (n, c_n)$ is reached by exactly one call at row $n$: the outer loop picks $c_1$ once, and at each row the loop over `next_col` picks $c_{i+1}$ exactly once, because $c_{i+1}$ is one of the three candidates, it passes the bounds test since the path is valid, and the candidates are different. So the calls at row $n$ correspond exactly to the valid paths, each with its correct score. At least one valid path always exists (straight down), and the algorithm keeps the highest score among these calls, so it returns the maximum total biomass density score and a path that achieves it.

**Algorithmic Strategy:**

We propose a dynamic programming algorithm. The key observation is that the best valid path ending at $(i, j)$ must pass through column $j - 1$, $j$, or $j + 1$ in row $i - 1$, and its part up to row $i - 1$ must itself be a best path to that coordinate, since otherwise replacing it with a better one would give a better path to $(i, j)$. So instead of checking every path like the baseline, we compute, for every coordinate, the best score $D(i, j)$ of a valid path (as defined in the Baseline Solution) that starts anywhere on the surface and ends at $(i, j)$:

```math
D(1, j) = B(1, j), \qquad D(i, j) = B(i, j) + \max_{k} D(i-1, k) \text{ for } 2 \le i \le n
```

where $k$ ranges over the columns $j - 1$, $j$, and $j + 1$ that lie inside the grid. The table is filled one row at a time from the surface down, so every value on the right-hand side is already known when it is needed. Every valid path ends somewhere on the ocean floor, so the answer is $\max_j D(n, j)$. To return the path itself, we also record in $P(i, j)$ the column $k$ that gives the maximum, choosing the leftmost one when there is a tie, and follow these pointers from the best floor coordinate back to the surface. Each coordinate is computed once from at most three values, while the baseline recomputes the same partial paths many times (its example has 17 paths but only 9 coordinates). On that example, the last row of $D$ is $9, 8, 10$, so the algorithm returns 10 and follows $P$ back to the same optimal path $(1,2) \to (2,3) \to (3,3)$, even though it passes through the vent at $(2,3)$.

**Strategy Pseudocode:**

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

**Strategy Correctness:**

The loop over `prev_col` computes exactly the recurrence above: it starts from $-\infty$ and keeps the largest value of $B(i, j) + D(i - 1, k)$ over the columns $k$ inside the grid, and at least one such column ($k = j$) always exists. We show by induction on $i$ that $D(i, j)$ is the maximum score of a valid path from row 1 to $(i, j)$, and that following $P$ back from $(i, j)$ gives a path with that score. For $i = 1$, the only such path is $(1, j)$ itself, with score $B(1, j)$. Now let $i \ge 2$ and assume the claim for row $i - 1$. Any valid path to $(i, j)$ passes through some column $k$ in row $i - 1$ with $k \in \{j - 1, j, j + 1\}$ inside the grid, and its part up to row $i - 1$ scores at most $D(i - 1, k)$ by the induction hypothesis, so its total is at most $B(i, j) + \max_k D(i - 1, k) = D(i, j)$. Conversely, following $P$ back from $(i - 1, P(i, j))$ gives a path with score $D(i - 1, P(i, j))$ by the induction hypothesis, and adding $(i, j)$ to it gives a valid path to $(i, j)$ with score exactly $D(i, j)$.

Every valid path ends at some coordinate $(n, j)$ on the ocean floor, so the maximum total score is $\max_j D(n, j)$, which is `best_score`. Following $P$ back from `best_col` gives `best_path`, a valid path that achieves it. Therefore, the algorithm always returns an optimal path.

**Complexity Analysis:**