from math import sqrt

def calc_expected_coins(n, p):
    """
    :param n: number of messages sent
    :param p: probability of jackpot each message
    :return: expected coins after m messages have been sent
    """
    q = 1 - p
    return n - (1 * (1**n - 1)) / (q - 1)

def calc_standard_deviation(n, p):
    """
    :param m: number of messages sent
    :param p: probability of jackpot each message
    :return: standard deviation after m messages have been sent
    """
    q = 1 - p
    return sqrt((2 * n * (q - 1) * q ** (n + 1) - q * (q**n - 1) * (q ** (n + 1) + 1))) / (1 - q)
