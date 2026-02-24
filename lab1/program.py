
import time
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import math
from decimal import Decimal, Context, ROUND_HALF_EVEN

# -------------------------------------------------
# Fibonacci methods
# -------------------------------------------------

# 1. Recursive
def fib_recursive(n):
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)


# 2. Dynamic programming (list)
def fib_dynamic(n):
    if n <= 1:
        return n

    dp = [0] * (n + 1)
    dp[1] = 1

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]

    return dp[n]


# 3. Matrix exponentiation
def multiply(F, M):
    x = F[0][0]*M[0][0] + F[0][1]*M[1][0]
    y = F[0][0]*M[0][1] + F[0][1]*M[1][1]
    z = F[1][0]*M[0][0] + F[1][1]*M[1][0]
    w = F[1][0]*M[0][1] + F[1][1]*M[1][1]

    F[0][0], F[0][1], F[1][0], F[1][1] = x, y, z, w


def matrix_power(F, n):
    if n <= 1:
        return

    M = [[1, 1], [1, 0]]

    matrix_power(F, n // 2)
    multiply(F, F)

    if n % 2 != 0:
        multiply(F, M)


def fib_matrix(n):
    if n == 0:
        return 0

    F = [[1, 1], [1, 0]]
    matrix_power(F, n - 1)
    return F[0][0]


# 4. Binet formula
def fib_binet(n):
    if n == 0:
        return 0

    # high precision context
    ctx = Context(prec=100, rounding=ROUND_HALF_EVEN)

    # constants
    sqrt5 = ctx.sqrt(Decimal(5))
    phi = (Decimal(1) + sqrt5) / Decimal(2)
    psi = (Decimal(1) - sqrt5) / Decimal(2)

    # Binet formula with Decimal power
    a = ctx.power(phi, Decimal(n))
    b = ctx.power(psi, Decimal(n))

    result = (a - b) / sqrt5

    return int(result.to_integral_value())

# 5. Fast doubling
def fib_fast_doubling(n):
    def helper(n):
        if n == 0:
            return (0, 1)
        else:
            a, b = helper(n // 2)
            c = a * (2*b - a)
            d = a*a + b*b
            if n % 2 == 0:
                return (c, d)
            else:
                return (d, c + d)

    return helper(n)[0]


# -------------------------------------------------
# Benchmark
# -------------------------------------------------

def run_benchmark(method):
    numbers = [_ for _ in range(0, 16001, 1000)]
    results = []

    for n in numbers:
        start = time.perf_counter()

        if method == "recursion":
            fib_recursive(n)
        elif method == "dynamic":
            fib_dynamic(n)
        elif method == "matrix":
            fib_matrix(n)
        elif method == "binet":
            fib_binet(n)
        elif method == "fast":
            fib_fast_doubling(n)
        else:
            print("Invalid method")
            return

        end = time.perf_counter()
        results.append((n, end - start))

    # PrettyTable
    table = PrettyTable()
    table.field_names = ["n", "Time (seconds)"]

    for n, t in results:
        table.add_row([n, f"{t:.6f}"])

    print(f"\nTiming results for: {method}")
    print(table)

    # Plot
    x_vals = [n for n, _ in results]
    y_vals = [t for _, t in results]

    plt.figure()
    plt.plot(x_vals, y_vals, marker='o')
    plt.title(f"Fibonacci Timing ({method})")
    plt.xlabel("n")
    plt.ylabel("Time (seconds)")
    plt.grid(True)
    plt.show()


# -------------------------------------------------
# Menu
# -------------------------------------------------

def choose_algorithm():
    print("Choose algorithm:")
    print("1 - Recursion")
    print("2 - Dynamic programming")
    print("3 - Matrix power")
    print("4 - Binet formula")
    print("5 - Fast doubling")

    choice = input("Enter choice: ")

    if choice == "1":
        run_benchmark("recursion")
    elif choice == "2":
        run_benchmark("dynamic")
    elif choice == "3":
        run_benchmark("matrix")
    elif choice == "4":
        run_benchmark("binet")
    elif choice == "5":
        run_benchmark("fast")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    choose_algorithm()

