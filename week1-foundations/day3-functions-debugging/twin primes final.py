import math
def isPrime(n):
    for i in range (2,n//2+1):
        if n%i==0:
            return False
    else:
        if n==1:
            return False
        else:
            return True
a=int(input("Enter a number : "))
f=isPrime(a)
if f:
    b=int(input("Enter another number : "))
    g=isPrime(b)
    if  g:
        v=math.fabs(a-b)
        if v==2:
            print("twin Primes")
        else:
            print("Both the numbers are prime but they are not twin primes ")
    else:
        if f:
            print(a,"is prime but ",b," is not")
        elif  g:
            print(b,"is prime but ",a,"is not")
        else:
            print("Both are composite")
else:
    print(a, "is not a prime number")
        
