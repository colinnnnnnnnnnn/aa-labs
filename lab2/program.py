import random
import time
from typing import Callable, List

import matplotlib.pyplot as plt
from prettytable import PrettyTable


def quick_sort(arr: List[int]) -> List[int]:
	if len(arr) < 2:
		return arr

	stack = [(0, len(arr) - 1)]
	while stack:
		left, right = stack.pop()
		if left >= right:
			continue

		pivot = arr[random.randint(left, right)]
		i, j = left, right
		while i <= j:
			while arr[i] < pivot:
				i += 1
			while arr[j] > pivot:
				j -= 1
			if i <= j:
				arr[i], arr[j] = arr[j], arr[i]
				i += 1
				j -= 1

		if left < j:
			stack.append((left, j))
		if i < right:
			stack.append((i, right))

	return arr


def merge_sort(arr: List[int]) -> List[int]:
	if len(arr) <= 1:
		return arr

	mid = len(arr) // 2
	left = merge_sort(arr[:mid])
	right = merge_sort(arr[mid:])

	merged: List[int] = []
	i = 0
	j = 0
	while i < len(left) and j < len(right):
		if left[i] <= right[j]:
			merged.append(left[i])
			i += 1
		else:
			merged.append(right[j])
			j += 1

	if i < len(left):
		merged.extend(left[i:])
	if j < len(right):
		merged.extend(right[j:])

	return merged


def heap_sort(arr: List[int]) -> List[int]:
	def sift_down(start: int, end: int) -> None:
		root = start
		while True:
			child = 2 * root + 1
			if child > end:
				return
			if child + 1 <= end and arr[child] < arr[child + 1]:
				child += 1
			if arr[root] < arr[child]:
				arr[root], arr[child] = arr[child], arr[root]
				root = child
			else:
				return

	n = len(arr)
	for start in range((n - 2) // 2, -1, -1):
		sift_down(start, n - 1)

	for end in range(n - 1, 0, -1):
		arr[end], arr[0] = arr[0], arr[end]
		sift_down(0, end - 1)

	return arr


def radix_sort(arr: List[int]) -> List[int]:
	if not arr:
		return arr

	max_value = max(arr)
	exp = 1
	output = arr[:]
	while max_value // exp > 0:
		count = [0] * 10
		for value in output:
			count[(value // exp) % 10] += 1
		for i in range(1, 10):
			count[i] += count[i - 1]

		temp = [0] * len(output)
		for i in range(len(output) - 1, -1, -1):
			digit = (output[i] // exp) % 10
			count[digit] -= 1
			temp[count[digit]] = output[i]

		output = temp
		exp *= 10

	return output


def get_algorithm() -> tuple[str, Callable[[List[int]], List[int]]]:
	algorithms = {
		"1": ("Quick Sort", quick_sort),
		"2": ("Merge Sort", merge_sort),
		"3": ("Heap Sort", heap_sort),
		"4": ("Radix Sort", radix_sort),
	}

	prompt = (
		"Choose sorting algorithm:\n"
		"1) Quick Sort\n"
		"2) Merge Sort\n"
		"3) Heap Sort\n"
		"4) Radix Sort\n"
		"Enter choice (1-4): "
	)

	while True:
		choice = input(prompt).strip()
		if choice in algorithms:
			return algorithms[choice]
		print("Invalid choice. Please enter 1, 2, 3, or 4.")


def time_algorithm(
	sorter: Callable[[List[int]], List[int]], sizes: List[int]
) -> List[float]:
	times: List[float] = []
	for size in sizes:
		data = [random.randint(0, 1_000_000) for _ in range(size)]
		working = data[:]
		start = time.perf_counter()
		result = sorter(working)
		if result is not None:
			working = result
		end = time.perf_counter()
		times.append(end - start)
	return times


def main() -> None:
	random.seed()
	sizes = [10, 100, 500, 1000, 5000, 10000, 50000, 100000]
	algo_name, sorter = get_algorithm()

	times = time_algorithm(sorter, sizes)

	table = PrettyTable()
	table.field_names = ["Size", "Time (s)"]
	for size, elapsed in zip(sizes, times):
		table.add_row([size, f"{elapsed:.6f}"])

	print(f"\nResults for {algo_name}:")
	print(table)

	plt.figure(figsize=(8, 5))
	plt.plot(sizes, times, marker="o", linewidth=2)
	plt.xscale("log")
	plt.xlabel("Array Size")
	plt.ylabel("Time (s)")
	plt.title(f"{algo_name} Performance")
	plt.grid(True, which="both", linestyle="--", alpha=0.5)
	plt.tight_layout()
	plt.show()


if __name__ == "__main__":
	main()
