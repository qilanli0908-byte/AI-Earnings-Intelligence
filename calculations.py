
def calculate_return(first_price, latest_price):

    if first_price == 0:
        return None

    result = (latest_price - first_price) / first_price * 100

    return result
