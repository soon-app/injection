from uuid import uuid4


def new_short_key() -> str:
    return uuid4().hex[:7]
