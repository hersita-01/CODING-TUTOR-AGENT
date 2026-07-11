def conversion(x):
    try:
        p = x * 82
        print("Amount in rupees:", p)
    except Exception as e:
        print("Error during conversion:", e)

try:
    a = int(input("Enter amount in dollar: "))
    conversion(a)
except ValueError:
    print("Invalid input! Please enter a valid integer amount.")
except Exception as e:
    print("An unexpected error occurred:", e)
