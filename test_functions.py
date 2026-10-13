
from calculations import calculate_return

first_price = 100
latest_price = 120

result = calculate_return(first_price, latest_price)

print(f"Stock Return: {result:.2f}%")
