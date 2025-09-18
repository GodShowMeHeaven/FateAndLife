import re
import html
import logging

logger = logging.getLogger(__name__)

def validate_date(date_str: str) -> bool:
    """Проверяет, соответствует ли строка формату ДД.ММ.ГГГГ."""
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", date_str))

def validate_time(time_str: str) -> bool:
    """Проверяет, соответствует ли строка формату ЧЧ:ММ."""
    return bool(re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", time_str))

def validate_place(place: str) -> bool:
    """Проверяет, содержит ли строка только буквы, пробелы и дефисы."""
    return bool(re.match(r'^[a-zA-Zа-яА-Я\s-]+$', place))

def validate_user_input(text: str, max_length: int = 1000) -> bool:
    """
    Проверяет пользовательский ввод на безопасность и корректность.
    
    Args:
        text: Входной текст для проверки
        max_length: Максимальная длина текста
        
    Returns:
        bool: True если ввод безопасен, False иначе
    """
    if not isinstance(text, str):
        return False
        
    if not text.strip() or len(text) > max_length:
        return False
    
    dangerous_patterns = [
        '<script>', 'javascript:', 'sql', 'drop table', 'insert into',
        'delete from', 'update set', 'exec', 'eval(', 'onclick=',
        'onload=', 'onerror=', '<iframe', '<object', '<embed',
        'vbscript:', 'data:text/html'
    ]
    
    text_lower = text.lower()
    return not any(pattern in text_lower for pattern in dangerous_patterns)

def sanitize_input(text: str) -> str:
    """
    Очищает пользовательский ввод и экранирует специальные символы для Telegram MarkdownV2.
    
    Args:
        text: Входной текст для очистки
        
    Returns:
        str: Очищенный и экранированный текст
    """
    if not isinstance(text, str):
        logger.warning("sanitize_input получил не строку, возвращаем пустую строку")
        return ""
    
    # HTML escape для предотвращения XSS
    text = html.escape(text)
    
    # Экранирование специальных символов для MarkdownV2
    markdown_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')
    
    # Сохраняем переносы строк, заменяя их на временный маркер
    text = text.replace('\n', '__NEWLINE__')
    
    # Удаление лишних пробелов, но не переносов строк
    text = re.sub(r'[ \t]+', ' ', text).strip()
    
    # Удаление управляющих символов
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Восстанавливаем переносы строк
    text = text.replace('__NEWLINE__', '\n')
    
    logger.debug(f"Экранированный текст: {text[:200]}...")
    return text

def validate_name(name: str) -> bool:
    """
    Проверяет корректность имени пользователя.
    
    Args:
        name: Имя для проверки
        
    Returns:
        bool: True если имя корректно, False иначе
    """
    if not isinstance(name, str) or not name.strip():
        return False
        
    if len(name.strip()) > 50:
        return False
        
    return bool(re.match(r'^[a-zA-Zа-яА-Я\s-]+$', name.strip()))

def validate_zodiac_sign(sign: str) -> bool:
    """
    Проверяет корректность знака зодиака.
    
    Args:
        sign: Знак зодиака для проверки
        
    Returns:
        bool: True если знак корректен, False иначе
    """
    valid_signs = [
        'овен', 'телец', 'близнецы', 'рак', 'лев', 'дева',
        'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыбы'
    ]
    
    if not isinstance(sign, str):
        return False
        
    return sign.lower().strip() in valid_signs

def validate_callback_data(data: str) -> bool:
    """
    Проверяет корректность callback data.
    
    Args:
        data: Callback data для проверки
        
    Returns:
        bool: True если data корректна, False иначе
    """
    if not isinstance(data, str) or not data:
        return False
        
    if len(data.encode('utf-8')) > 64:
        return False
        
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', data))

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Обрезает текст до указанной длины с добавлением суффикса.
    
    Args:
        text: Текст для обрезки
        max_length: Максимальная длина
        suffix: Суффикс для добавления при обрезке
        
    Returns:
        str: Обрезанный текст
    """
    if not isinstance(text, str):
        return ""
        
    if len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix

def validate_phone(phone: str) -> bool:
    """
    Проверяет корректность номера телефона.
    
    Args:
        phone: Номер телефона для проверки
        
    Returns:
        bool: True если номер корректен, False иначе
    """
    if not isinstance(phone, str):
        return False
        
    clean_phone = re.sub(r'[^\d+]', '', phone)
    return bool(re.match(r'^(\+?\d{10,15})$', clean_phone))

def validate_email(email: str) -> bool:
    """
    Проверяет корректность email адреса.
    
    Args:
        email: Email для проверки
        
    Returns:
        bool: True если email корректен, False иначе
    """
    if not isinstance(email, str) or len(email) > 254:
        return False
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_safe_length(text: str, max_bytes: int = 4096) -> int:
    """
    Возвращает безопасную длину текста в символах для заданного лимита байт.
    
    Args:
        text: Текст для проверки
        max_bytes: Максимальное количество байт
        
    Returns:
        int: Максимальная безопасная длина в символах
    """
    if not isinstance(text, str):
        return 0
        
    for i, char in enumerate(text):
        if len(text[:i+1].encode('utf-8')) > max_bytes:
            return i
            
    return len(text)