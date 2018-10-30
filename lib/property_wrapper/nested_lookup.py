"""
Use lists of keys and indices to access certain properties in
subscriptable structures.

Example:
data = {'dk0': ['li0', ('ti0', 'ti1')], 'dk1': 'dv1'}
v = nget(data, ['dk0', 1, 0])
v is now 'ti0'.
"""

from pprint import pformat


def _nget(data: any, path: list) -> tuple:
    """
    Get the furthest value along a given key path in a subscriptable
    structure.

    :param data: the subscriptable structure to examine
    :param path: the lookup path to follow
    :return: tuple of value at furthest valid key, furthest valid
    path
    """

    idx = 0
    for key in path:
        try:
            data = data[key]
            idx += 1
        except LookupError:
            break
    return data, path[:idx]


def path_valid(data: any, path: list) -> bool:
    """
    Determine whether it's possible to follow the key path in a
    subscriptable structure.

    :param data: the subscriptable structure to examine
    :param path: the lookup path to verify
    :return: whether the lookup path exists within data
    """

    return len(path) == len(_nget(data, path)[1])


def nget(data: any, path: list) -> any:
    """
    Get the value at the end of the key path in a subscriptable
    structure.

    :param data: the subscriptable structure to examine
    :param path: the lookup path to follow
    :return: the value at the end of the key path
    """

    val, valid_path = _nget(data, path)
    if len(path) == len(valid_path):
        return val
    else:
        raise LookupError('Failed to find key \'{}\' at path {} in the '
                          'following data:\n{}.'.format(path[len(valid_path)],
                                                        valid_path,
                                                        pformat(data)))


def nset(data: any, path: list, val: any) -> None:
    """
    Set the value at the end of the key path in a subscriptable
    structure.

    :param data: the subscriptable structure to examine
    :param path: the lookup path to follow
    :param val: the new value to assign
    """

    try:
        nget(data, path[:-1])[path[-1]] = val
    except TypeError as e:
        raise TypeError('Cannot set value at path {} in the following '
                        'data:\n{}.'.format(path, pformat(data))) from e


def ndel(data: any, path: list) -> None:
    """
    Delete the value at the end of the key path from the subscriptable
    structure containing it.
    
    :param data: the subscriptable structure to examine
    :param path: the lookup path to follow
    """

    try:
        del(nget(data, path[:-1])[path[-1]])
    except TypeError as e:
        raise TypeError('Cannot delete value at path {} in the following '
                        'data:\n{}.'.format(path, pformat(data))) from e
