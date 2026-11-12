***Project 3: Navigating the Sea***

**Problem Formulation**  
You are charting a newly discovered, biologically dense ocean trench represented by an nm grid of vertical depth zones and horizontal coordinates. 


Inputs: Each coordinate (i,j) has a surveyed "biomass density" score B(i,j), which can be positive (rich coral) or negative (hazardous hydrothermal vents that damage sensors). An autonomous submersible drops from the surface (row 1) and must navigate to the ocean floor (row n). 


Output: Determine the path that maximizes the total accumulated biomass density score.


Constraints: To conserve battery, the submersible can only move downward. From zone (i,j), it can only move to (i+1,j-1) (down-left), (i+1,j) (straight down), or (i+1,j+1) (down-right). The submersible can start at any horizontal coordinate on the surface and end at any horizontal coordinate on the floor. 

**Baseline Solutions:**
Our baseline soulution will work by checking every Possible path for the maximum value of biomass density amoung them.

Input: a matrix of corinates each holding a biomass score matrix: List[Lists[floats]], a starting node row, col and a list of past destinations
Expected Ouput: path to accumulate highest biomass score

'''
ALGORITHM FindBestPath(chart, row, column, visitedPath)

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
'''

**Algorithmic Solutions:**


**Complexity Analysis:**