from functools import wraps
import asyncio

def sync_async_method(async_func):
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        coro = async_func(*args, **kwargs)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return coro
            else:
                return asyncio.run(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    return wrapper