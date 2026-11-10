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