import jwt
import datetime


# Функція для перевірки валідності токену
def is_token_valid(token: str, secret_key: str):
    try:
        # Розкодувати токен
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Отримати дату і час закінчення терміну дії токену
        expiration_time = datetime.datetime.fromtimestamp(payload["exp"])

        # Перевірити, чи токен ще не сплив
        if expiration_time > datetime.datetime.now():
            return True
        else:
            return False
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
