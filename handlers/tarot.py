from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from keyboards.main_menu import main_menu_keyboard
from utils.telegram_helpers import send_photo_with_caption
import logging

logger = logging.getLogger(__name__)

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    try:
        card, interpretation = await get_tarot_interpretation()
        full_text = f"🎴 Вытянутая карта: {card}\n\n{interpretation}"
        full_text = full_text[:4000]

        image_url = generate_tarot_image(card)
        if image_url:
            await update.message.reply_photo(
                photo=image_url,
                caption=escape_markdown(full_text, version=2),
                parse_mode="MarkdownV2",
                reply_markup=main_menu_keyboard
            )
        else:
            await update.message.reply_text(
                escape_markdown(full_text, version=2),
                parse_mode="MarkdownV2",
                reply_markup=main_menu_keyboard
            )
    except Exception as e:
        logger.error(f"Ошибка вытягивания карты Таро: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при вытягивании карты. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )