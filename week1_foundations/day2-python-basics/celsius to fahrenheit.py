temp = float(input("Enter Temperature: "))
unit = input("Enter unit('C' for Celsius or 'F' for Fahrenheit): ")

if unit == 'C' or unit == 'c' :
    new = 9 / 5 * temp + 32
    print("Temperature in Fahrenheit =", new)
elif unit == 'F' or unit == 'f' :
    new = 5 / 9 * (temp - 32)
    print("Temperature in Celsius =", new)
else :
    print("Unknown unit", unit)
