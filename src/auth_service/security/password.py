from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Создаёт необратимый хеш пароля."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет, соответствует ли пароль сохранённому хешу."""

    return password_hasher.verify(password, password_hash)