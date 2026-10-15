def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)


data = []

result = calculate_average(data)

print(f"Average: {result}")
