from functools import wraps
from flask_caching import Cache
from app.extensions import cache

def cache_with_args(timeout=300):
    """
    Декоратор для кэширования результатов функций с аргументами.
    Использует аргументы функции как часть ключа кэша.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Создаем ключ кэша из имени функции и аргументов
            cache_key = f.__name__ + str(args) + str(kwargs)
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def cache_with_key(key_prefix, timeout=300):
    """
    Декоратор для кэширования результатов функций с фиксированным префиксом ключа.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Создаем ключ кэша из префикса и аргументов
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def clear_cache_by_prefix(prefix):
    """
    Очищает все ключи кэша с указанным префиксом.
    """
    keys = cache.get_many(prefix + '*')
    if keys:
        cache.delete_many(keys.keys()) 