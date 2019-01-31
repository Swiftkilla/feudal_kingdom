from itertools import chain, combinations


weights = [3, 1, 2, 3, 2, 1]
w = 6

# weights = (3, 1, 2, 3, 2, 1) / w = 6 / Output: 4
# weights = [1, 1, 1] / w = 2 / Output: 2
# weights = (1, 1, 1) / w = 7 / Output: 3
# weights = [4,2,1,3] / w = 5 / Output: 2
# weights = [5] / w =5 / Output: 1


def powerset(iterable):
    """
    :param iterable: the iterable you want to find all combinations for
    :return: each combination of the iterables in this example:
    :example:
    weights = (3, 1, 2, 3, 2, 1)
    w = len(weights)
    powersets = []
    for x in powerset(weights):
        if sum(x) == w:
            print(x)
            powersets.append(len(x))
    Output >>>
    (3, 3)
    (3, 1, 2)
    (3, 1, 2)
    (3, 2, 1)
    (3, 2, 1)
    (1, 2, 3)
    (1, 3, 2)
    (2, 3, 1)
    (3, 2, 1)
    (1, 2, 2, 1)
    4
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


powersets = [len(x) for x in powerset(weights) if sum(x) <= w]

# for x in powerset(weights):
#     if sum(x) <= w:
#         print(x)
#         powersets.append(len(x))

print(max(powersets))

