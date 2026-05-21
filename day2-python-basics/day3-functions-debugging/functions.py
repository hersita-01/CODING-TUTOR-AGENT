def greet():
    print("Hello Hersita")
greet()


def greet(name):
    print("Hello", name)
greet("Hersita")
greet("Python")


def add(a, b):
    return a + b
result = add(5, 3)
print(result)


def greet(name):
    print("Hello", name)
greet("Hersita")
greet("Python")


def add(a, b):
    return a + b
result = add(5, 3)
print(result)

try:
    number = int(input("Enter a number: "))
    print(number)
except:
    print("Invalid input")


file = open("notes.txt", "w")
file.write("Hello AI Tutor")
file.close()
print("File created")

file = open("notes.txt", "r")
content = file.read()
print(content)
file.close()

def calculator(a, b):
    print("Add:", a + b)
    print("Subtract:", a - b)
calculator(10, 5)