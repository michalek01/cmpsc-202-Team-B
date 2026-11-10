***Project 3: Navigating the Sea***

**Problem Formulation**  
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. 
Inputs: Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). 
Output: Determine the path that maximizes the total accumulated biomass density score.
Constraints: To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. 

**Algorithmic Strategy:**
Our algorithmic stratige will work similarly to Dijkstra's algorithm looking at all posible paths bellow the robot and find the path that holds the highest biomass.

Input: a matrix of corinates each holding a biomass score matrix: List[Lists[floats]], a starting node row, col and a list of past destinations
Expected Ouput: path to accumulate highest biomass score

'''
def algo_strat(chart, row, col, past_visited):
    current_value = chart[row][col]
    next_row = row + 1
    destinations = []
    highest = ()

    if next_row >= len(chart):
        return past_visited

    for next_col in (col - 1, col, col + 1):
        if 0 <= next_col < len(chart[0]):
            destinations.append((next_row, next_col))
    
    for row, col in destinations:
        if chart[row][col] > highest:
            highest = (row,col)
        else:
            None
    
    past_visited.append(highest)
    return algo_strat(chart, highest[0], highest[1], past_visited)

'''

**Baseline Solutions:**


**Complexity Analysis:**