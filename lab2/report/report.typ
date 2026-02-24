#import "report_template.typ": temp

#set document(title: [
  Report
])

#show: temp.with(
  lab-number: "2",
  title: "Study and empirical analysis of sorting algorithms",
  year: "2026",
  group: "FAF-243",
  name: "Poiata Calin"
)

= ALGORITHM ANALYSIS

== Objective

Study and analyze the empirical performance of sorting algorithms on randomized integer arrays.

== Tasks

#block[
    #set enum(indent: 3em)
1. Implement QuickSort, MergeSort, HeapSort, and RadixSort in a programming language;
2. Establish properties of the input data for the analysis;
3. Choose a metric for comparing the algorithms;
4. Perform empirical analysis of the algorithms;
5. Present the results graphically;
6. Draw conclusions from the obtained data.
]

== Theoretical Notes

Empirical analysis complements theoretical complexity by observing real execution times on
concrete inputs. It is useful for comparing implementations, estimating practical constants, and
understanding behavior on specific data distributions.

The standard steps are:
1. Define the analysis goal.
2. Select a metric (time or operation count).
3. Specify input properties (size, range, distribution).
4. Implement the algorithms.
5. Generate multiple test datasets.
6. Run experiments and record results.
7. Analyze and visualize the measurements.

== Introduction

Sorting is a fundamental operation in computer science that arranges data into a specific order,
most commonly ascending. The efficiency of sorting depends on algorithmic complexity, memory
behavior, and data distribution. For this laboratory, four classic sorting techniques are compared:
quick sort, merge sort, heap sort, and radix sort. The first three are comparison-based, while radix
sort is non-comparison based and leverages digit processing for integer keys.

== Comparison Metric

The comparison metric is wall-clock execution time for sorting arrays of increasing size.

== Input Format

Each algorithm receives randomized integer arrays with sizes:
$10, 100, 500, 1000, 5000, 10000, 50000, 100000$. The values are uniformly generated integers in
the range $[0, 1000000]$.

= IMPLEMENTATION

All algorithms are implemented in Python. The program prompts the user to select the algorithm,
generates random arrays for each size, sorts them, and records the execution time. Results are
printed using PrettyTable and plotted using matplotlib.

== Quick Sort

_Algorithm Description:_

Quick sort is a divide-and-conquer algorithm that partitions an array around a pivot, then sorts
the partitions recursively. Average time complexity is $O(n log n)$ with good cache performance.

_Pseudocode:_

```
QuickSort(A, low, high):
    if low < high:
        p <- partition(A, low, high)
        QuickSort(A, low, p - 1)
        QuickSort(A, p + 1, high)
```

_Implementation:_

```python
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
```

_Results:_

#figure(
    image("images/quick_table.png", width: 25%),
    caption: "Results for Quick Sort",
)

#figure(
    image("images/quick_graph.png", width: 60%),
    caption: "Quick Sort Performance Graph",
)

== Merge Sort

_Algorithm Description:_

Merge sort splits the array, sorts each half, and merges the results. It has stable behavior and
guaranteed $O(n log n)$ time complexity at the cost of additional memory.

_Pseudocode:_

```
MergeSort(A):
    if |A| <= 1: return A
    mid <- |A|/2
    L <- MergeSort(A[0:mid])
    R <- MergeSort(A[mid:])
    return Merge(L, R)
```

_Implementation:_

```python
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
```

_Results:_

#figure(
    image("images/merge_table.png", width: 25%),
    caption: "Results for Merge Sort",
)

#figure(
    image("images/merge_graph.png", width: 60%),
    caption: "Merge Sort Performance Graph",
)

== Heap Sort

_Algorithm Description:_

Heap sort builds a max heap, then repeatedly extracts the maximum to build a sorted array. It
guarantees $O(n log n)$ time complexity with $O(1)$ extra space.

_Pseudocode:_

```
HeapSort(A):
    BuildMaxHeap(A)
    for i from n-1 downto 1:
        swap A[0], A[i]
        Heapify(A, 0, i)
```

_Implementation:_

```python
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
```

_Results:_

#figure(
    image("images/heap_table.png", width: 25%),
    caption: "Results for Heap Sort",
)

#figure(
    image("images/heap_graph.png", width: 60%),
    caption: "Heap Sort Performance Graph",
)

== Radix Sort

_Algorithm Description:_

Radix sort processes integer digits from least significant to most significant using counting
sort as a stable subroutine. For fixed-size integers, the time complexity is $O(k \cdot n)$.

_Pseudocode:_

```
RadixSort(A):
    exp <- 1
    while max(A)/exp > 0:
        CountingSortByDigit(A, exp)
        exp <- exp * 10
```

_Implementation:_

```python
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
```

_Results:_

#figure(
    image("images/radix_table.png", width: 25%),
    caption: "Results for Radix Sort",
)

#figure(
    image("images/radix_graph.png", width: 60%),
    caption: "Radix Sort Performance Graph",
)

= CONCLUSION

The empirical results show the expected $O(n log n)$ growth for the comparison-based algorithms
and a lower slope for radix sort on fixed-size integers. For small sizes, all algorithms perform within
fractions of a millisecond, with minor variability due to constant factors. For large inputs (50,000 and
100,000 elements), radix sort is the fastest, reaching $0.135337$ seconds at 100,000 elements. Quick
sort performs best among comparison-based methods on the larger datasets, while merge sort and heap
sort show similar, slightly higher timings in this experiment.

Overall, radix sort is preferable when keys are non-negative integers with bounded digit length,
while quick sort is a strong general-purpose choice for in-memory sorting due to its practical speed and
in-place behavior. Merge sort offers predictable performance and stability, and heap sort provides
consistent $O(n log n)$ time with minimal extra space.
