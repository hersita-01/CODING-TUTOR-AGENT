import random
def ran(a,b):
    for i in range(3):
        x=random.randint(a,b)
        print("The number is ",x)

d=int(input("Enter "))
e=int(input("Enter "))
print(ran(d,e))
