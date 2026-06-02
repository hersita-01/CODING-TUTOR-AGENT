t=()
while True:
    name=input("Enter the name of the student:")
    rno=int(input("Enter the roll number of the student:"))
    marks=int(input("Enter the marks of the student :"))
    stu=((rno,name,marks),)
    t=t+(stu,)
    check=eval(input("Do you want to continue Y/N :"))
    if check in 'yY':
        continue
    else :
        break
print(t)
