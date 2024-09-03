import random

import multiprocessing as mp
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

def single_process():
    return test_program(100, 42)

def multithreaded():
    tp = ThreadPool(4)
    return tp.starmap(test_program, [(100, 42) for _ in range(10)])

def multiprocessed():
    mp = Pool(4)
    return mp.starmap(test_program, [(100, 42) for _ in range(10)])

def addition(a, b):
    return a + b

def division(a, b):
    return a / b

def generate_random_list(n):
    return [random.randint(1,1000) for _ in range(n)]

def add_at_ran_idx(arr, v):
    arr.insert(random.randint(0,len(arr)), v)
    return arr

def bubble_sort(arr):
    n = len(arr)
    # Traverse through all array elements
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def binary_search(arr, x):
    low = 0
    high = len(arr)
    
    while low < high:
        mid = (high + low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            high = mid-1
        else:
            low = mid+1

    if arr[low] == x:
        return low
        
    return None

def remove_uneven(arr):
    return [v for v in arr if v % 2 == 0]

def calculate_mean(arr):
    arr_sum = 0
    for a in arr:
        arr_sum = addition(a, arr_sum)

    return division(arr_sum, len(arr))

def test_program(n, v):
    arr = generate_random_list(n)
    arr = add_at_ran_idx(arr, v)
    arr = bubble_sort(arr)
    idx = binary_search(arr, v)
    arr = remove_uneven(arr)
    mean = calculate_mean(arr)
    return mean

def main():
    results_sp = single_process()
    results_mt = multithreaded()
    results_mp = multiprocessed()

    print(
        (
            f'Single process results: {results_sp}\n'
            f'Multithreading results: {results_mt}\n'
            f'Multiprocessing results: {results_mp}\n'
        )
    )

if __name__ == '__main__':
    main()