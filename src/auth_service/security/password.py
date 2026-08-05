from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Создаёт необратимый хеш пароля."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Проверяет соответствие обычного пароля сохранённому хешу.

    Args:
        password: Пароль, который пользователь ввёл при входе.
        password_hash: Хеш пароля из PostgreSQL.

    Returns:
        True, если пароль правильный, иначе False.
    """
    return password_hasher.verify(password, password_hash)