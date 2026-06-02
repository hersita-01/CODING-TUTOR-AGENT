def fact(n):
        fact=1
        for i in range (n,1,-1):
            fact= fact*i
        return fact
ch=int(input("1 for S1 and 2 for S2 :"))
if ch==1:
    n=int(input("Enter the value of n (terminating value):"))
    s=0
    for i in range ( 2,n+1):
        f=fact(i)
        d=1/f
        s=s+d
    print(s)
elif ch==2:
    n=int(input("Enter the value of n (terminating value):"))
    x=int(input("Enter the value of x(numerator value):"))
    s=0
    for i in range (2,n+1):
        num=fact(i)
        numerator=x**num
        denum=fact(i+1)
        s=s+numerator/denum
    print(s)
else:
    print("Invalid choice")

        

    
        
