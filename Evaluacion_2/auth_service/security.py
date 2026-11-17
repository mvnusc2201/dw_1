from argon2 import PasswordHasher
from argon2.low_level import Type
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)


_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:

    try:
        return _password_hasher.verify(
            stored_hash,
            password,
        )
    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False