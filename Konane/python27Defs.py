# Functions available in 2.7 that are trivial to implement, so they're being used
# For the 2.4 on the cluster

def any(iterable):
    for element in iterable:
        if element:
            return True
    return False

def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True
