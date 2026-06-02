num = int(input("Enter an integer: "))
str = input("Enter the string: ")

digitsStr = ''
digitsNum = 0;

for ch in str :
    if ch.isdigit() :
        digitsStr += ch

if digitsStr :
    digitsNum = int(digitsStr)

print(num, "+", digitsNum, "=", (num + digitsNum))
