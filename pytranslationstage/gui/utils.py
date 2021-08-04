def find_unit_prefix( x ):
    if isinstance( x, list )or isinstance( x, tuple ):
        _max = max( [ abs( val ) for val in x] )
    else:
        _max = max( abs( x ) )
    if _max < 1e-15:
        return "a", 1e-18
    elif _max < 1e-12:
        return "f", 1e-15
    elif _max < 1e-9:
        return "p", 1e-12
    elif _max < 1e-6:
        return "n", 1e-9
    elif _max < 1e-3:
        return "u", 1e-6
    elif _max < 1:
        return "m", 1e-3
    elif _max < 1e3:
        return "", 1
    elif _max < 1e6:
        return "k", 1e3
    elif _max < 1e9:
        return "M", 1e6
    elif _max < 1e12:
        return "G", 1e9
    elif _max < 1e15:
        return "T", 1e12
    elif _max < 1e18:
        return "P", 1e15
    return "E", 1e18
