reload_functions = []

def reload_all():
    global reload_functions
    for f in reload_functions:
        f()