from telegram import Update
from telegram.ext import ContextTypes

async def send_processing_message(update: Update, message: str, parse_mode: str = None) -> dict:
    """
    Отправляет временное сообщение о процессе обработки.
    
    Args:
        update: Объект Update из Telegram
        message: Текст сообщения
        parse_mode: Формат текста (например, 'MarkdownV2')
    
    Returns:
        dict: Ответ Telegram API с информацией о сообщении
    """
    chat_id = update.effective_chat.id
    return await update.effective_chat.send_message(
        text=message,
        parse_mode=parse_mode
    )

async def replace_processing_message(context: ContextTypes.DEFAULT_TYPE, processing_message: dict, new_text: str, parse_mode: str = None) -> None:
    """
    Заменяет временное сообщение новым текстом или отправляет новое, если редактирование невозможно.
    
    Args:
        context: Контекст Telegram
        processing_message: Ответ Telegram API с информацией о временном сообщении
        new_text: Новый текст для замены
        parse_mode: Формат текста (например, 'MarkdownV2')
    """
    chat_id = processing_message["chat"]["id"]
    message_id = processing_message["message_id"]
    
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=new_text,
            parse_mode=parse_mode
        )
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id,
            text=new_text,
            parse_mode=parse_mode
        )