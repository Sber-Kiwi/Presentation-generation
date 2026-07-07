import os
import pickle
import functools
from pathlib import Path

CACHE_DIR = Path(".dev_cache")
CACHE_DIR.mkdir(exist_ok=True)

DEV_CACHE = os.environ.get("DEV_CACHE") == "1"


def dev_cache(name: str):
    """Кэширует результат async-функции на диск для ускорения разработки.

    Активируется только при DEV_CACHE=1 в переменных окружения.
    При повторном запуске с тем же именем стадии результат берётся из файла,
    минуя реальный вызов функции (и, соответственно, LLM).
    """

    def decorator(func):
        cache_path = CACHE_DIR / f"{name}.pkl"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if DEV_CACHE and cache_path.exists():
                print(f"[dev cache] using cached '{name}' output")
                with open(cache_path, "rb") as f:
                    return pickle.load(f)

            result = await func(*args, **kwargs)

            if DEV_CACHE:
                with open(cache_path, "wb") as f:
                    pickle.dump(result, f)

            return result

        return wrapper

    return decorator
