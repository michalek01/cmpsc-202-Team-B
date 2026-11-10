***Project 3: Navigating the Sea***

**Problem Formulation**  
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. 


Inputs: Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). 


Output: Determine the path that maximizes the total accumulated biomass density score.


Constraints: To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. 

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

**Baseline Solutions:**


**Complexity Analysis:**