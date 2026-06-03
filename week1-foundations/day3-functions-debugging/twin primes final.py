import math

def isPrime(n):
    if n <= 1:
        return False

    for i in range(2, n // 2 + 1):
        if n % i == 0:
            return False
    return True

try:
    a = int(input("Enter a number: "))
    f = isPrime(a)

    if f:
        b = int(input("Enter another number: "))
        g = isPrime(b)

        if g:
            v = math.fabs(a - b)

            if v == 2:
                print("Twin Primes")
            else:
                print("Both the numbers are prime but they are not twin primes")
        else:
            print(a, "is prime but", b, "is not")
    else:
        print(a, "is not a prime number")

except ValueError:
    print("Invalid input! Please enter an integer.")

except Exception as e:
    print("An unexpected error occurred:", e)
