

def baseline(chart, row, col, past_visited):
    next_row = row + 1
    destinations = []
    highest_value = float("-inf")
    best_option = None
    
    if next_row >= len(chart):
        return past_visited

    opt = []
    for next_col in (col - 1, col, col + 1):
        if 0 <= next_col < len(chart[0]):
            destination = (next_row, next_col)
            destinations.append(destination)

            new_path = past_visited + [destination]
            opt.append(baseline(chart, next_row, next_col, new_path))

    for index in range(len(opt)):
        option = opt[index]
        destination = destinations[index]
        total = 0

        for option_row, option_col in option:
            total += chart[option_row][option_col]

        if total > highest_value:
            highest_value = total
            best_option = option
    
    return best_option



def test():
    chart = [
        [1, 3, 0],
        [2, -6, -2],
        [2, 1, 9],
    ]

    result = baseline(chart, 0, 1, [])
    print(result)

test()


