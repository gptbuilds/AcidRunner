def in_files(filenames):
    if not isinstance(filenames, list):
        raise ValueError(f"Expected a list of filenames, got {type(filenames).__name__}")

    def decorator(func):
        func._filenames = filenames 
        return func
    return decorator
