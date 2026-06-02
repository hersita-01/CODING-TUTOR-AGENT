s=input("Enter a string")
new=""
for i in s:
    if i in "AEIOUaeiou":
        i="*"
        new=new+i
    else:
        new=new +i
print(new)
        