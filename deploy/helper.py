
def set_dict_if_not_set(thedict, key, value):
    if key not in thedict:
        thedict[key] = value
