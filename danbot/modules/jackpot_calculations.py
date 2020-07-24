def calc_expected_coin_volume(m, p):
    """
    :param m: number of messages sent
    :param p: 1 - probability of jackpot each message
    :return: expected coin volume after m messages have been sent
    """
    return m - (p * (p**m - 1)) / (p - 1)


def calc_expected_coins(total_msg, user_msg, p):
    """
    :param total_msg: total messages sent since jackpot enabled
    :param user_msg: messages sent by used since jackpot enabled
    :param p: 1 - probability of jackpot each message
    :return: expected number of coins that the user should have
    """
    total_coins = calc_expected_coin_volume(total_msg, p)
    msg_ratio = user_msg / total_msg
    expected_coins = total_coins * msg_ratio

    return expected_coins
