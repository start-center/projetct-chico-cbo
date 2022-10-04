def binary_search(sorted_array, element):
    left = 0
    right = len(sorted_array) - 1
    middle = 0

    while left <= right:
        middle = (left + right) // 2
        if sorted_array[middle] < element:
            left = middle + 1
        elif sorted_array[middle] > element:
            right = middle - 1
        else:
            return middle
            
    return -1