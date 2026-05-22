# loop_mastery.py
"""
A complete reference script covering core Python loops, 
loop helpers (enumerate, zip), and flow control statements.
"""

print("=========================================")
print("1. CORE LOOPS: FOR vs WHILE")
print("=========================================\n")

# A standard for loop (Iterates over a known sequence or range)
print("--- Standard For Loop ---")
items = ["apple", "banana", "cherry"]
for fruit in items:
    print(f"Processing fruit: {fruit}")

print("\n--- Standard While Loop ---")
# A standard while loop (Runs as long as a conditional test remains True)
count = 3
while count > 0:
    print(f"Countdown: {count}")
    count -= 1  # Crucial: update condition to avoid an infinite loop

print("\n=========================================")
print("2. LOOP HELPERS: ENUMERATE & ZIP")
print("=========================================\n")

print("--- Enumerate Helper ---")
# Use enumerate() to automatically generate an index counter alongside items
players = ["Alice", "Bob", "Charlie"]
for index, name in enumerate(players):
    print(f"Player Rank {index + 1}: {name}")

print("\n--- Zip Helper ---")
# Use zip() to merge multiple lists and iterate over them side-by-side
products = ["Laptop", "Mouse", "Keyboard"]
prices = [1200, 25, 75]
for product, price in zip(products, prices):
    print(f"The {product} costs ${price}")

print("\n=========================================")
print("3. FLOW CONTROL: BREAK, CONTINUE, & ELSE")
print("=========================================\n")

print("--- Continue Statement ---")
# continue skips the rest of the current iteration block and jumps straight to the next round
numbers = [1, 2, 3, 4, 5]
print("Printing only odd numbers:")
for num in numbers:
    if num % 2 == 0:
        continue  # Skips the print statement for even numbers
    print(f"Odd number found: {num}")

print("\n--- Break Statement & Else Clause Trigger ---")
# Scenario A: The loop finishes normally (Else block executes!)
target_search_1 = 99
print(f"Searching list for target: {target_search_1}")
for num in numbers:
    if num == target_search_1:
        print("Target found! Breaking loop.")
        break
else:
    # This block executes ONLY if the loop finishes without hitting a 'break'
    print("⚠️ Else Triggered: The loop finished naturally. Target was not found.")

print("\nScenario B: The loop hits a break (Else block gets skipped!)")
target_search_2 = 3
print(f"Searching list for target: {target_search_2}")
for num in numbers:
    if num == target_search_2:
        print(f"🎯 Target {num} found! Breaking loop early.")
        break
else:
    print("This will not print because the loop hit a break statement.")

print("\n=========================================")
print("Execution complete.")
print("=========================================")