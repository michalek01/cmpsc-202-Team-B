***Project 3: Navigating the Sea***

**Problem Formulation**  
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. 


Inputs: Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). 


Output: Determine the path that maximizes the total accumulated biomass density score.


Constraints: To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. 

**Baseline Solution:**

Our baseline is an exhaustive brute-force search that checks every valid path, so it always finds a best one, although it is too slow for large grids. The grid has n rows and m columns, both numbered from 1. A valid path is a sequence of columns (c1, ..., cn), one for each row, where every ci is between 1 and m and consecutive columns differ by at most 1. Its score is B(1, c1) + ... + B(n, cn).

The algorithm tries each surface coordinate (1, j) as a starting point. From (i, j), it recursively tries the moves to (i+1, j-1), (i+1, j), and (i+1, j+1), skipping down-left when j = 1 and down-right when j = m. When the recursion reaches row n, it compares the score of the finished path with the best score so far and, if it is higher, records the score and a copy of the path. The current path is kept in one list: each coordinate is appended before a recursive call and removed after it returns, which is why the list must be copied when it is recorded. The search never stops early on a negative running total, because a hydrothermal vent may lead to rich coral further down. If several paths tie, it returns the one whose column sequence comes first in lexicographic order, since it tries moves from left to right and only replaces the best path on a strictly higher score.

For example, consider the following 3 x 3 grid:

```
     | 1   3   0 |
B =  | 4  -6  -2 |
     | 2   1   9 |
```

It has 17 valid paths: 5 starting from (1,1), 7 from (1,2), and 5 from (1,3). The only optimal path is (1,2) → (2,3) → (3,3), with a score of 3 + (-2) + 9 = 10, and it passes through the vent at (2,3). Always moving to the highest-scoring next coordinate scores only 7, 9, and 7 from the three starting columns, which is why the baseline checks every path.

The drawback is the number of paths. When m ≥ 2, every coordinate has two or three moves, so there are between m · 2^(n-1) and m · 3^(n-1) valid paths: 136,946 for a 10 x 10 grid and about 1.8 x 10^10 for a 20 x 20 grid.

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

Every call Explore(i, j, score, path) is made with path holding a valid path from row 1 to row i that ends at column j, and with score equal to its total. This holds for the calls from the outer loop, where path = [(1, j)] and score = B[1][j], and each recursive call extends path by one downward move inside the grid and adds that coordinate's score. Every call also returns with path unchanged, because a call at row n does not modify it and every other call removes each coordinate right after appending it. Since i grows by one with each call, the recursion always stops at row n.

Conversely, every valid path (c1, ..., cn) is reached by exactly one call at row n: the outer loop picks c1 once, and at each row the loop over next_col picks the next column once, because the three candidate columns are different. So the calls at row n correspond exactly to the valid paths, each with its correct score. At least one valid path always exists (straight down), and the algorithm keeps the highest score among these calls, so it returns the maximum total biomass density score and a path that achieves it.

**Algorithmic Strategy:**
Our algorithmic strategy will work similarly to Dijkstra's algorithm instead looking at all posible paths bellow the robot and find the path that holds the highest biomass.

Input: a matrix of corinates each holding a biomass score matrix: List[Lists[floats]], a starting node row, col and a list of past destinations
Expected Ouput: path to accumulate highest biomass score

'''
FUNCTION algo_strat(chart, row, col, past_visited):

    current_value ← chart[row][col]
    next_row ← row + 1
    destinations ← empty list
    highest ← NONE
    highest_value ← negative infinity

    IF next_row is greater than or equal to number of rows in chart:
        RETURN past_visited

    FOR next_col IN [col - 1, col, col + 1]:
        IF next_col is within the chart boundaries:
            ADD (next_row, next_col) TO destinations

    FOR each (destination_row, destination_col) IN destinations:
        destination_value ← chart[destination_row][destination_col]

        IF destination_value > highest_value:
            highest_value ← destination_value
            highest ← (destination_row, destination_col)

    ADD highest TO past_visited

    RETURN algo_strat(
        chart,
        highest row,
        highest column,
        past_visited
    )

'''

**Complexity Analysis:**