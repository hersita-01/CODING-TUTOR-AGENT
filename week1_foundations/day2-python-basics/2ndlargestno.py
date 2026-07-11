l=[]
maximum=0
maxi=0
n=int(input("Enter the number of elements you want to enter :"))
for i in range (0,n):
    a=int(input("Enter the elements "))
    l.append(a)
for i in l:
    if i>maximum:
        maximum=i
for i in l:
    if i>maxi and i<maximum:
        maxi=i
print("The 2nd largest element is ",maxi)
    
