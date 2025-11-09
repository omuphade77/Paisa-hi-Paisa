# primes.py
for num in range(2, 21):
    is_prime = all(num % i != 0 for i in range(2, num))
    if is_prime:
        print(num, "is prime")
