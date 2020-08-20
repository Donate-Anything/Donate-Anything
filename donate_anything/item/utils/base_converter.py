from string import ascii_letters, digits
from typing import Tuple


order = digits + ascii_letters + "_-"
base = 64


def item_encode_b64(num_id: int, condition: int = 3) -> str:
    """Encodes a base 10 number to base 64
    The purpose is to encode the BigInt ID
    with the item's condition (0-3).

    Implementation is here due to Javascript
    losing precision (only goes up to 15 digits.

    Assert that num_id is greater than 0.
    The condition is added by appending the number.

    :param num_id: the wanted item's integer ID
    :param condition: condition choice in integer form
    :return: base 64 encoded string of ID and condition
    """
    assert num_id > 0
    num = int(str(num_id) + str(condition))
    string = ""
    while num:
        r = num % base
        num -= r
        num /= base
        string = order[int(r)] + string
    assert string not in digits
    return string


def b64_to_wanted_item(string: str) -> Tuple[int, int]:
    """Converts base64 string to base 10.

    :param string: url query parameter string in base 64
    :return: WantedItem's id and condition as a tuple
    """
    assert len(string) > 0
    num = 0
    while len(string):
        r = order.index(string[0])
        string = string[1:]
        num *= base
        num += r
    return int(str(num)[:-1]), int(str(num)[-1])
