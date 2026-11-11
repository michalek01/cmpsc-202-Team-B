

def algo_strat(chart, row, col, past_visited):
    current_value = chart[row][col]
    next_row = row + 1
    destinations = []
    highest = None
    highest_value = float("-inf")

    if next_row >= len(chart):
        return past_visited

    for next_col in (col - 1, col, col + 1):
        if 0 <= next_col < len(chart[0]):
            destinations.append((next_row, next_col))
    
    for row, col in destinations:
        if chart[row][col] > highest_value:
            highest_value = chart[row][col]
            highest = (row,col)
    
    past_visited.append(highest)
    return algo_strat(chart, highest[0], highest[1], past_visited)



# def test():
    chart = [
        [0, 0, 0],
        [4, 5, 2],
        [9, 3, 5],
    ]

    result = algo_strat(chart, 0, 1, [])
    print(result)

# test()


