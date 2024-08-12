import numpy as np
from time import perf_counter


class PriceSetter1:

    def __init__(self, rounds):
        """
        Initialize the price setter.
        In this settings, the values of the costumers is constant and unknown in advance.

        Args:
            rounds (int): the number of rounds to simulate
        """
        self.lower_bound = 0.0
        self.upper_bound = 1.0
        self.price = (self.lower_bound + self.upper_bound) / 2
        self.gr = (1 + np.sqrt(5)) / 2  # golden ratio


    def set_price(self, t):
        """
        Return the price at time t.

        Args:
            t (int): the time period

        Returns:
            float: the price at time t
        """
        return self.price


    def update(self, t, outcome):
        """
        Update the price setter based on the outcome of the previous period.

        Args:
            t (int): the time period
            outcome (int): the outcome of the previous period - true if the product was sold, false otherwise
        """
        # Calculate the new bounds based on the golden ratio
        def golden_ratio():
            return (self.upper_bound - self.lower_bound) / self.gr
        
        c1 = self.upper_bound - golden_ratio()
        c2 = self.lower_bound + golden_ratio()

        # Update the bounds based on the outcome
        if outcome:
            self.lower_bound = c1
        else:
            self.upper_bound = c2

        # Update the current price based on the new bounds
        self.price = self.upper_bound - golden_ratio()


def simulate(simulations, rounds):
    """
    Simulate the game for the given number of rounds.

    Args:
        rounds (int): the number of rounds to simulate

    Returns:
        float: the revenue of the price setter
    """
    simulations_results = []
    for _ in range(simulations):
        start = perf_counter()
        price_setter = PriceSetter1(rounds)
        end = perf_counter()
        if end - start > 1:
            raise Exception("The initialization of the price setter is too slow.")
        revenue = 0
        costumer_value = np.random.uniform(0, 1)
        #rounds is number of customers
        for t in range(rounds):
            start = perf_counter()
            price = price_setter.set_price(t)
            end = perf_counter()
            if end - start > 0.1:
                raise Exception("The set_price method is too slow.")
            if costumer_value >= price:
                revenue += price

            start = perf_counter()
            price_setter.update(t, costumer_value >= price)
            end = perf_counter()
            if end - start > 0.1:
                raise Exception("The update method is too slow.")

        simulations_results.append(revenue)

    return np.mean(simulations_results)


if __name__ == "__main__":
    np.random.seed(0)
    print(simulate(3000, 1000))
