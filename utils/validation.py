import re

def validate_date(date_str: str) -> bool:
    """Проверяет, соответствует ли строка формату ДД.ММ.ГГГГ."""
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", date_str))

def validate_time(time_str: str) -> bool:
    """Проверяет, соответствует ли строка формату ЧЧ:ММ."""
    return bool(re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", time_str))

def validate_place(place: str) -> bool:
    """Проверяет, содержит ли строка только буквы, пробелы и дефисы."""
    return bool(re.match(r'^[a-zA-Zа-яА-Я\s-]+$', place))