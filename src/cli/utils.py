import asyncio
from functools import wraps
from typing import Optional



def run_async(func):
    """Executa comandos assíncronos corretamente dentro do Typer."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(func(*args, **kwargs))
        else:
            return asyncio.run(func(*args, **kwargs))
    return wrapper


def strip_or_none(value: str) -> Optional[str]:
    return value.strip() if value else None
