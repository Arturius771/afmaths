from afmaths.operation import add, divide_by, exponentiate, multiply


def compounding_interest(principal: float, rate: float, time: float, n: int) -> float:
    """
    Calculates the compound interest on a principal amount.

    Formula: A = P * (1 + r/n)^(n*t)

    Parameters:
    principal (float): The initial amount of money.
    rate (float): The annual interest rate (as a decimal).
    time (float): The time the money is invested for in years.
    n (int): The number of times that interest is compounded per year.

    Returns:
    float: The amount of money accumulated after n years, including interest.
    """

    return multiply(principal)(
        exponentiate(multiply(n)(time))(add(1)(divide_by(n)(rate)))
    )


if __name__ == "__main__":
    # Example usage:
    principal_amount = 100_000  # Initial amount of money
    annual_rate = 0.05
    investment_time = 20  # Time in years
    compounding_frequency = 4  # Compounded quarterly

    accumulated_amount = compounding_interest(
        principal_amount, annual_rate, investment_time, compounding_frequency
    )
    print(f"Accumulated amount after {investment_time} years: {accumulated_amount:.2f}")
