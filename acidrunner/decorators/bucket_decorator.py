def use_bucket(bucket_name):
    def decorator(func):
        func._bucket = bucket_name  # Attach the bucket name to the function
        return func
    return decorator
