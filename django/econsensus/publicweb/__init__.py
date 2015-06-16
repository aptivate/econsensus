VERSION = (0, 5, 4)


def get_version():
    return '.'.join([str(subversion) for subversion in VERSION])
