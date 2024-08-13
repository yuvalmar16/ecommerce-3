import copy

import numpy as np
from time import perf_counter


class AuctionClient:
    def __init__(self, value, clients_num, insurances_num):
        """Initializes the AuctionClient class.

        Args:
            value (float): The value of the client for a year of insurance.
            clients_num (int): The number of clients in the simulation.
            manufacturers_num (int): The number of manufacturers in the simulation.
        """
        self.value = value
        self.clients_num = clients_num
        self.insurances_num = insurances_num
        self.history = []
        self.wins = 0


    # def decide_bid(self, t, duration):
    #     """
    #     Decides the bid of the client at time t given the duration of the insurance.

    #     Args:
    #         t (int): The current time.
    #         duration (int): The duration of the insurance.

    #     Returns:
    #         float: The bid of the client
    #     """
    #     # remaining_auctions = self.insurances_num - t
    #     # if self.clients_num < self.insurances_num:
    #     #     bid = (self.value ) * (1 - np.exp(- t / self.insurances_num))*(1-self.wins/self.clients_num)

    #     remaining_auctions = self.insurances_num - t
    #     win_rate = self.wins / (t + 1) if t > 0 else 0

    #     if self.clients_num < self.insurances_num:
    #     # Consider both the value, duration, and a factor based on the number of wins
    #          bid = (self.value * duration) * (1 - np.exp(- t / self.insurances_num)) * (1 - win_rate)

    #     else:
    #         bid = (self.value * duration) * (1 - np.exp(- t / self.insurances_num)) - 0.5

    #      # Ensure bid is non-negative
    #     return max(bid, 0.1 * self.value)


    def decide_bid(self, t, duration):
        """
        Decides the bid of the client at time t given the duration of the insurance.

        Args:
            t (int): The current time.
            duration (int): The duration of the insurance.

        Returns:
            float: The bid of the client
        """
        remaining_auctions = self.insurances_num - t
        win_rate = self.wins / (t + 1) if t > 0 else 0

        if self.clients_num < self.insurances_num:
            # Increase bid aggressiveness as the number of remaining auctions decreases
            if remaining_auctions <= self.insurances_num / 2:
                bid = (self.value * duration) * (1 - np.exp(- t / self.insurances_num)) * (1.2 - win_rate) + 0.1
            else:
                # Use a more conservative approach initially
                bid = (self.value * duration) * (1 - np.exp(- t / self.insurances_num)) * (0.9 - win_rate) + 0.1

#option 2
            # remaining_auctions = self.insurances_num - t
            # if remaining_auctions > self.insurances_num / 2:
            #     bid = 0.2 * (self.value * duration)  # Bid low early on
            # else:
            #     # Gradually increase bid as auctions progress, up to 2x the value
            #     bid = (0.2 + 1.8 * (1 - remaining_auctions / (self.insurances_num / 2))) * (self.value * duration) * (1 + (1 - win_rate))
        
        
        else:
            bid = (self.value * duration) * (1 - np.exp(- t / self.insurances_num)) - 0.5

        # Ensure bid is non-negative and above a certain threshold to remain competitive
        return max(bid, 0.1 * self.value)


    def update(self, t, price):
        """
        Updates the client based on the price
        of the winning bid at time t.

        Args:
            t (int): The current time.
            price (float): The price of the winning bid.
        """
        self.history.append(price)
        if price <= self.value:
            self.wins += 1  # Track wins to adjust future bids


def auction_client_creator(value, clients_num, insurances_num):
    return AuctionClient(value, clients_num, insurances_num)


class NaiveAuctionClient:
    def __init__(self, value, clients_num, insurances_num):
        """
        Initializes the NaiveAuctionClient class.
        It offers its actual value for the product.
        """
        self.value = value
        self.clients_num = clients_num
        self.manufacturers_num = insurances_num

    def decide_bid(self, t, quality):
        return self.value

    def update(self, t, price):
        pass


def naive_auction_client_creator(value, clients_num, insurances_num):
    return NaiveAuctionClient(value, clients_num, insurances_num)


def simulate_single_auction(num_of_competitors, number_of_insurances):
    """
    Simulates a single auction game.
    Args:
        your_client: your AuctionClient object
        num_of_competitors: number of competitors
        number_of_insurances: number of insurances

    Returns:

    """

    start = perf_counter()
    your_value = np.random.beta(5, 2)
    your_client = auction_client_creator(your_value, num_of_competitors + 1, number_of_insurances)
    end = perf_counter()
    if end - start > 2:
        raise Exception("The initialization of the client took too long.")

    competing_clients_list = [naive_auction_client_creator(np.random.beta(5, 2), num_of_competitors,
                                                           number_of_insurances) for _ in range(num_of_competitors)]

    active_competing_clients = copy.deepcopy(competing_clients_list)
    for t in range(number_of_insurances):

        duration = 3 * np.random.beta(2, 5)

        start = perf_counter()
        your_bid = your_client.decide_bid(t, duration)
        end = perf_counter()
        if end - start > 0.5:
            raise Exception("The decision of the bid took too long.")

        competing_bid_list = [client.decide_bid(t, duration) for client in active_competing_clients]

        if len(active_competing_clients) == 0:
            if your_bid == -1:  # you didn't want to bid
                continue
            else:
                return duration * your_value

        if your_bid == -1:  # you didn't want to bid
            if len(active_competing_clients) == 1:
                second_highest_bid = 0
                active_competing_clients.pop(0)

            else:

                highest_bid = max(competing_bid_list)
                clients_with_highest_bid = [i for i, bid in enumerate(competing_bid_list) if bid == highest_bid]
                winner = np.random.choice(clients_with_highest_bid)
                second_highest_bid = max([bid for i, bid in enumerate(competing_bid_list) if i != winner])
                active_competing_clients.pop(winner)

        else:
            # Check if you are the winner of the auction. Determine tie-breaks randomly.
            highest_bid = max(your_bid, max(competing_bid_list))
            clients_with_highest_bid = [-1] if your_bid == highest_bid else []
            clients_with_highest_bid += [i for i, bid in enumerate(competing_bid_list) if bid == highest_bid]
            winner = np.random.choice(clients_with_highest_bid)
            second_highest_bid = your_bid if winner != -1 else 0
            less_then_maximum_scores = [bid for i, bid in enumerate(competing_bid_list) if i != winner]
            if len(less_then_maximum_scores) > 0:
                second_highest_bid = max(second_highest_bid, max(less_then_maximum_scores))

            # if you are the winner you get your utility and the simulation ends.
            # otherwise, the winner is removed from the list of active clients and the simulation continues.
            if winner == -1:
                return duration * (your_value - second_highest_bid)

            else:
                active_competing_clients.pop(winner)

        start = perf_counter()
        your_client.update(t, second_highest_bid)
        end = perf_counter()
        if end - start > 0.5:
            raise Exception("The update of the client took too long.")
        for client in active_competing_clients:
            client.update(t, second_highest_bid)

    return 0.5 * your_value  # if the simulation ends and you didn't win, you get default utility.


def simulate(simulations, num_of_competitors, number_of_insurances):
    """
    Simulates the auction game for the given number of rounds.

    Args:
        simulations (int): The number of simulations to run.
        num_of_competitors (int): The number of competitors in the simulation.
        number_of_insurances (int): The number of insurances in the simulation.

    Returns:
        float: The revenue of your client.
    """

    revenues_list = []
    for _ in range(simulations):
        revenue = simulate_single_auction(num_of_competitors, number_of_insurances)
        revenues_list.append(revenue)

    return np.mean(revenues_list)


VARIABLES_VALUES = [(10, 5), (5, 10), (10, 10), (20, 10), (10, 20), (20, 20)]
BASELINES = [0.3565, 0.756, 0.3565, 0.3565, 0.856, 0.3565]

if __name__ == "__main__":
    """ Original code:
    
    np.random.seed(0)
    for i, (num_of_competitors, number_of_insurances) in enumerate(VARIABLES_VALUES):
        result = simulate(1000, num_of_competitors, number_of_insurances)
        if result < BASELINES[i]:
            raise Exception("You didn't beat the baseline.")

    print("All simulations passed.")
    """
    
    np.random.seed(0)
    for i, (num_of_competitors, number_of_insurances) in enumerate(VARIABLES_VALUES):
        result = simulate(1000, num_of_competitors, number_of_insurances)
        print("Case:", VARIABLES_VALUES[i], "\nresult:", result)
        if result < BASELINES[i]:
            print("----- Test failed. ------")
        print()
