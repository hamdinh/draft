from typing import Any

def delete_key_nested(obj: Any, key: str) -> None:
    """Delete all occurrences of `key` from a nested dict/list structure in place.

    Mutates the input structure; does minimum necessary recursion and checks.
    """
    if isinstance(obj, dict):
        if key in obj:
            del obj[key]
        for v in obj.values():
            if v is not None:
                delete_key_nested(v, key)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if item is not None:
                delete_key_nested(item, key)
