from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.database import add_subscription, remove_subscription
from utils.zodiac import ZODIAC_SIGNS
from keyboards.main_menu import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            escape_markdown(f"⚠️ Укажите знак зодиака: {', '.join(ZODIAC_SIGNS)}", version=2),
            parse_mode="MarkdownV2"
        )
        return

    zodiac = context.args[0].lower()
    if zodiac not in [sign.lower() for sign in ZODIAC_SIGNS]:
        await update.message.reply_text(
            escape_markdown(f"⚠️ Неверный знак зодиака. Выберите из: {', '.join(ZODIAC_SIGNS)}", version=2),
            parse_mode="MarkdownV2"
        )
        return

    try:
        await add_subscription(update.effective_chat.id, zodiac)
        await update.message.reply_text(
            escape_markdown(f"✅ Вы подписаны на ежедневные гороскопы для {zodiac}!", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка подписки: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при подписке. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    try:
        await remove_subscription(update.effective_chat.id)
        await update.message.reply_text(
            escape_markdown("✅ Вы отписаны от ежедневных гороскопов!", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка отписки: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при отписке. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )