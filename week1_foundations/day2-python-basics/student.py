name="hersita"
marks=[94,89,92]

total=sum(marks)
print("Name of the Student :" , name)
print("Total marks of the Student :", total)

percent=total/len(marks)
if percent>=40:
    print("Pass")
else:
    print("Fail")

for mark in marks:
    print(mark)