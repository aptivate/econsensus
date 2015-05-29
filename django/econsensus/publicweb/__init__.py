VERSION = (0, 5, 1)

def get_version():
    return '.'.join([str(subversion) for subversion in VERSION])
