# job_exponential.py
def fib(n):
    return 1 if n <= 2 else fib(n - 1) + fib(n - 2)

fib(30)  # slow enough for demo but won't freeze your PC
